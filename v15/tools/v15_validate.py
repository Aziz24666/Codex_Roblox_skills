#!/usr/bin/env python3
"""Validate V15 JSON contracts and native Codex skill metadata using only stdlib."""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}
ENVIRONMENTS = {"static", "luau-cli", "rojo-build", "studio", "device-simulator", "physical-device", "staging-service", "production"}
EXPECTED_SKILLS = {
    "roblox-project-intelligence", "roblox-skill-selection-orchestration",
    "roblox-acceptance-driven-implementation", "roblox-remote-security-review",
    "roblox-persistence-migration-testing", "roblox-performance-regression-testing",
    "roblox-runtime-evidence-triage", "roblox-reproducible-release-engineering",
}
SCHEMAS = {
    "project-manifest.schema.json": {"schema_version", "project_name", "project_kind", "entrypoints", "toolchain"},
    "task-evaluation.schema.json": {"schema_version", "task_id", "selected_skills", "criteria", "result"},
    "runtime-evidence.schema.json": {"schema_version", "run_id", "environment", "scenario_id", "status", "started_at"},
}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


def require_object(data, path):
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")


def validate_manifest(data, path):
    require_object(data, path)
    required = {"schema_version", "project_name", "project_kind", "entrypoints", "toolchain"}
    if required - data.keys():
        raise ValueError(f"{path}: missing manifest keys: {sorted(required - data.keys())}")
    if data["schema_version"] != 1 or not isinstance(data["project_name"], str) or not data["project_name"].strip():
        raise ValueError(f"{path}: invalid schema_version or project_name")
    if data["project_kind"] not in {"experience", "plugin", "package", "shared-library"}:
        raise ValueError(f"{path}: invalid project_kind")
    entries = data["entrypoints"]
    if not isinstance(entries, list) or any(not isinstance(x, str) or not x.strip() for x in entries):
        raise ValueError(f"{path}: entrypoints must be non-empty strings")
    if len(entries) != len(set(entries)):
        raise ValueError(f"{path}: entrypoints must be unique")
    toolchain = data["toolchain"]
    if not isinstance(toolchain, dict) or not all(isinstance(toolchain.get(k), str) and toolchain[k].strip() for k in ("luau", "rojo")):
        raise ValueError(f"{path}: toolchain must pin luau and rojo")


def validate_benchmarks(data, path):
    require_object(data, path)
    tasks = data.get("tasks")
    if data.get("schema_version") != 1 or not isinstance(tasks, list) or not tasks:
        raise ValueError(f"{path}: expected schema_version 1 and non-empty tasks")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError(f"{path}: each task must be an object")
        tid = task.get("task_id")
        if not isinstance(tid, str) or not tid.strip() or tid in seen:
            raise ValueError(f"{path}: missing or duplicate task_id {tid!r}")
        seen.add(tid)
        for field in ("required_skill_tags", "acceptance_criteria"):
            values = task.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values):
                raise ValueError(f"{path}: task {tid} needs non-empty string {field}")


def validate_evidence(data, path):
    require_object(data, path)
    required = {"schema_version", "run_id", "environment", "scenario_id", "status", "started_at"}
    if required - data.keys():
        raise ValueError(f"{path}: missing evidence keys: {sorted(required - data.keys())}")
    if data["schema_version"] != 1 or data["environment"] not in ENVIRONMENTS or data["status"] not in STATUSES:
        raise ValueError(f"{path}: invalid schema_version, environment, or status")
    for field in ("run_id", "scenario_id", "started_at"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"{path}: {field} must be a non-empty string")
    try:
        datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path}: started_at must be ISO 8601") from exc
    for field in ("artifacts", "logs", "limitations"):
        if field in data and (not isinstance(data[field], list) or any(not isinstance(x, str) for x in data[field])):
            raise ValueError(f"{path}: {field} must be an array of strings")
    if data["status"] == "PASS" and not (data.get("artifacts") or data.get("logs")):
        raise ValueError(f"{path}: PASS requires an evidence artifact or log reference")
    if data["environment"] == "studio" and (not isinstance(data.get("client_count"), int) or data["client_count"] < 1):
        raise ValueError(f"{path}: Studio evidence must record client_count >= 1")


def validate_task_evaluation(data, path):
    require_object(data, path)
    required = {"schema_version", "task_id", "selected_skills", "criteria", "result"}
    if required - data.keys():
        raise ValueError(f"{path}: missing evaluation keys: {sorted(required - data.keys())}")
    if data["schema_version"] != 1 or not isinstance(data["task_id"], str) or not data["task_id"].strip():
        raise ValueError(f"{path}: invalid schema_version or task_id")
    if not isinstance(data["selected_skills"], list) or any(not isinstance(x, str) for x in data["selected_skills"]):
        raise ValueError(f"{path}: selected_skills must be an array of strings")
    if data["result"] not in {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}:
        raise ValueError(f"{path}: invalid task result")
    criteria = data["criteria"]
    if not isinstance(criteria, list) or not criteria:
        raise ValueError(f"{path}: criteria must be a non-empty array")
    statuses = []
    for item in criteria:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip() for k in ("id", "description", "status")):
            raise ValueError(f"{path}: each criterion needs id, description, and status")
        if item["status"] not in STATUSES:
            raise ValueError(f"{path}: invalid criterion status {item['status']}")
        statuses.append(item["status"])
    if data["result"] == "PASS" and any(s not in {"PASS", "NOT_APPLICABLE"} for s in statuses):
        raise ValueError(f"{path}: PASS conflicts with a non-passing criterion")
    if data["result"] == "FAIL" and "FAIL" not in statuses:
        raise ValueError(f"{path}: FAIL requires at least one FAIL criterion")


def validate_schemas(root):
    for filename, expected in SCHEMAS.items():
        path = root / "schemas" / filename
        schema = load(path)
        require_object(schema, path)
        properties, required = schema.get("properties"), schema.get("required")
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise ValueError(f"{path}: schema needs properties object and required array")
        if set(required) != expected or not expected.issubset(properties):
            raise ValueError(f"{path}: required/properties contract mismatch")
        if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
            raise ValueError(f"{path}: top-level schema must be a closed object")


def parse_skill(path):
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    front = content[4:end]
    name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", front, re.MULTILINE)
    description = re.search(r'^description:\s*"?([^\n"]{20,})"?\s*$', front, re.MULTILINE)
    if not name or not description:
        raise ValueError(f"{path}: frontmatter requires valid name and description")
    body = content[end + 5:].strip()
    if "Mandatory current-source research gate" not in body and "V10 mandatory current-source research gate" not in body:
        raise ValueError(f"{path}: missing mandatory current-source research gate")
    if len(name.group(1)) > 64 or len(description.group(1).strip()) > 160 or len(body) < 200:
        raise ValueError(f"{path}: invalid name length or insufficient instructions")
    return name.group(1)


def validate_skills(root):
    skill_root = root / "codex-skills"
    if not skill_root.is_dir():
        raise ValueError(f"{skill_root}: missing native Codex skill source directory")
    names = set()
    for folder in sorted(p for p in skill_root.iterdir() if p.is_dir()):
        path = folder / "SKILL.md"
        if not path.is_file():
            raise ValueError(f"{folder}: missing required SKILL.md")
        name = parse_skill(path)
        if name != folder.name or name in names:
            raise ValueError(f"{path}: duplicate or folder-mismatched skill name")
        names.add(name)
    if names != EXPECTED_SKILLS:
        raise ValueError(f"{skill_root}: skill set mismatch; missing={sorted(EXPECTED_SKILLS-names)}, extra={sorted(names-EXPECTED_SKILLS)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    checks = [
        (root / "examples/project-manifest.example.json", validate_manifest),
        (root / "examples/benchmark-tasks.json", validate_benchmarks),
        (root / "examples/task-evaluation.example.json", validate_task_evaluation),
    ]
    errors = []
    for path, validator in checks:
        try:
            validator(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(str(exc))
    evidence_paths = sorted((root / "examples").glob("*evidence*.json"))
    if not evidence_paths:
        errors.append("No runtime evidence examples found")
    for path in evidence_paths:
        try:
            validate_evidence(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(str(exc))
    for label, check in (("schemas", validate_schemas), ("native Codex skills", validate_skills)):
        try:
            check(root)
            print(f"PASS {label}")
        except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("V15 contract and native-skill validation passed. No Roblox Studio runtime was executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
, front, re.MULTILINE)
    if not name or not description:
        raise ValueError(f"{path}: frontmatter requires valid name and description")
    body = content[end + 5:].strip()
    if "Mandatory current-source research gate" not in body and "V10 mandatory current-source research gate" not in body:
        raise ValueError(f"{path}: missing mandatory current-source research gate")
    if len(name.group(1)) > 64 or len(description.group(1).strip()) > 160 or len(body) < 200:
        raise ValueError(f"{path}: invalid name length or insufficient instructions")
    return name.group(1)


def validate_skills(root):
    skill_root = root / "codex-skills"
    if not skill_root.is_dir():
        raise ValueError(f"{skill_root}: missing native Codex skill source directory")
    names = set()
    for folder in sorted(p for p in skill_root.iterdir() if p.is_dir()):
        path = folder / "SKILL.md"
        if not path.is_file():
            raise ValueError(f"{folder}: missing required SKILL.md")
        name = parse_skill(path)
        if name != folder.name or name in names:
            raise ValueError(f"{path}: duplicate or folder-mismatched skill name")
        names.add(name)
    if names != EXPECTED_SKILLS:
        raise ValueError(f"{skill_root}: skill set mismatch; missing={sorted(EXPECTED_SKILLS-names)}, extra={sorted(names-EXPECTED_SKILLS)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    checks = [
        (root / "examples/project-manifest.example.json", validate_manifest),
        (root / "examples/benchmark-tasks.json", validate_benchmarks),
        (root / "examples/task-evaluation.example.json", validate_task_evaluation),
    ]
    errors = []
    for path, validator in checks:
        try:
            validator(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(str(exc))
    evidence_paths = sorted((root / "examples").glob("*evidence*.json"))
    if not evidence_paths:
        errors.append("No runtime evidence examples found")
    for path in evidence_paths:
        try:
            validate_evidence(load(path), path)
            print(f"PASS {path.relative_to(root)}")
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(str(exc))
    for label, check in (("schemas", validate_schemas), ("native Codex skills", validate_skills)):
        try:
            check(root)
            print(f"PASS {label}")
        except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("V15 contract and native-skill validation passed. No Roblox Studio runtime was executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
