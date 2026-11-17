#!/usr/bin/env python3
"""Validate V15 JSON contracts and benchmark/evidence honesty rules."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}
ENVIRONMENTS = {"static", "luau-cli", "rojo-build", "studio", "device-simulator", "physical-device", "staging-service", "production"}

def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc

def validate_manifest(data, path):
    required = {"schema_version", "project_name", "project_kind", "entrypoints", "toolchain"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{path}: missing manifest keys: {sorted(missing)}")
    if data["schema_version"] != 1 or not str(data["project_name"]).strip():
        raise ValueError(f"{path}: invalid schema_version or project_name")
    if data["project_kind"] not in {"experience", "plugin", "package", "shared-library"}:
        raise ValueError(f"{path}: invalid project_kind")
    if not isinstance(data["entrypoints"], list) or not isinstance(data["toolchain"], dict):
        raise ValueError(f"{path}: entrypoints must be a list and toolchain an object")
    if not data["toolchain"].get("luau") or not data["toolchain"].get("rojo"):
        raise ValueError(f"{path}: toolchain must pin luau and rojo")

def validate_benchmarks(data, path):
    if data.get("schema_version") != 1 or not isinstance(data.get("tasks"), list) or not data["tasks"]:
        raise ValueError(f"{path}: expected schema_version 1 and non-empty tasks")
    seen = set()
    for task in data["tasks"]:
        tid = task.get("task_id")
        if not tid or tid in seen:
            raise ValueError(f"{path}: missing or duplicate task_id {tid!r}")
        seen.add(tid)
        if not task.get("required_skill_tags") or not task.get("acceptance_criteria"):
            raise ValueError(f"{path}: task {tid} needs skill tags and acceptance criteria")

def validate_evidence(data, path):
    required = {"schema_version", "run_id", "environment", "scenario_id", "status", "started_at"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{path}: missing evidence keys: {sorted(missing)}")
    if data["schema_version"] != 1 or data["environment"] not in ENVIRONMENTS or data["status"] not in STATUSES:
        raise ValueError(f"{path}: invalid schema_version, environment, or status")
    if data["status"] == "PASS" and not (data.get("artifacts") or data.get("logs")):
        raise ValueError(f"{path}: PASS requires at least one evidence artifact or log reference")
    if data["environment"] == "studio" and data.get("client_count", 0) < 1:
        raise ValueError(f"{path}: Studio evidence must record client_count >= 1")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root
    checks = [
        (root / "examples/project-manifest.example.json", validate_manifest),
        (root / "examples/benchmark-tasks.json", validate_benchmarks),
    ]
    errors = []
    for path, validator in checks:
        try:
            validator(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    for path in sorted((root / "examples").glob("*evidence*.json")):
        try:
            validate_evidence(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("V15 contract validation passed. No Roblox Studio runtime was executed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
