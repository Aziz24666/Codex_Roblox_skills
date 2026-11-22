#!/usr/bin/env python3
"""V26 read-only Studio MCP preflight and review-only test-plan utility."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "26.0.0"
DEFAULT_PLAN = ".codex/testing/studio-mcp-test-plan.json"
REQUIRED_APPROVALS = (
    "saving a modified place",
    "publishing",
    "production DataStore writes",
    "player-impacting Open Cloud operations",
)


def resolve_project_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def _server_entry(config: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(config, dict):
        return None, ["Configuration root must be a JSON object."]
    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        return None, ["Configuration must contain an mcpServers object."]
    entry = servers.get("Roblox_Studio")
    if entry is None:
        entry = next(
            (value for key, value in servers.items()
             if isinstance(key, str) and key.casefold() in {"roblox studio", "roblox_studio"}),
            None,
        )
    if not isinstance(entry, dict):
        return None, ["A Roblox_Studio server entry was not found."]
    return entry, []


def inspect_mcp_config(path: Path) -> dict[str, Any]:
    """Inspect JSON structure only. Never execute the configured command or reveal its values."""
    try:
        resolved = path.expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return {"state": "fail", "command_kind": "unknown",
                "errors": ["MCP configuration file could not be found or read."], "warnings": []}
    if not resolved.is_file():
        return {"state": "fail", "command_kind": "unknown",
                "errors": ["MCP configuration path is not a regular file."], "warnings": []}
    try:
        config = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"state": "fail", "command_kind": "unknown",
                "errors": ["MCP configuration is not readable UTF-8 JSON."], "warnings": []}

    entry, errors = _server_entry(config)
    if errors:
        return {"state": "fail", "command_kind": "unknown", "errors": errors, "warnings": []}

    command = entry.get("command")
    args = entry.get("args", [])
    if not isinstance(command, str) or not command.strip():
        return {"state": "fail", "command_kind": "unknown",
                "errors": ["Roblox_Studio command must be a non-empty string."], "warnings": []}
    if not isinstance(args, list) or any(not isinstance(item, str) for item in args):
        return {"state": "fail", "command_kind": "unknown",
                "errors": ["Roblox_Studio args must be an array of strings."], "warnings": []}

    normalized_command = command.strip().replace("/", "\\").casefold()
    normalized_args = [item.casefold() for item in args]
    if normalized_command in {"cmd.exe", "cmd"} and len(normalized_args) >= 2:
        windows_target = any("%localappdata%\\roblox\\mcp.bat" in item.replace("/", "\\") for item in normalized_args[1:])
        if normalized_args[0] == "/c" and windows_target:
            return {"state": "pass", "command_kind": "official_windows_example",
                    "errors": [], "warnings": [
                        "The configured command was not executed; confirm Studio's green MCP connection indicator."
                    ]}
    if "studiomcp" in normalized_command:
        return {"state": "pass", "command_kind": "studio_mcp_binary",
                "errors": [], "warnings": [
                    "The configured command was not executed; confirm Studio's green MCP connection indicator."
                ]}

    return {"state": "review", "command_kind": "custom",
            "errors": [], "warnings": [
                "The command differs from the documented examples. Verify its source and arguments manually; V26 did not execute it."
            ]}


def doctor_report(root: Path, config_path: Path | None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "toolkit_version": VERSION,
        "project_root": str(root),
        "project_root_valid": True,
        "mcp_config": {"state": "not_checked", "command_kind": "unknown", "errors": [], "warnings": []},
        "warnings": [
            "A valid config does not prove the MCP server is connected or identify the intended Studio instance.",
            "This command is read-only and does not launch Studio or execute configured commands.",
        ],
    }
    if config_path is not None:
        report["mcp_config"] = inspect_mcp_config(config_path)
    else:
        report["warnings"].append("No MCP config path was supplied; client configuration was not inspected.")
    return report


def build_test_plan(root: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "toolkit_version": VERSION,
        "project_root": str(root),
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "execution_mode": "manual_review_only",
        "does_not_execute_tools": True,
        "production_data_access": False,
        "published_experience_testing": False,
        "requires_human_approval_before": list(REQUIRED_APPROVALS),
        "stages": [
            {
                "id": "preflight", "name": "Project and Studio identity", "client_counts": [1],
                "checks": ["Confirm project and place", "Confirm target studio_id", "Confirm isolated test environment"],
                "evidence": ["Place identity", "Studio instance identity"],
            },
            {
                "id": "static", "name": "Static and contract validation", "client_counts": [],
                "checks": ["Compile Luau", "Check script and remote contracts", "Review changed-file scope"],
                "evidence": ["Compiler output", "Changed-file list"],
            },
            {
                "id": "smoke", "name": "Single-client smoke test", "client_counts": [1],
                "checks": ["Spawn and initialize", "Exercise primary user flow", "Check clean exit"],
                "evidence": ["Studio console output", "Focused screenshot"],
            },
            {
                "id": "multiplayer", "name": "Multiplayer test matrix", "client_counts": [2, 4, 8],
                "checks": ["Replication and ownership", "Join/leave sequencing", "Shared-state correctness"],
                "evidence": ["Server output", "Client observations", "Exact simulated client count"],
            },
            {
                "id": "device", "name": "Device and input coverage", "client_counts": [],
                "checks": ["Phone and tablet layout", "Desktop layout", "Controller and orientation where supported"],
                "evidence": ["Device profile", "Viewport screenshots"],
            },
            {
                "id": "network", "name": "Degraded-network coverage", "client_counts": [],
                "checks": ["Baseline conditions", "Added latency", "Jitter and packet loss where relevant"],
                "evidence": ["Inbound/outbound settings", "Observed behaviour", "Console output"],
            },
            {
                "id": "review", "name": "Evidence and approval review", "client_counts": [],
                "checks": ["Classify PASS/FAIL/BLOCKED/NOT RUN", "List untested cases", "Review save/publish approvals"],
                "evidence": ["Test summary", "Screenshots/log references", "Approval record where required"],
            },
        ],
        "safety": {
            "uses_synthetic_test_data": True,
            "isolated_test_place_required": True,
            "never_write_production_datastores": True,
            "never_publish_automatically": True,
            "no_gambling_or_coercive_monetization": True,
        },
    }


def verify_plan_document(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["Plan root must be a JSON object."]
    if plan.get("schema_version") != 1:
        errors.append("Unsupported or missing schema_version.")
    if plan.get("toolkit_version") != VERSION:
        errors.append("toolkit_version must match V26.")
    if plan.get("execution_mode") != "manual_review_only":
        errors.append("execution_mode must remain manual_review_only.")
    if plan.get("does_not_execute_tools") is not True:
        errors.append("Plan must explicitly state that it does not execute tools.")
    if plan.get("production_data_access") is not False:
        errors.append("Plan must not access production data.")
    if plan.get("published_experience_testing") is not False:
        errors.append("Plan must not claim to test a published experience.")
    approvals = plan.get("requires_human_approval_before")
    if (
        not isinstance(approvals, list)
        or any(not isinstance(item, str) for item in approvals)
        or not set(REQUIRED_APPROVALS).issubset(set(approvals))
    ):
        errors.append("Plan is missing one or more mandatory human-approval boundaries.")
    stages = plan.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("Plan must contain a non-empty stages array.")
    else:
        ids: set[str] = set()
        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                errors.append(f"Stage {index} must be an object.")
                continue
            stage_id = stage.get("id")
            if not isinstance(stage_id, str) or not stage_id or stage_id in ids:
                errors.append(f"Stage {index} has a missing or duplicate id.")
            else:
                ids.add(stage_id)
            counts = stage.get("client_counts", [])
            if not isinstance(counts, list) or any(
                not isinstance(count, int) or isinstance(count, bool) or count < 1 or count > 8
                for count in counts
            ):
                errors.append(f"Stage {index} has invalid client_counts; supported range is 1-8.")
            for field in ("checks", "evidence"):
                values = stage.get(field)
                if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                    errors.append(f"Stage {index} field {field!r} must be an array of strings.")
    safety = plan.get("safety")
    if not isinstance(safety, dict):
        errors.append("Plan safety object is missing.")
    else:
        for key in ("uses_synthetic_test_data", "isolated_test_place_required",
                    "never_write_production_datastores", "never_publish_automatically",
                    "no_gambling_or_coercive_monetization"):
            if safety.get(key) is not True:
                errors.append(f"Plan safety invariant {key!r} must remain true.")
    return errors


def plan_output_path(root: Path, raw: str) -> Path:
    supplied = Path(raw).expanduser()
    candidate = supplied if supplied.is_absolute() else root / supplied
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Plan output must be inside the selected project root.") from exc
    if not relative.parts or ".." in relative.parts:
        raise ValueError("Plan output must be a safe relative path inside the project root.")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ValueError("Plan output cannot traverse a symlinked directory.")
    current.mkdir(parents=True, exist_ok=True)
    parent = current.resolve(strict=True)
    if not parent.is_relative_to(root):
        raise ValueError("Plan output resolves outside the selected project root.")
    target = parent / relative.name
    if target.is_symlink():
        raise ValueError("Plan output cannot replace a symlink.")
    if target.exists() and not target.is_file():
        raise ValueError("Plan output path is not a regular file.")
    return target


def write_plan(root: Path, raw_output: str, force: bool = False) -> Path:
    target = plan_output_path(root, raw_output)
    if target.exists() and not force:
        raise FileExistsError("Plan already exists; use --force only after reviewing the existing file.")
    payload = json.dumps(build_test_plan(root), indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        if target.exists() and not force:
            raise FileExistsError("Plan already exists; refusing to overwrite it.")
        os.replace(temporary, target)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return target


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.root)
    report = doctor_report(root, Path(args.config) if args.config else None)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"V26 Studio MCP doctor — {report['toolkit_version']}")
        print(f"Project root: {root}")
        print(f"MCP config: {report['mcp_config']['state']}")
        for warning in report["warnings"] + report["mcp_config"]["warnings"]:
            print(f"WARNING: {warning}")
        for error in report["mcp_config"]["errors"]:
            print(f"FAIL: {error}", file=sys.stderr)
    return 1 if report["mcp_config"]["state"] == "fail" else 0


def command_plan(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.root)
    target = write_plan(root, args.output, args.force)
    print(f"PASS: review-only Studio test plan created: {target}")
    print("No Studio connection, MCP action, playtest, save, or publish operation was performed.")
    return 0


def command_verify_plan(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser()
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print("FAIL: plan is missing, unreadable, or invalid JSON.", file=sys.stderr)
        return 1
    errors = verify_plan_document(plan)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: V26 test plan structure and safety invariants verified.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Read-only project and MCP JSON preflight.")
    doctor.add_argument("--root", required=True, help="Existing Roblox project directory.")
    doctor.add_argument("--config", help="Optional MCP JSON config file to inspect; never executed.")
    doctor.add_argument("--format", choices=("text", "json"), default="text")
    doctor.set_defaults(handler=command_doctor)

    plan = sub.add_parser("plan", help="Generate a review-only Studio test-plan JSON file.")
    plan.add_argument("--root", required=True, help="Existing Roblox project directory.")
    plan.add_argument("--output", default=DEFAULT_PLAN, help=f"Output path inside the project root (default: {DEFAULT_PLAN}).")
    plan.add_argument("--force", action="store_true", help="Replace an existing regular plan file after review.")
    plan.set_defaults(handler=command_plan)

    verify = sub.add_parser("verify-plan", help="Verify a plan's structure and safety invariants.")
    verify.add_argument("--path", required=True, help="Path to an existing Studio test-plan JSON file.")
    verify.set_defaults(handler=command_verify_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, RuntimeError, ValueError, FileExistsError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
