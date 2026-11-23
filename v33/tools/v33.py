#!/usr/bin/env python3
"""Offline validators and bounded QA inventory for the cumulative V33 Roblox toolkit."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "33.0.0"
MAX_FILES = 10_000
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_TESTS = 250
SKIP_DIRS = {
    ".git", ".agents", ".codex", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "node_modules", "target", "build", "dist",
    ".idea", ".vscode", "Packages",
}
PLATFORMS = {"desktop", "mobile", "tablet", "console", "vr"}
NETWORK_PROFILES = {"baseline", "high_latency", "jitter", "packet_loss"}
SCENARIOS = {
    "baseline_smoke", "fresh_join", "respawn", "mid_session_join", "mid_session_leave",
    "rapid_join_leave", "multi_client_replication", "remote_validation", "ui_open_close",
    "touch_navigation", "controller_navigation", "orientation_change", "keyboard_open_close",
    "network_latency", "network_jitter", "network_packet_loss", "save_reload", "cross_device_layout",
}
CATEGORIES = {"smoke", "lifecycle", "multiplayer", "security", "ui", "device", "networking", "persistence"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
EXECUTIONS = {"static_local", "studio_manual", "studio_scripted"}
EXPECTED = {
    "no_unhandled_errors", "state_consistent", "players_replicated", "invalid_request_rejected",
    "ui_action_received", "layout_usable", "orientation_adapted", "input_received",
    "session_recovered", "data_round_trip",
}
RUNNERS = {"studio_plugin", "studio_manual", "local_static"}
STATUSES = {"pass", "fail", "blocked", "not_run"}
OUTCOMES = {
    "passed", "assertion_failed", "unhandled_error", "timeout", "state_divergence",
    "ui_input_missing", "data_roundtrip_failed", "remote_validation_failed",
    "network_disconnect", "studio_unavailable", "setup_incomplete",
    "device_profile_unavailable", "not_executed",
}
FAIL_OUTCOMES = {
    "assertion_failed", "unhandled_error", "timeout", "state_divergence",
    "ui_input_missing", "data_roundtrip_failed", "remote_validation_failed", "network_disconnect",
}
BLOCKED_OUTCOMES = {"studio_unavailable", "setup_incomplete", "device_profile_unavailable"}
SUITE_REF = re.compile(r"^suite-[a-z0-9]{8,24}$")
TEST_ID = re.compile(r"^TC-[A-Z0-9-]{3,24}$")
RUN_REF = re.compile(r"^run-[a-z0-9]{12}$")
EVIDENCE_REF = re.compile(r"^ev-[a-z0-9]{12}$")
PLAN_FIELDS = {"schema_version", "suite_id", "max_simulated_clients", "platforms", "network_profiles", "tests"}
TEST_FIELDS = {"id", "scenario", "category", "priority", "execution", "clients", "platforms", "expected"}
REPORT_FIELDS = {"schema_version", "suite_id", "run_ref", "created_at", "environment", "results"}
ENVIRONMENT_FIELDS = {"runner", "studio_version", "platform", "network_profile", "simulated_clients"}
RESULT_FIELDS = {"test_id", "status", "outcome_code", "executed_at"}
RESULT_OPTIONAL = {"evidence_ref"}
DEFAULT_AUDIT = ".codex/reports/v33-qa-inventory.json"
DEFAULT_COMPARISON = ".codex/reports/v33-regression-comparison.json"


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
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Path cannot traverse a symlink.")
    candidate = root.joinpath(*parts)
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


def reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON numeric constant: {value}")


def load_json(root: Path, raw: str) -> tuple[Path, Any]:
    path = safe_project_path(root, raw, must_exist=True)
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError(f"{path.relative_to(root)} exceeds the {MAX_JSON_BYTES}-byte JSON input limit.")
        data = json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject_json_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path, data


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


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


def is_unique_string_list(value: Any, allowed: set[str], *, minimum: int = 1) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= minimum
        and all(isinstance(item, str) and item in allowed for item in value)
        and len(value) == len(set(value))
    )


def validate_plan(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Test plan must be a JSON object."]
    if set(data) != PLAN_FIELDS:
        missing = PLAN_FIELDS - set(data)
        extra = set(data) - PLAN_FIELDS
        if missing:
            errors.append("Test plan is missing required fields: " + ", ".join(sorted(missing)) + ".")
        if extra:
            errors.append("Test plan contains unsupported fields.")
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")
    suite_id = data.get("suite_id")
    if not isinstance(suite_id, str) or not SUITE_REF.fullmatch(suite_id):
        errors.append("suite_id must be an opaque suite- reference with 8-24 lowercase letters or digits.")
    max_clients = data.get("max_simulated_clients")
    if not isinstance(max_clients, int) or isinstance(max_clients, bool) or not 1 <= max_clients <= 8:
        errors.append("max_simulated_clients must be an integer between 1 and 8.")
    if not is_unique_string_list(data.get("platforms"), PLATFORMS):
        errors.append("platforms must contain one or more unique supported platform codes.")
    if not is_unique_string_list(data.get("network_profiles"), NETWORK_PROFILES):
        errors.append("network_profiles must contain one or more unique supported network profile codes.")
    tests = data.get("tests")
    if not isinstance(tests, list) or not 1 <= len(tests) <= MAX_TESTS:
        errors.append(f"tests must be an array with 1-{MAX_TESTS} entries.")
        return errors
    seen: set[str] = set()
    plan_platforms = set(data.get("platforms", [])) if isinstance(data.get("platforms"), list) else set()
    for index, case in enumerate(tests):
        prefix = f"tests[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        if set(case) != TEST_FIELDS:
            if TEST_FIELDS - set(case):
                errors.append(f"{prefix} is missing required fields.")
            if set(case) - TEST_FIELDS:
                errors.append(f"{prefix} contains unsupported fields.")
        test_id = case.get("id")
        if not isinstance(test_id, str) or not TEST_ID.fullmatch(test_id):
            errors.append(f"{prefix}.id must be a valid TC- identifier.")
        elif test_id in seen:
            errors.append(f"Duplicate test ID: {test_id}.")
        else:
            seen.add(test_id)
        if not isinstance(case.get("scenario"), str) or case.get("scenario") not in SCENARIOS:
            errors.append(f"{prefix}.scenario is not a supported scenario code.")
        if not isinstance(case.get("category"), str) or case.get("category") not in CATEGORIES:
            errors.append(f"{prefix}.category is not a supported category code.")
        if not isinstance(case.get("priority"), str) or case.get("priority") not in PRIORITIES:
            errors.append(f"{prefix}.priority must be P0, P1, P2, or P3.")
        if not isinstance(case.get("execution"), str) or case.get("execution") not in EXECUTIONS:
            errors.append(f"{prefix}.execution is not a supported execution mode.")
        clients = case.get("clients")
        if not isinstance(clients, int) or isinstance(clients, bool) or not 1 <= clients <= 8:
            errors.append(f"{prefix}.clients must be an integer between 1 and 8.")
        elif isinstance(max_clients, int) and not isinstance(max_clients, bool) and clients > max_clients:
            errors.append(f"{prefix}.clients exceeds max_simulated_clients.")
        case_platforms = case.get("platforms")
        if not is_unique_string_list(case_platforms, PLATFORMS):
            errors.append(f"{prefix}.platforms must contain unique supported platform codes.")
        elif not set(case_platforms).issubset(plan_platforms):
            errors.append(f"{prefix}.platforms must be a subset of plan platforms.")
        if not isinstance(case.get("expected"), str) or case.get("expected") not in EXPECTED:
            errors.append(f"{prefix}.expected is not a supported expected-result code.")
    return errors


def validate_report(data: Any, plan: Any) -> list[str]:
    errors: list[str] = []
    plan_errors = validate_plan(plan)
    if plan_errors:
        return ["Cannot validate report against an invalid plan."] + plan_errors
    if not isinstance(data, dict):
        return ["Test report must be a JSON object."]
    if set(data) != REPORT_FIELDS:
        if REPORT_FIELDS - set(data):
            errors.append("Test report is missing required fields.")
        if set(data) - REPORT_FIELDS:
            errors.append("Test report contains unsupported fields; do not add raw logs, player identifiers, or free text.")
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        errors.append("Report schema_version must equal 1.")
    if data.get("suite_id") != plan.get("suite_id"):
        errors.append("Report suite_id must match the supplied plan.")
    run_ref = data.get("run_ref")
    if not isinstance(run_ref, str) or not RUN_REF.fullmatch(run_ref):
        errors.append("run_ref must be an opaque run- reference with exactly 12 lowercase letters or digits.")
    if parse_timestamp(data.get("created_at")) is None:
        errors.append("created_at must be an ISO-8601 timestamp with a timezone.")
    environment = data.get("environment")
    if not isinstance(environment, dict):
        errors.append("environment must be an object.")
        return errors
    if set(environment) != ENVIRONMENT_FIELDS:
        errors.append("environment must contain exactly the documented fields.")
    runner = environment.get("runner")
    if not isinstance(runner, str) or runner not in RUNNERS:
        errors.append("environment.runner is not supported.")
    studio_version = environment.get("studio_version")
    if not isinstance(studio_version, str) or not studio_version.strip() or len(studio_version) > 80:
        errors.append("environment.studio_version must be a non-empty string of at most 80 characters.")
    elif runner in {"studio_plugin", "studio_manual"} and studio_version == "not_applicable":
        errors.append("A Studio runner must record its Studio version.")
    elif runner == "local_static" and studio_version != "not_applicable":
        errors.append("local_static reports must set studio_version to not_applicable.")
    platform = environment.get("platform")
    if not isinstance(platform, str) or platform not in PLATFORMS or platform not in plan.get("platforms", []):
        errors.append("environment.platform must be a platform included in the plan.")
    network_profile = environment.get("network_profile")
    if not isinstance(network_profile, str) or network_profile not in NETWORK_PROFILES or network_profile not in plan.get("network_profiles", []):
        errors.append("environment.network_profile must be a profile included in the plan.")
    simulated_clients = environment.get("simulated_clients")
    if not isinstance(simulated_clients, int) or isinstance(simulated_clients, bool) or not 1 <= simulated_clients <= 8:
        errors.append("environment.simulated_clients must be an integer between 1 and 8.")
    elif simulated_clients > plan.get("max_simulated_clients", 0):
        errors.append("environment.simulated_clients exceeds the plan maximum.")
    if runner == "local_static" and simulated_clients != 1:
        errors.append("local_static reports must set simulated_clients to 1.")
    results = data.get("results")
    if not isinstance(results, list) or not 1 <= len(results) <= MAX_TESTS:
        errors.append(f"results must be an array with 1-{MAX_TESTS} entries.")
        return errors
    test_map = {case["id"]: case for case in plan["tests"]}
    seen: set[str] = set()
    for index, result in enumerate(results):
        prefix = f"results[{index}]"
        if not isinstance(result, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        if not RESULT_FIELDS.issubset(result) or set(result) - RESULT_FIELDS - RESULT_OPTIONAL:
            errors.append(f"{prefix} has missing or unsupported fields.")
        test_id = result.get("test_id")
        if not isinstance(test_id, str) or test_id not in test_map:
            errors.append(f"{prefix}.test_id is not present in the plan.")
            continue
        if test_id in seen:
            errors.append(f"Duplicate result for test ID: {test_id}.")
        seen.add(test_id)
        status = result.get("status")
        outcome = result.get("outcome_code")
        executed_at = result.get("executed_at")
        evidence_ref = result.get("evidence_ref")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"{prefix}.status is not supported.")
        if not isinstance(outcome, str) or outcome not in OUTCOMES:
            errors.append(f"{prefix}.outcome_code is not supported.")
        if evidence_ref is not None and (not isinstance(evidence_ref, str) or not EVIDENCE_REF.fullmatch(evidence_ref)):
            errors.append(f"{prefix}.evidence_ref must be an opaque ev- reference.")
        if status == "pass" and outcome != "passed":
            errors.append(f"{prefix}: pass status requires outcome_code passed.")
        elif status == "fail" and (not isinstance(outcome, str) or outcome not in FAIL_OUTCOMES):
            errors.append(f"{prefix}: fail status requires a failure outcome code.")
        elif status == "blocked" and (not isinstance(outcome, str) or outcome not in BLOCKED_OUTCOMES):
            errors.append(f"{prefix}: blocked status requires a blocker outcome code.")
        elif status == "not_run" and outcome != "not_executed":
            errors.append(f"{prefix}: not_run status requires outcome_code not_executed.")
        if isinstance(status, str) and status in {"pass", "fail"} and parse_timestamp(executed_at) is None:
            errors.append(f"{prefix}.executed_at must be timezone-aware for an executed test.")
        elif status == "not_run" and executed_at is not None:
            errors.append(f"{prefix}.executed_at must be null for a not_run test.")
        elif status == "blocked" and executed_at is not None and parse_timestamp(executed_at) is None:
            errors.append(f"{prefix}.executed_at must be null or timezone-aware.")
        case = test_map[test_id]
        if runner == "local_static" and case["execution"] != "static_local" and isinstance(status, str) and status in {"pass", "fail"}:
            errors.append(f"{prefix}: local_static cannot pass or fail a Studio test.")
    missing = set(test_map) - seen
    if missing:
        errors.append("Report is missing results for test IDs: " + ", ".join(sorted(missing)) + ".")
    return errors


def compare_reports(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    before = {item["test_id"]: item for item in baseline["results"]}
    after = {item["test_id"]: item for item in current["results"]}
    regressions: list[dict[str, str]] = []
    newly_blocked: list[dict[str, str]] = []
    coverage_gaps: list[dict[str, str]] = []
    improvements: list[dict[str, str]] = []
    unchanged = 0
    for test_id in sorted(before):
        old = before[test_id]
        new = after[test_id]
        record = {
            "test_id": test_id,
            "baseline_status": old["status"],
            "current_status": new["status"],
            "baseline_outcome": old["outcome_code"],
            "current_outcome": new["outcome_code"],
        }
        if old["status"] == "pass" and new["status"] == "fail":
            regressions.append(record)
        elif old["status"] == "pass" and new["status"] == "blocked":
            newly_blocked.append(record)
        elif old["status"] == "pass" and new["status"] == "not_run":
            coverage_gaps.append(record)
        elif old["status"] != "pass" and new["status"] == "pass":
            improvements.append(record)
        elif old["status"] == new["status"] and old["outcome_code"] == new["outcome_code"]:
            unchanged += 1
    return {
        "report_type": "v33_regression_comparison",
        "schema_version": 1,
        "version": VERSION,
        "suite_id": baseline["suite_id"],
        "baseline_run_ref": baseline["run_ref"],
        "current_run_ref": current["run_ref"],
        "counts": {
            "tests_compared": len(before),
            "regressions": len(regressions),
            "newly_blocked": len(newly_blocked),
            "coverage_gaps": len(coverage_gaps),
            "improvements": len(improvements),
            "unchanged": unchanged,
        },
        "regressions": regressions,
        "newly_blocked": newly_blocked,
        "coverage_gaps": coverage_gaps,
        "improvements": improvements,
        "execution_status": "report_comparison_only",
        "limitations": [
            "Comparison checks supplied, structurally valid reports; it cannot prove that external evidence is truthful.",
            "A newly blocked test is an execution blocker, not proof of a gameplay regression.",
            "A not_run test is a coverage gap and must never be treated as a pass.",
            "This comparison does not approve a release or execute Roblox Studio tests.",
        ],
    }


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


def is_test_candidate(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    parts = {part.lower() for part in relative.parts}
    name = path.name.lower()
    return bool(parts & {"test", "tests", "spec", "specs"}) or name.endswith(
        (".spec.lua", ".spec.luau", "_test.lua", "_test.luau", ".test.lua", ".test.luau")
    )


def audit_project(root: Path, max_files: int = MAX_FILES) -> dict[str, Any]:
    warnings: list[str] = []
    files = iter_luau_files(root, max(1, min(max_files, MAX_FILES)), warnings)
    readable = 0
    test_candidates = 0
    studio_test_service_refs = 0
    device_simulator_refs = 0
    virtual_input_refs = 0
    for path in files:
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            warnings.append(f"Skipped unreadable Luau source: {path.relative_to(root)}")
            continue
        readable += 1
        if is_test_candidate(path, root):
            test_candidates += 1
        studio_test_service_refs += len(re.findall(r"\bStudioTestService\b", source))
        device_simulator_refs += len(re.findall(r"\bStudioDeviceSimulatorService\b", source))
        virtual_input_refs += len(re.findall(r"\bCreateVirtualInput\b|\bVirtualInput\b", source))
    return {
        "report_type": "v33_qa_source_inventory",
        "schema_version": 1,
        "version": VERSION,
        "project_root_name": root.name,
        "inventory": {
            "luau_files_discovered": len(files),
            "files_read": readable,
            "test_candidate_files": test_candidates,
            "studio_test_service_references": studio_test_service_refs,
            "device_simulator_service_references": device_simulator_refs,
            "virtual_input_references": virtual_input_refs,
        },
        "warnings": warnings,
        "execution_status": "static_inventory_only",
        "studio_execution_performed": False,
        "limitations": [
            "This bounded scan is a file inventory and API-name search, not a Luau parser or semantic test.",
            "It does not execute code, launch Studio, simulate clients/devices/input, or contact Roblox services.",
            "A test candidate filename does not prove that the file contains valid or passing tests.",
            "No player identities, raw chat, credentials, or live game data are collected.",
        ],
    }


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    warnings: list[str] = []
    files = iter_luau_files(root, MAX_FILES, warnings)
    print(f"Project: {root}")
    print(f"Luau/Lua source files discovered: {len(files)}")
    print("Optional local tools:")
    for executable in ("git", "rojo", "luau-analyze", "selene"):
        print(f"  {executable}: {shutil.which(executable) or 'not found on PATH'}")
    print("No command is executed, no Roblox connection is attempted, and no Studio session is launched.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    report = audit_project(root, args.max_files)
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    inventory = report["inventory"]
    print(f"Read-only QA inventory written to: {output}")
    print(
        f"Luau files: {inventory['files_read']}; test candidates: {inventory['test_candidate_files']}; "
        f"StudioTestService refs: {inventory['studio_test_service_references']}; "
        f"device simulator refs: {inventory['device_simulator_service_references']}; "
        f"VirtualInput refs: {inventory['virtual_input_references']}"
    )
    print("Static inventory only; no Studio test or Roblox service was executed.")
    return 0


def command_validate_plan(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    path, plan = load_json(root, args.plan)
    errors = validate_plan(plan)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: validated test plan {plan['suite_id']} with {len(plan['tests'])} test cases ({path.relative_to(root)}).")
    print("Validation is structural; it does not execute or approve the planned tests.")
    return 0


def command_validate_report(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    _, plan = load_json(root, args.plan)
    path, report = load_json(root, args.report)
    errors = validate_report(report, plan)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    counts = {status: sum(1 for item in report["results"] if item["status"] == status) for status in sorted(STATUSES)}
    print(f"PASS: validated run {report['run_ref']} with {len(report['results'])} complete test results ({path.relative_to(root)}).")
    print("Status counts: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    print("Report validation checks consistency only; it cannot prove external evidence or Studio execution.")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    _, plan = load_json(root, args.plan)
    _, baseline = load_json(root, args.baseline)
    _, current = load_json(root, args.current)
    errors = validate_report(baseline, plan) + validate_report(current, plan)
    if not isinstance(baseline, dict) or not isinstance(current, dict):
        errors.append("Baseline and current reports must be JSON objects.")
    else:
        if baseline.get("suite_id") != current.get("suite_id"):
            errors.append("Baseline and current reports must use the same suite_id.")
        if baseline.get("run_ref") == current.get("run_ref"):
            errors.append("Baseline and current reports must have different run_ref values.")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    comparison = compare_reports(baseline, current)
    output = safe_output_path(root, args.output)
    atomic_write_json(output, comparison)
    print(f"PASS: report comparison written to: {output}")
    for key, value in comparison["counts"].items():
        print(f"  {key}: {value}")
    print("Comparison is a triage aid, not an automatic release approval.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Inspect local Luau inventory and optional tools.")
    doctor.add_argument("--root", required=True)
    doctor.set_defaults(func=command_doctor)
    audit = sub.add_parser("audit", help="Create a bounded read-only source/test inventory.")
    audit.add_argument("--root", required=True)
    audit.add_argument("--output", default=DEFAULT_AUDIT)
    audit.add_argument("--max-files", type=int, default=MAX_FILES)
    audit.set_defaults(func=command_audit)
    plan = sub.add_parser("validate-plan", help="Validate a structured test plan.")
    plan.add_argument("--root", required=True)
    plan.add_argument("--plan", default=".codex/qa/test-plan.json")
    plan.set_defaults(func=command_validate_plan)
    report = sub.add_parser("validate-report", help="Validate a complete run report against its plan.")
    report.add_argument("--root", required=True)
    report.add_argument("--plan", default=".codex/qa/test-plan.json")
    report.add_argument("--report", default=".codex/qa/test-report.json")
    report.set_defaults(func=command_validate_report)
    compare = sub.add_parser("compare", help="Compare baseline and current reports for regressions.")
    compare.add_argument("--root", required=True)
    compare.add_argument("--plan", default=".codex/qa/test-plan.json")
    compare.add_argument("--baseline", default=".codex/qa/baseline-report.json")
    compare.add_argument("--current", default=".codex/qa/current-report.json")
    compare.add_argument("--output", default=DEFAULT_COMPARISON)
    compare.set_defaults(func=command_compare)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
