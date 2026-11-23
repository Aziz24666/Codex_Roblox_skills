#!/usr/bin/env python3
"""Offline Roblox analytics governance, instrumentation audit, and game-health checks."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "31.0.0"
MAX_FILES = 10_000
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_FINDINGS = 500
SKIP_DIRS = {
    ".git", ".agents", ".codex", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules",
    "target", "build", "dist", ".idea", ".vscode",
}
CUSTOM_EVENT_LIMIT = 100
CUSTOM_FIELD_LIMIT = 3
CUSTOM_FIELD_COMBINATION_LIMIT = 8_000
ANALYTICS_CUSTOM_FIELD_SLOTS = {"CustomField01", "CustomField02", "CustomField03"}
CUSTOM_FIELD_VALUES_PER_FIELD_LIMIT = 256
CUSTOM_EVENT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
FIELD_NAME = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
METRIC_NAME = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
ENVIRONMENTS = {"development", "staging", "production"}
FORBIDDEN_FIELD_NAMES = {
    "user_id", "userid", "player_id", "playerid", "roblox_user_id",
    "username", "user_name", "player_name", "display_name", "email",
    "phone", "phone_number", "ip", "ip_address", "device_id", "deviceid",
    "session_id", "sessionid", "guid", "uuid", "cookie", "token",
    "chat", "chat_text", "message", "message_text", "raw_text",
    "account_age", "payer_id",
}
DEPRECATED_METHODS = {
    "FireCustomEvent", "FireEvent", "FireInGameEconomyEvent",
    "FireLogEvent", "FirePlayerProgressionEvent",
}
SUPPORTED_METHODS = {
    "LogCustomEvent", "LogEconomyEvent", "LogFunnelStepEvent", "LogJourneyEvent",
    "LogOnboardingFunnelStepEvent", "LogProgressionEvent",
    "LogProgressionCompleteEvent", "LogProgressionFailEvent",
    "LogProgressionStartEvent",
}
CLIENT_PATH_PARTS = {
    "starterplayerscripts", "startercharacterscripts", "playerscripts",
}
DEFAULT_CATALOG = ".codex/analytics/event-catalog.json"
DEFAULT_AUDIT = ".codex/reports/v31-analytics-audit.json"
DEFAULT_POLICY = ".codex/analytics/health-policy.json"
DEFAULT_SNAPSHOT = ".codex/analytics/health-snapshot.json"
DEFAULT_HEALTH_REPORT = ".codex/reports/v31-game-health.json"


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_project_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw.strip() or "\x00" in raw:
        raise ValueError("Project-relative path must be a non-empty string.")
    if "\\" in raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise ValueError("Path must be project-relative and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Path must stay inside the selected project root.")
    candidate = root.joinpath(*parts)
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Path cannot traverse a symlink.")
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Path resolves outside the selected project root or does not exist.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Path must identify an existing regular file.")
    return resolved


def safe_output_path(root: Path, raw: str) -> Path:
    target = safe_project_path(root, raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve(strict=True)
    if not parent.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent / target.name


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_json(root: Path, raw: str) -> tuple[Path, Any]:
    path = safe_project_path(root, raw, must_exist=True)
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError(f"{path.relative_to(root)} exceeds the {MAX_JSON_BYTES}-byte JSON input limit.")
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path, value


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def finite_nonnegative(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0
    )


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _sensitive_value(value: str) -> bool:
    if len(value) > 48 or any(ord(ch) < 32 for ch in value):
        return True
    if re.search(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", value):
        return True
    if re.fullmatch(r"(?i)[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}", value):
        return True
    if re.fullmatch(r"\d{7,}", value):
        return True
    return False


def validate_catalog(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Event catalog must be a JSON object."]
    if set(data) - {"schema_version", "events", "telemetry_budget"}:
        errors.append("Event catalog contains unsupported top-level fields; keep the catalog metadata-only.")
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")
    events = data.get("events")
    if not isinstance(events, list):
        return errors + ["events must be an array."]
    if len(events) > CUSTOM_EVENT_LIMIT:
        errors.append(f"Custom event catalog exceeds Roblox's {CUSTOM_EVENT_LIMIT}-event experience limit.")

    names: set[str] = set()
    declared_combination_upper_bound = 0
    for index, event in enumerate(events):
        label = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{label} must be an object.")
            continue
        if set(event) - {"name", "method", "purpose", "privacy_reviewed", "fields"}:
            errors.append(f"{label} contains unsupported fields; keep event definitions minimal.")
        name = event.get("name")
        if not isinstance(name, str) or not CUSTOM_EVENT_NAME.fullmatch(name):
            errors.append(f"{label}.name must be 1-64 ASCII letters, digits, or underscores and start with a letter.")
        elif name in names:
            errors.append(f"Duplicate custom event name: {name}.")
        else:
            names.add(name)
        if event.get("method") != "LogCustomEvent":
            errors.append(f"{label}.method must be LogCustomEvent for a custom-event catalog entry.")
        purpose = event.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip() or len(purpose) > 240:
            errors.append(f"{label}.purpose must be a non-empty description of at most 240 characters.")
        if event.get("privacy_reviewed") is not True:
            errors.append(f"{label}.privacy_reviewed must be true before the event is approved.")

        if "fields" not in event:
            errors.append(f"{label}.fields must be declared, even when empty.")
        fields = event.get("fields", [])
        if not isinstance(fields, list):
            errors.append(f"{label}.fields must be an array.")
            continue
        if len(fields) > CUSTOM_FIELD_LIMIT:
            errors.append(f"{label} exceeds Roblox's {CUSTOM_FIELD_LIMIT}-custom-field limit.")
        field_names: set[str] = set()
        field_slots: set[str] = set()
        field_value_counts: list[int] = []
        for field_index, field in enumerate(fields):
            field_label = f"{label}.fields[{field_index}]"
            if not isinstance(field, dict):
                errors.append(f"{field_label} must be an object.")
                continue
            field_name = field.get("name")
            if not isinstance(field_name, str) or not FIELD_NAME.fullmatch(field_name):
                errors.append(f"{field_label}.name must be a lower_snake_case semantic field name.")
            elif field_name in field_names:
                errors.append(f"{label} has duplicate custom field name {field_name}.")
            else:
                field_names.add(field_name)
                if field_name in FORBIDDEN_FIELD_NAMES:
                    errors.append(f"{field_label}.name is not allowed: identifiers and personal data are prohibited.")

            slot = field.get("slot")
            slot_is_unique = isinstance(slot, str) and slot in ANALYTICS_CUSTOM_FIELD_SLOTS and slot not in field_slots
            if not isinstance(slot, str) or slot not in ANALYTICS_CUSTOM_FIELD_SLOTS:
                errors.append(
                    f"{field_label}.slot must be CustomField01, CustomField02, or CustomField03 "
                    "and maps to Enum.AnalyticsCustomFieldKeys.<slot>.Name."
                )
            elif slot in field_slots:
                errors.append(f"{label} maps more than one semantic field to {slot}; each AnalyticsService slot may be used once per event.")
            else:
                field_slots.add(slot)

            if set(field) - {"name", "slot", "allowed_values"}:
                errors.append(f"{field_label} contains unsupported fields.")
            values = field.get("allowed_values")
            if not isinstance(values, list) or not values:
                errors.append(f"{field_label}.allowed_values must be a non-empty finite list.")
                continue
            values_are_valid = True
            if len(values) > CUSTOM_FIELD_VALUES_PER_FIELD_LIMIT:
                errors.append(f"{field_label}.allowed_values exceeds the {CUSTOM_FIELD_VALUES_PER_FIELD_LIMIT}-value local review limit.")
                values_are_valid = False
            seen_values: set[str] = set()
            for value in values:
                if not isinstance(value, str) or not value.strip() or _sensitive_value(value):
                    errors.append(f"{field_label}.allowed_values must contain short, non-identifying strings only.")
                    values_are_valid = False
                    continue
                if value in seen_values:
                    errors.append(f"{field_label}.allowed_values contains a duplicate value.")
                    values_are_valid = False
                seen_values.add(value)
            if slot_is_unique and values_are_valid and seen_values:
                field_value_counts.append(len(seen_values))

        # Each event's Cartesian product is a conservative upper bound for its
        # possible field tuples. Sum the event bounds so duplicate tuples across
        # events cannot make this local preflight less strict than Roblox's cap.
        if fields and len(field_value_counts) == len(fields):
            declared_combination_upper_bound += math.prod(field_value_counts)

    if declared_combination_upper_bound > CUSTOM_FIELD_COMBINATION_LIMIT:
        errors.append(
            f"Catalog permits an upper bound of {declared_combination_upper_bound:,} custom-field combinations "
            f"(sum of per-event Cartesian products), exceeding Roblox's {CUSTOM_FIELD_COMBINATION_LIMIT:,}-combination limit."
        )
    telemetry_budget = data.get("telemetry_budget")
    if telemetry_budget is not None:
        if not isinstance(telemetry_budget, dict):
            errors.append("telemetry_budget must be an object.")
        else:
            calls = telemetry_budget.get("expected_calls_per_minute")
            ccu = telemetry_budget.get("maximum_concurrent_users")
            if not positive_integer(calls) or not isinstance(ccu, int) or isinstance(ccu, bool) or ccu < 0:
                errors.append("telemetry_budget requires positive expected_calls_per_minute and non-negative maximum_concurrent_users integers.")
            elif calls > 120 + 20 * ccu:
                errors.append(
                    f"Declared AnalyticsService call budget ({calls}/min) exceeds the documented "
                    f"global limit estimate of 120 + 20 × CCU ({120 + 20 * ccu}/min)."
                )
    return errors


def iter_luau_files(root: Path, max_files: int, warnings: list[str]) -> list[Path]:
    result: list[Path] = []
    total_bytes = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept: list[str] = []
        for name in sorted(dirnames):
            child = current / name
            if name in SKIP_DIRS:
                continue
            if child.is_symlink() or not child.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root directory: {child.relative_to(root)}")
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = current / name
            if path.suffix.lower() not in {".lua", ".luau"}:
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root source: {path.relative_to(root)}")
                continue
            try:
                size = path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat source file: {path.relative_to(root)}")
                continue
            if size > MAX_FILE_BYTES:
                warnings.append(f"Skipped oversized source file ({size} bytes): {path.relative_to(root)}")
                continue
            if total_bytes + size > MAX_TOTAL_BYTES:
                warnings.append("Stopped at the 128 MiB aggregate Luau scan limit.")
                return result
            result.append(path)
            total_bytes += size
            if len(result) >= max_files:
                warnings.append(f"Stopped at the configured {max_files}-file scan limit.")
                return result
    return result


def is_client_context(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    name = path.name.lower()
    parts = {part.lower() for part in relative.parts}
    return (
        name.endswith((".client.lua", ".client.luau"))
        or any(part in CLIENT_PATH_PARTS for part in parts)
    )


def audit_project(root: Path, catalog: Any = None, max_files: int = MAX_FILES) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    warnings: list[str] = []
    files = iter_luau_files(root, max(1, min(max_files, MAX_FILES)), warnings)
    catalog_errors = validate_catalog(catalog) if catalog is not None else []
    approved_events = {
        event.get("name")
        for event in catalog.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("name"), str)
    } if isinstance(catalog, dict) and not catalog_errors else set()
    inventory_methods: dict[str, int] = {method: 0 for method in sorted(SUPPORTED_METHODS | DEPRECATED_METHODS)}
    readable_files = 0
    custom_calls = 0

    deprecated_pattern = re.compile(
        r"AnalyticsService\s*:\s*(" + "|".join(sorted(DEPRECATED_METHODS)) + r")\b"
    )
    method_pattern = re.compile(
        r"AnalyticsService\s*:\s*(" + "|".join(sorted(SUPPORTED_METHODS)) + r")\b"
    )
    call_pattern = re.compile(
        r"AnalyticsService\s*:\s*LogCustomEvent\s*\(\s*[^,]+,\s*([^,\r\n)]+)",
        re.S,
    )
    literal_pattern = re.compile(r"""^\s*(['"])([^'"]+)\1\s*$""")
    private_property_pattern = re.compile(
        r"(?i)\.\s*(?:UserId|DisplayName|Name|Email|PhoneNumber|AccountAge|IPAddress|DeviceId)\b"
        r"|\b(?:email|phone_number|ip_address|raw_chat|chat_message)\b"
    )

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            warnings.append(f"Skipped unreadable Luau source: {relative}")
            continue
        readable_files += 1
        client = is_client_context(path, root)

        for match in deprecated_pattern.finditer(source):
            method = match.group(1)
            inventory_methods[method] += 1
            findings.append({
                "severity": "high", "code": "deprecated_analytics_api",
                "file": relative, "line": source.count("\n", 0, match.start()) + 1,
                "method": method,
                "message": "Deprecated AnalyticsService method detected; review the current Creator Hub API and migrate deliberately.",
            })

        for match in method_pattern.finditer(source):
            inventory_methods[match.group(1)] += 1
        for match in call_pattern.finditer(source):
            custom_calls += 1
            argument = match.group(1).strip()
            literal = literal_pattern.fullmatch(argument)
            line = source.count("\n", 0, match.start()) + 1
            if client:
                findings.append({
                    "severity": "high", "code": "analytics_api_in_client_context",
                    "file": relative, "line": line, "method": "LogCustomEvent",
                    "message": "AnalyticsService custom-event calls are documented for server-side use; verify the call is moved to an authoritative server script.",
                })
            if literal:
                event_name = literal.group(2)
                if catalog is not None and not catalog_errors and event_name not in approved_events:
                    findings.append({
                        "severity": "medium", "code": "event_missing_from_catalog",
                        "file": relative, "line": line, "event_name": event_name,
                        "message": "Static custom event name is not present in the supplied approved event catalog.",
                    })
                tail = source[match.end(1): min(len(source), match.end(1) + 1200)]
                if private_property_pattern.search(tail):
                    findings.append({
                        "severity": "high", "code": "possible_personal_data_in_event_arguments",
                        "file": relative, "line": line, "event_name": event_name,
                        "message": "A potentially identifying or free-text property appears near a custom-event call; inspect the customFields argument without copying player data into reports.",
                    })
            else:
                findings.append({
                    "severity": "low", "code": "dynamic_event_name_requires_review",
                    "file": relative, "line": line, "method": "LogCustomEvent",
                    "message": "Event name is not a simple string literal; confirm it comes from the approved finite catalog.",
                })

        if len(findings) >= MAX_FINDINGS:
            warnings.append(f"Stopped recording at the {MAX_FINDINGS}-finding report limit.")
            break

    counts = {level: sum(1 for item in findings if item["severity"] == level) for level in ("high", "medium", "low")}
    return {
        "report_type": "v31_analytics_instrumentation_audit",
        "schema_version": 1,
        "version": VERSION,
        "project_root_name": root.name,
        "inventory": {
            "luau_files_discovered": len(files),
            "files_read": readable_files,
            "analytics_method_calls": {key: value for key, value in inventory_methods.items() if value},
            "custom_event_calls": custom_calls,
        },
        "catalog_status": "not_supplied" if catalog is None else ("invalid" if catalog_errors else "valid"),
        "catalog_errors": catalog_errors,
        "finding_counts": counts,
        "findings": findings[:MAX_FINDINGS],
        "warnings": warnings,
        "execution_status": "static_local_audit_only",
        "limitations": [
            "This is a bounded text-pattern review, not a Luau parser or proof that every analytics call was found.",
            "Client context is inferred from file names and common client-only folders; shared modules require manual review.",
            "A static finding may be a false positive. Confirm call context and arguments in Studio before changing code.",
            "No Roblox service is contacted, no player data is collected, and no source file is modified.",
        ],
    }


def validate_health_policy(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Health policy must be a JSON object."]
    if set(data) - {"schema_version", "minimum_sample_size", "maximum_age_hours", "metrics"}:
        errors.append("Health policy contains unsupported top-level fields.")
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")
    minimum = data.get("minimum_sample_size")
    if not positive_integer(minimum):
        errors.append("minimum_sample_size must be a positive integer.")
    maximum_age = data.get("maximum_age_hours")
    if not finite_nonnegative(maximum_age) or maximum_age <= 0 or maximum_age > 8760:
        errors.append("maximum_age_hours must be greater than 0 and at most 8760.")
    metrics = data.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        errors.append("metrics must be a non-empty object.")
        return errors
    if len(metrics) > 100:
        errors.append("Health policy may define at most 100 aggregate metrics.")
    for name, rule in metrics.items():
        label = f"metrics.{name}"
        if not isinstance(name, str) or not METRIC_NAME.fullmatch(name):
            errors.append(f"{label} must use a lower_snake_case metric identifier.")
            continue
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object.")
            continue
        direction = rule.get("direction")
        threshold = rule.get("threshold")
        warning = rule.get("warning_threshold")
        if direction not in {"min", "max"}:
            errors.append(f"{label}.direction must be min or max.")
        if not finite_nonnegative(threshold):
            errors.append(f"{label}.threshold must be a finite non-negative number.")
        if not finite_nonnegative(warning):
            errors.append(f"{label}.warning_threshold must be a finite non-negative number.")
        if direction == "max" and finite_nonnegative(threshold) and finite_nonnegative(warning) and warning > threshold:
            errors.append(f"{label}.warning_threshold must be less than or equal to threshold for max rules.")
        if direction == "min" and finite_nonnegative(threshold) and finite_nonnegative(warning) and warning < threshold:
            errors.append(f"{label}.warning_threshold must be greater than or equal to threshold for min rules.")
        description = rule.get("description", "")
        if not isinstance(description, str) or len(description) > 200:
            errors.append(f"{label}.description must be a string of at most 200 characters.")
    return errors


def evaluate_health(policy: Any, snapshot: Any, *, now: datetime | None = None) -> dict[str, Any]:
    errors = validate_health_policy(policy)
    if errors:
        raise ValueError("Invalid health policy: " + " ".join(errors))
    if not isinstance(snapshot, dict):
        raise ValueError("Health snapshot must be a JSON object.")
    allowed_snapshot_fields = {"schema_version", "environment", "captured_at", "source", "sample_size", "metrics"}
    if set(snapshot) - allowed_snapshot_fields:
        raise ValueError("Health snapshot contains unsupported fields; only aggregate metadata and numeric metrics are accepted.")
    if snapshot.get("schema_version") != 1:
        raise ValueError("Health snapshot schema_version must equal 1.")
    environment = snapshot.get("environment")
    if not isinstance(environment, str) or environment not in ENVIRONMENTS:
        raise ValueError("Health snapshot environment must be development, staging, or production.")
    captured_at = parse_timestamp(snapshot.get("captured_at"))
    if captured_at is None:
        raise ValueError("Health snapshot captured_at must be an ISO-8601 timestamp with a timezone.")
    source = snapshot.get("source")
    if not isinstance(source, str) or not source.strip() or len(source) > 160:
        raise ValueError("Health snapshot source must be a non-empty description of at most 160 characters.")
    sample_size = snapshot.get("sample_size")
    if not positive_integer(sample_size):
        raise ValueError("Health snapshot sample_size must be a positive integer.")
    metrics = snapshot.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("Health snapshot metrics must be an object.")
    policy_metrics = policy["metrics"]
    unknown = set(metrics) - set(policy_metrics)
    if unknown:
        raise ValueError("Health snapshot contains metrics not defined in policy: " + ", ".join(sorted(unknown)))
    for name, value in metrics.items():
        if not finite_nonnegative(value):
            raise ValueError(f"Health snapshot metric {name} must be finite and non-negative.")

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Evaluation clock must be timezone-aware.")
    age_hours = (current.astimezone(timezone.utc) - captured_at).total_seconds() / 3600
    holds: list[str] = []
    if age_hours < -0.083333:
        holds.append("Snapshot timestamp is more than five minutes in the future.")
    if age_hours > float(policy["maximum_age_hours"]):
        holds.append("Snapshot is older than the policy maximum age.")
    if sample_size < policy["minimum_sample_size"]:
        holds.append("Snapshot sample_size is below the policy minimum.")
    missing = sorted(set(policy_metrics) - set(metrics))
    if missing:
        holds.append("Snapshot is missing policy metrics: " + ", ".join(missing) + ".")

    results: list[dict[str, Any]] = []
    alerts = 0
    warnings = 0
    if not holds:
        for name, rule in policy_metrics.items():
            value = float(metrics[name])
            threshold = float(rule["threshold"])
            warning_threshold = float(rule["warning_threshold"])
            direction = rule["direction"]
            if direction == "max":
                state = "alert" if value > threshold else ("warning" if value > warning_threshold else "clear")
            else:
                state = "alert" if value < threshold else ("warning" if value < warning_threshold else "clear")
            alerts += state == "alert"
            warnings += state == "warning"
            results.append({
                "metric": name, "value": value, "direction": direction,
                "threshold": threshold, "warning_threshold": warning_threshold,
                "status": state, "description": rule.get("description", ""),
            })

    status = "hold" if holds else ("alert" if alerts else ("warning" if warnings else "clear"))
    return {
        "report_type": "v31_aggregate_game_health",
        "schema_version": 1,
        "version": VERSION,
        "environment": environment,
        "captured_at": snapshot["captured_at"],
        "source": source,
        "sample_size": sample_size,
        "snapshot_age_hours": round(max(0.0, age_hours), 3),
        "status": status,
        "alert_count": alerts,
        "warning_count": warnings,
        "hold_reasons": holds,
        "metrics": results,
        "limitations": [
            "This report evaluates only the supplied aggregate snapshot; it does not collect telemetry or calculate metrics from player-level records.",
            "A clear result means only that the supplied values meet this policy. It is not proof of player wellbeing, platform compliance, or system correctness.",
            "Small, stale, incomplete, or mismatched snapshots are held rather than treated as healthy.",
            "Thresholds must be chosen for the experience and reviewed by its operators; no retention or revenue target is prescribed.",
        ],
    }


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    warnings: list[str] = []
    files = iter_luau_files(root, MAX_FILES, warnings)
    print(f"Project: {root}")
    print(f"Luau/Lua source files discovered: {len(files)}")
    print("Optional local tools:")
    for executable in ("git", "rojo", "luau-analyze"):
        print(f"  {executable}: {shutil.which(executable) or 'not found on PATH'}")
    print("No configured command is executed and no Roblox connection is attempted.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def command_validate_catalog(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    path, data = load_json(root, args.catalog)
    errors = validate_catalog(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    event_count = len(data["events"])
    field_count = sum(len(event.get("fields", [])) for event in data["events"])
    print(f"PASS: validated {event_count} custom events and {field_count} bounded custom fields.")
    print(f"Catalog: {path.relative_to(root)}")
    print("This validates the declared contract; it does not prove that runtime code follows it.")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    catalog = None
    if args.catalog:
        _, catalog = load_json(root, args.catalog)
    report = audit_project(root, catalog, args.max_files)
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    print(f"Read-only analytics audit written to: {output}")
    print(f"Files: {report['inventory']['files_read']}; calls: {report['inventory']['custom_event_calls']}; findings: {sum(report['finding_counts'].values())}")
    if report["catalog_errors"]:
        print(f"WARNING: supplied event catalog has {len(report['catalog_errors'])} validation problem(s).")
    print("Static audit only; inspect all findings manually.")
    return 0


def command_evaluate_health(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    policy_path, policy = load_json(root, args.policy)
    _, snapshot = load_json(root, args.snapshot)
    report = evaluate_health(policy, snapshot)
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    print(f"Aggregate game-health report written to: {output}")
    print(f"Status: {report['status']} | alerts: {report['alert_count']} | warnings: {report['warning_count']} | holds: {len(report['hold_reasons'])}")
    for reason in report["hold_reasons"]:
        print(f"HOLD: {reason}")
    for metric in report["metrics"]:
        if metric["status"] != "clear":
            print(f"{metric['status'].upper()}: {metric['metric']}={metric['value']}")
    print(f"Policy: {policy_path.relative_to(root)}")
    print("This evaluates supplied aggregate values only; it does not authorize a release.")
    return 1 if report["status"] in {"hold", "alert"} else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Inspect local source inventory and optional tools.")
    doctor.add_argument("--root", required=True)
    doctor.set_defaults(func=command_doctor)

    catalog = sub.add_parser("validate-catalog", help="Validate privacy and cardinality rules for a custom-event catalog.")
    catalog.add_argument("--root", required=True)
    catalog.add_argument("--catalog", default=DEFAULT_CATALOG)
    catalog.set_defaults(func=command_validate_catalog)

    audit = sub.add_parser("audit", help="Create a bounded, read-only AnalyticsService source audit.")
    audit.add_argument("--root", required=True)
    audit.add_argument("--catalog")
    audit.add_argument("--output", default=DEFAULT_AUDIT)
    audit.add_argument("--max-files", type=int, default=MAX_FILES)
    audit.set_defaults(func=command_audit)

    health = sub.add_parser("evaluate-health", help="Evaluate a supplied aggregate health snapshot against guardrails.")
    health.add_argument("--root", required=True)
    health.add_argument("--policy", default=DEFAULT_POLICY)
    health.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    health.add_argument("--output", default=DEFAULT_HEALTH_REPORT)
    health.set_defaults(func=command_evaluate_health)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
