#!/usr/bin/env python3
"""Offline validator, auditor, and compatibility checker for Roblox LiveOps contracts."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "42.0.0"
MAX_INPUT_BYTES = 1024 * 1024
MAX_CONFIG_VALUE_CHARS = 100_000
MAX_EXACT_INTEGER = 2**53
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
CONFIG_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,255}$")

TOP_FIELDS = {"schema_version", "model_id", "config_contract", "configs", "events", "deployment", "rollback", "consumers"}
CONTRACT_FIELDS = {
    "repository", "key_limit", "active_config_limit", "server_only", "runtime_write_access",
    "staged_before_publish", "draft_hash_guard", "publish_message_required",
    "snapshot_refresh_policy", "refresh_signal_handling", "fallback_on_initial_failure",
}
CONFIG_FIELDS = {
    "key", "value_type", "default_value", "category", "runtime_change_policy",
    "fallback_policy", "targeting_mode", "condition_count", "condition_order_reviewed",
    "owner", "server_only", "contains_secret",
}
EVENT_FIELDS = {
    "event_id", "title", "schedule_group", "status", "starts_at", "ends_at",
    "config_keys", "enabled_config_key", "preflight_required", "test_case_ids",
}
DEPLOYMENT_FIELDS = {
    "strategy", "staged_test_required", "pre_publish_validation_required",
    "published_readback_required", "human_approval_required", "publish_message_required",
    "publish_only_after_approval", "draft_hash_guard_required", "api_key_outside_project",
    "publish_message",
}
ROLLBACK_FIELDS = {
    "revision_history_required", "restore_creates_staged_draft", "republish_after_restore",
    "published_readback_required", "human_approval_required", "no_automatic_production_rollback",
    "rollback_test_required",
}
CONSUMER_FIELDS = {
    "consumer_id", "config_key", "expected_type", "required", "fallback_value",
    "apply_boundary", "server_only",
}
VALUE_TYPES = {"boolean", "number", "string", "json"}
CATEGORIES = {"feature_flag", "balance_tuning", "event_control", "operations"}
RUNTIME_POLICIES = {"immediate_noncompetitive_only", "next_safe_boundary", "next_session"}
FALLBACK_POLICIES = {"static_default", "keep_last_known_good", "disable_optional_feature"}
TARGETING_MODES = {"global", "conditional"}
EVENT_STATUSES = {"planned", "staged", "scheduled", "active", "completed", "cancelled"}
DEPLOYMENT_STRATEGIES = {"Immediate", "GradualRollout"}
APPLY_BOUNDARIES = {"immediate_noncompetitive_only", "next_round", "next_event_boundary", "next_session"}


def allowed(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def is_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def is_slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value))


def check_fields(value: dict, expected: set[str], label: str) -> list[str]:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    errors = []
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return errors


def value_matches_type(value: Any, value_type: str) -> bool:
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if value_type == "string":
        return isinstance(value, str)
    if value_type == "json":
        return isinstance(value, dict)
    return False


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be an ISO 8601 timestamp with an explicit UTC offset.")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be a valid ISO 8601 timestamp.")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label} must include a timezone or UTC offset; naive local times are ambiguous.")
        return None
    return parsed


def validate_model(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Model must be a JSON object."]
    errors += check_fields(data, TOP_FIELDS, "model")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        errors.append("schema_version must be integer 1.")
    if not is_slug(data.get("model_id")):
        errors.append("model_id must be a lowercase slug (2-40 characters).")

    contract = data.get("config_contract")
    if not isinstance(contract, dict):
        errors.append("config_contract must be an object.")
        contract = {}
    else:
        errors += check_fields(contract, CONTRACT_FIELDS, "config_contract")
        if contract.get("repository") != "InExperienceConfig":
            errors.append("config_contract.repository must be InExperienceConfig.")
        if not is_int(contract.get("key_limit"), 1, 100):
            errors.append("config_contract.key_limit must be an integer from 1 to 100 (Open Cloud repository limit).")
        if not is_int(contract.get("active_config_limit"), 1, 1000):
            errors.append("config_contract.active_config_limit must be an integer from 1 to 1000.")
        for name in ("server_only", "staged_before_publish", "draft_hash_guard", "publish_message_required"):
            if contract.get(name) is not True:
                errors.append(f"config_contract.{name} must be true.")
        if contract.get("runtime_write_access") is not False:
            errors.append("config_contract.runtime_write_access must be false; in-experience ConfigService is read-only.")
        if not allowed(contract.get("snapshot_refresh_policy"), {"next_safe_boundary", "immediate_noncompetitive_only"}):
            errors.append("config_contract.snapshot_refresh_policy must be next_safe_boundary or immediate_noncompetitive_only.")
        if contract.get("refresh_signal_handling") != "UpdateAvailable_then_Refresh":
            errors.append("config_contract.refresh_signal_handling must be UpdateAvailable_then_Refresh.")
        if not allowed(contract.get("fallback_on_initial_failure"), {"static_defaults", "disable_optional_features"}):
            errors.append("config_contract.fallback_on_initial_failure must be static_defaults or disable_optional_features.")

    configs = data.get("configs")
    config_map: dict[str, dict] = {}
    if not isinstance(configs, list) or not 1 <= len(configs) <= 100:
        errors.append("configs must contain 1-100 config declarations (Open Cloud InExperienceConfig repository limit).")
        configs = []
    condition_total = 0
    for index, item in enumerate(configs):
        label = f"configs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, CONFIG_FIELDS, label)
        key = item.get("key")
        if not isinstance(key, str) or not CONFIG_KEY.fullmatch(key):
            errors.append(f"{label}.key must be 1-256 characters and start with a letter; use letters, digits, underscore, dot, or hyphen.")
        elif key in config_map:
            errors.append(f"Duplicate config key: {key}.")
        else:
            config_map[key] = item
        value_type = item.get("value_type")
        if not allowed(value_type, VALUE_TYPES):
            errors.append(f"{label}.value_type must be one of {', '.join(sorted(VALUE_TYPES))}.")
        elif "default_value" in item and not value_matches_type(item["default_value"], value_type):
            errors.append(f"{label}.default_value does not match value_type {value_type}.")
        if isinstance(value_type, str) and value_type in {"string", "json"} and "default_value" in item:
            try:
                encoded = item["default_value"] if value_type == "string" else json.dumps(item["default_value"], ensure_ascii=False, separators=(",", ":"), allow_nan=False)
                if len(encoded) > MAX_CONFIG_VALUE_CHARS:
                    errors.append(f"{label}.default_value exceeds Roblox's {MAX_CONFIG_VALUE_CHARS}-character limit.")
            except (TypeError, ValueError, UnicodeError):
                errors.append(f"{label}.default_value is not valid JSON-compatible data.")
        if value_type == "number" and isinstance(item.get("default_value"), int) and not isinstance(item.get("default_value"), bool):
            if abs(item["default_value"]) > MAX_EXACT_INTEGER:
                errors.append(f"{label}.default_value integer exceeds exact numeric representation range (2^53).")
        if not allowed(item.get("category"), CATEGORIES):
            errors.append(f"{label}.category must be one of {', '.join(sorted(CATEGORIES))}.")
        if not allowed(item.get("runtime_change_policy"), RUNTIME_POLICIES):
            errors.append(f"{label}.runtime_change_policy must be one of {', '.join(sorted(RUNTIME_POLICIES))}.")
        if not allowed(item.get("fallback_policy"), FALLBACK_POLICIES):
            errors.append(f"{label}.fallback_policy must be one of {', '.join(sorted(FALLBACK_POLICIES))}.")
        targeting_mode = item.get("targeting_mode")
        if not allowed(targeting_mode, TARGETING_MODES):
            errors.append(f"{label}.targeting_mode must be global or conditional.")
        count = item.get("condition_count")
        if not is_int(count, 0, 20):
            errors.append(f"{label}.condition_count must be an integer from 0 to 20.")
        else:
            condition_total += count
            if targeting_mode == "global" and count != 0:
                errors.append(f"{label}.global targeting must have condition_count 0.")
            if targeting_mode == "conditional" and count < 1:
                errors.append(f"{label}.conditional targeting must declare at least one condition.")
        if item.get("condition_order_reviewed") is not True:
            errors.append(f"{label}.condition_order_reviewed must be true.")
        if not is_slug(item.get("owner")):
            errors.append(f"{label}.owner must be a lowercase slug.")
        if item.get("server_only") is not True:
            errors.append(f"{label}.server_only must be true; ConfigService is server-script only.")
        if item.get("contains_secret") is not False:
            errors.append(f"{label}.contains_secret must be false; do not put secrets or credentials in experience configs.")

    if condition_total > 100:
        errors.append("Total condition_count exceeds the documented 100-condition-per-experience limit.")

    events = data.get("events")
    if not isinstance(events, list) or len(events) > 100:
        errors.append("events must be a list of at most 100 event declarations.")
        events = []
    event_ids: set[str] = set()
    parsed_events: list[tuple[dict, datetime, datetime]] = []
    for index, item in enumerate(events):
        label = f"events[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, EVENT_FIELDS, label)
        event_id = item.get("event_id")
        if not is_slug(event_id):
            errors.append(f"{label}.event_id must be a lowercase slug.")
        elif event_id in event_ids:
            errors.append(f"Duplicate event_id: {event_id}.")
        else:
            event_ids.add(event_id)
        if not isinstance(item.get("title"), str) or not 1 <= len(item["title"]) <= 100:
            errors.append(f"{label}.title must contain 1-100 characters.")
        if not is_slug(item.get("schedule_group")):
            errors.append(f"{label}.schedule_group must be a lowercase slug.")
        status = item.get("status")
        if not allowed(status, EVENT_STATUSES):
            errors.append(f"{label}.status must be one of {', '.join(sorted(EVENT_STATUSES))}.")
        start = parse_timestamp(item.get("starts_at"), f"{label}.starts_at", errors)
        end = parse_timestamp(item.get("ends_at"), f"{label}.ends_at", errors)
        if start and end:
            if end <= start:
                errors.append(f"{label}.ends_at must be later than starts_at.")
            else:
                parsed_events.append((item, start, end))
        keys = item.get("config_keys")
        if not isinstance(keys, list) or not 1 <= len(keys) <= 20 or not all(isinstance(x, str) for x in keys):
            errors.append(f"{label}.config_keys must contain 1-20 config keys.")
            keys = []
        elif len(set(keys)) != len(keys):
            errors.append(f"{label}.config_keys must be unique.")
        for key in keys:
            if key not in config_map:
                errors.append(f"{label}.config_keys references undeclared config key {key!r}.")
        enabled_key = item.get("enabled_config_key")
        if not isinstance(enabled_key, str) or enabled_key not in config_map:
            errors.append(f"{label}.enabled_config_key must reference a declared config.")
        elif enabled_key not in keys:
            errors.append(f"{label}.enabled_config_key must also appear in config_keys.")
        elif config_map[enabled_key].get("value_type") != "boolean" or not allowed(config_map[enabled_key].get("category"), {"event_control", "feature_flag"}):
            errors.append(f"{label}.enabled_config_key must reference a boolean event_control or feature_flag config.")
        if item.get("preflight_required") is not True:
            errors.append(f"{label}.preflight_required must be true.")
        cases = item.get("test_case_ids")
        if not isinstance(cases, list) or len(cases) > 20 or not all(is_slug(x) for x in cases):
            errors.append(f"{label}.test_case_ids must contain at most 20 lowercase test-case slugs.")
        elif len(set(cases)) != len(cases):
            errors.append(f"{label}.test_case_ids must be unique.")
        elif isinstance(status, str) and status in {"staged", "scheduled", "active"} and not cases:
            errors.append(f"{label}.test_case_ids must not be empty for staged, scheduled, or active events.")

    active_schedule_statuses = {"staged", "scheduled", "active"}
    for index, (left, left_start, left_end) in enumerate(parsed_events):
        if not allowed(left.get("status"), active_schedule_statuses):
            continue
        for right, right_start, right_end in parsed_events[index + 1:]:
            if not allowed(right.get("status"), active_schedule_statuses):
                continue
            if left.get("schedule_group") == right.get("schedule_group") and left_start < right_end and right_start < left_end:
                errors.append(
                    f"Events {left.get('event_id')} and {right.get('event_id')} overlap in schedule_group {left.get('schedule_group')}."
                )

    deployment = data.get("deployment")
    if not isinstance(deployment, dict):
        errors.append("deployment must be an object.")
        deployment = {}
    else:
        errors += check_fields(deployment, DEPLOYMENT_FIELDS, "deployment")
        if not allowed(deployment.get("strategy"), DEPLOYMENT_STRATEGIES):
            errors.append("deployment.strategy must be Immediate or GradualRollout.")
        for name in (
            "staged_test_required", "pre_publish_validation_required", "published_readback_required",
            "human_approval_required", "publish_message_required", "publish_only_after_approval",
            "draft_hash_guard_required", "api_key_outside_project",
        ):
            if deployment.get(name) is not True:
                errors.append(f"deployment.{name} must be true.")
        message = deployment.get("publish_message")
        if not isinstance(message, str) or not 10 <= len(message) <= 200:
            errors.append("deployment.publish_message must contain 10-200 characters for release history.")

    rollback = data.get("rollback")
    if not isinstance(rollback, dict):
        errors.append("rollback must be an object.")
        rollback = {}
    else:
        errors += check_fields(rollback, ROLLBACK_FIELDS, "rollback")
        for name in ROLLBACK_FIELDS:
            if rollback.get(name) is not True:
                errors.append(f"rollback.{name} must be true; config restore stages a draft and requires a separate publish.")

    consumers = data.get("consumers")
    consumer_ids: set[str] = set()
    consumer_pairs: set[tuple[str, str]] = set()
    if not isinstance(consumers, list) or not 1 <= len(consumers) <= 256:
        errors.append("consumers must contain 1-256 runtime consumer contracts.")
        consumers = []
    for index, item in enumerate(consumers):
        label = f"consumers[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, CONSUMER_FIELDS, label)
        consumer_id = item.get("consumer_id")
        if not is_slug(consumer_id):
            errors.append(f"{label}.consumer_id must be a lowercase slug.")
        elif consumer_id in consumer_ids:
            errors.append(f"Duplicate consumer_id: {consumer_id}.")
        else:
            consumer_ids.add(consumer_id)
        key = item.get("config_key")
        if not isinstance(key, str) or key not in config_map:
            errors.append(f"{label}.config_key must reference a declared config.")
        else:
            if isinstance(consumer_id, str):
                pair = (consumer_id, key)
                if pair in consumer_pairs:
                    errors.append(f"Duplicate consumer/config pair: {consumer_id}/{key}.")
                consumer_pairs.add(pair)
            if item.get("expected_type") != config_map[key].get("value_type"):
                errors.append(f"{label}.expected_type does not match config {key!r}.")
        expected_type = item.get("expected_type")
        if not allowed(expected_type, VALUE_TYPES):
            errors.append(f"{label}.expected_type must be one of {', '.join(sorted(VALUE_TYPES))}.")
        elif "fallback_value" in item and not value_matches_type(item["fallback_value"], expected_type):
            errors.append(f"{label}.fallback_value does not match expected_type.")
        if item.get("required") is True and "fallback_value" not in item:
            errors.append(f"{label}.fallback_value is required for required consumers.")
        if not is_bool(item.get("required")):
            errors.append(f"{label}.required must be boolean.")
        if not allowed(item.get("apply_boundary"), APPLY_BOUNDARIES):
            errors.append(f"{label}.apply_boundary must be one of {', '.join(sorted(APPLY_BOUNDARIES))}.")
        if item.get("server_only") is not True:
            errors.append(f"{label}.server_only must be true.")

    return sorted(set(errors))


def audit_model(data: dict) -> dict:
    config_map = {item["key"]: item for item in data["configs"]}
    referenced: set[str] = set()
    for event in data["events"]:
        referenced.update(event["config_keys"])
    for consumer in data["consumers"]:
        referenced.add(consumer["config_key"])
    warnings: list[str] = []
    unused = sorted(set(config_map) - referenced)
    if unused:
        warnings.append("Config keys have no declared event or runtime consumer: " + ", ".join(unused) + ".")
    if len(data["configs"]) >= 90:
        warnings.append("The InExperienceConfig repository is approaching its 100-key limit; reserve capacity for operational changes.")
    total_conditions = sum(item["condition_count"] for item in data["configs"])
    if total_conditions >= 80:
        warnings.append("Conditional config usage is approaching the documented 100-condition experience limit.")
    if data["deployment"]["strategy"] == "Immediate":
        warnings.append("Immediate publishing can distribute changes quickly; prefer GradualRollout when an incremental deployment is suitable.")
    if any(item["runtime_change_policy"] == "next_safe_boundary" for item in data["configs"]):
        warnings.append("At least one config must be applied at a safe gameplay boundary; do not mutate an active encounter or round mid-flight.")
    if any(item["fallback_policy"] == "keep_last_known_good" for item in data["configs"]):
        warnings.append("Keep-last-known-good behavior requires a real server runtime implementation; this offline validator cannot verify cached snapshots.")
    if not data["events"]:
        warnings.append("No scheduled LiveOps events are declared; add event manifests only when there is a real launch plan.")
    return {
        "schema_version": 1,
        "model_id": data["model_id"],
        "status": "review_required" if warnings else "no_design_warnings",
        "summary": {
            "config_count": len(data["configs"]),
            "conditional_config_count": sum(1 for item in data["configs"] if item["targeting_mode"] == "conditional"),
            "condition_count": total_conditions,
            "event_count": len(data["events"]),
            "runtime_consumer_count": len(data["consumers"]),
            "unused_config_keys": unused,
            "deployment_strategy": data["deployment"]["strategy"],
        },
        "warnings": sorted(set(warnings)),
        "limitations": [
            "This report validates declared JSON contracts only; it does not inspect Luau consumers or call ConfigService/Open Cloud.",
            "It does not stage, publish, restore, or verify live experience configuration.",
            "A passing audit is not approval for a production change. Use a test experience, human approval, and a published readback.",
        ],
    }


def compare_models(baseline: dict, candidate: dict) -> dict:
    baseline_configs = {item["key"]: item for item in baseline["configs"]}
    candidate_configs = {item["key"]: item for item in candidate["configs"]}
    removed = sorted(set(baseline_configs) - set(candidate_configs))
    added = sorted(set(candidate_configs) - set(baseline_configs))
    type_changes = []
    default_changes = []
    for key in sorted(set(baseline_configs) & set(candidate_configs)):
        old = baseline_configs[key]
        new = candidate_configs[key]
        if old["value_type"] != new["value_type"]:
            type_changes.append({"key": key, "before": old["value_type"], "after": new["value_type"]})
        elif old["default_value"] != new["default_value"]:
            default_changes.append({"key": key, "before": old["default_value"], "after": new["default_value"]})
    base_events = {item["event_id"]: item for item in baseline["events"]}
    new_events = {item["event_id"]: item for item in candidate["events"]}
    removed_events = sorted(set(base_events) - set(new_events))
    added_events = sorted(set(new_events) - set(base_events))
    breaking = []
    for key in removed:
        breaking.append(f"Removed config key {key!r}; existing Luau consumers may still reference it.")
    for item in type_changes:
        breaking.append(f"Changed config key {item['key']!r} type from {item['before']} to {item['after']}.")
    warnings = []
    for item in default_changes:
        warnings.append(f"Changed default for {item['key']!r}; review live behavior and fallback assumptions.")
    for event_id in removed_events:
        warnings.append(f"Removed event {event_id!r}; verify its schedule, player messaging, and cleanup plan.")
    for event_id in added_events:
        warnings.append(f"Added event {event_id!r}; verify preflight, schedule, and rollback references.")
    status = "breaking_changes" if breaking else ("review_required" if warnings else "compatible")
    return {
        "schema_version": 1,
        "baseline_model_id": baseline["model_id"],
        "candidate_model_id": candidate["model_id"],
        "status": status,
        "summary": {
            "removed_config_count": len(removed),
            "added_config_count": len(added),
            "type_change_count": len(type_changes),
            "default_change_count": len(default_changes),
            "removed_event_count": len(removed_events),
            "added_event_count": len(added_events),
        },
        "breaking_changes": sorted(breaking),
        "warnings": sorted(warnings),
        "changes": {
            "removed_config_keys": removed,
            "added_config_keys": added,
            "config_type_changes": type_changes,
            "config_default_changes": default_changes,
            "removed_events": removed_events,
            "added_events": added_events,
        },
        "limitations": [
            "The comparison checks declared manifest contracts only; it does not search Luau source for string-literal config references.",
            "Review actual code references and staged config values before removing or changing any published key.",
        ],
    }


def duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"Duplicate JSON key: {key}")
        output[key] = value
    return output


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")


def resolve_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_path(root: Path, raw: str, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw) > 1 and raw[1:2] == ":"):
        raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Empty, dot, and parent path segments are forbidden.")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Symlink traversal is not allowed.")
    resolved = probe.resolve(strict=must_exist)
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise ValueError("Path escapes the project root.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Input must be an existing regular file.")
    return resolved


def load_model(root: Path, raw: str) -> Any:
    path = safe_path(root, raw, True)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("LiveOps model JSON exceeds the 1 MiB input limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=duplicate_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid LiveOps model JSON: {exc}") from exc


def write_report(root: Path, raw: str, report: dict) -> None:
    path = safe_path(root, raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Output must be a regular file.")
    descriptor, temp = tempfile.mkstemp(prefix=".v42-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temp).replace(path)
    finally:
        try:
            Path(temp).unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("doctor")
    command.add_argument("--root", required=True)
    command = sub.add_parser("validate")
    command.add_argument("--root", required=True)
    command.add_argument("--model", required=True)
    command = sub.add_parser("audit")
    command.add_argument("--root", required=True)
    command.add_argument("--model", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("compare")
    command.add_argument("--root", required=True)
    command.add_argument("--baseline", required=True)
    command.add_argument("--candidate", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "doctor":
            print(f"V{VERSION} ready | project={root}")
            return 0
        if args.command == "compare":
            baseline = load_model(root, args.baseline)
            candidate = load_model(root, args.candidate)
            errors = [f"baseline: {item}" for item in validate_model(baseline)]
            errors += [f"candidate: {item}" for item in validate_model(candidate)]
            if errors:
                for error in errors:
                    print("FAIL: " + error)
                return 1
            report = compare_models(baseline, candidate)
            write_report(root, args.output, report)
            print(f"PASS: compatibility report written; status={report['status']}; breaking_changes={len(report['breaking_changes'])}; warnings={len(report['warnings'])}.")
            return 1 if report["breaking_changes"] else 0
        model = load_model(root, args.model)
        errors = validate_model(model)
        if errors:
            for error in errors:
                print("FAIL: " + error)
            return 1
        if args.command == "validate":
            print("PASS: LiveOps config, event schedule, deployment, rollback, and consumer contracts are valid.")
            return 0
        report = audit_model(model)
        write_report(root, args.output, report)
        print(f"PASS: LiveOps audit written; configs={report['summary']['config_count']}; events={report['summary']['event_count']}; consumers={report['summary']['runtime_consumer_count']}; warnings={len(report['warnings'])}.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
