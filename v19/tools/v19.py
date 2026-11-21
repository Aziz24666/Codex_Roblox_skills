#!/usr/bin/env python3
"""V19 deterministic routing evaluation, test-plan generation, and evidence validation."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def require_jsonschema():
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError(
            "jsonschema is required for V19 schema validation. Install with: "
            "python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt"
        ) from exc
    return jsonschema


def load_v18(root: Path):
    path = root / "v18" / "tools" / "v18.py"
    if not path.is_file():
        raise FileNotFoundError(f"V18 router not found: {path}")
    spec = importlib.util.spec_from_file_location("v18_cli_for_v19", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load V18 router: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_routing(root: Path, cases_path: Path | None = None, max_specialists: int = 20):
    root = root.resolve()
    cases_path = cases_path or (root / "v19" / "evals" / "routing-cases.json")
    dataset = read_json(cases_path)
    if dataset.get("schema_version") != 1 or not isinstance(dataset.get("cases"), list):
        raise ValueError("Routing benchmark must use schema_version 1 and a cases array")
    if not dataset["cases"]:
        raise ValueError("Routing benchmark cannot be empty")

    router = load_v18(root)
    rows = []
    seen_ids = set()
    for case in dataset["cases"]:
        case_id = case.get("id")
        task = case.get("task")
        if not isinstance(case_id, str) or not case_id or case_id in seen_ids:
            raise ValueError(f"Invalid or duplicate routing case ID: {case_id!r}")
        seen_ids.add(case_id)
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"{case_id}: task must be a non-empty string")
        required_domains = set(case.get("required_domains", []))
        required_skills = set(case.get("required_skills", []))
        forbidden_skills = set(case.get("forbidden_skills", []))
        route = router.route_task(root, task, max_specialists=max_specialists)
        selected = set(route["selected_skills"])
        actual_domains = {row["name"] for row in route["domains"]}
        missing_domains = sorted(required_domains - actual_domains)
        missing_skills = sorted(required_skills - selected)
        forbidden_selected = sorted(forbidden_skills & selected)
        passed = not (missing_domains or missing_skills or forbidden_selected)
        rows.append({
            "id": case_id,
            "passed": passed,
            "required_domains": sorted(required_domains),
            "actual_domains": sorted(actual_domains),
            "missing_domains": missing_domains,
            "required_skills": sorted(required_skills),
            "selected_skills": route["selected_skills"],
            "missing_skills": missing_skills,
            "forbidden_skills": sorted(forbidden_skills),
            "forbidden_selected": forbidden_selected,
        })

    passed = sum(1 for row in rows if row["passed"])
    total = len(rows)
    return {
        "schema_version": 1,
        "benchmark_id": dataset.get("benchmark_id", "unnamed"),
        "max_specialists": max_specialists,
        "status": "PASS" if passed == total else "FAIL",
        "summary": {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": total - passed,
            "pass_rate": round(passed / total, 4),
        },
        "cases": rows,
        "interpretation": (
            "This evaluates deterministic route_task behavior only. It does not measure "
            "LLM reasoning, skill compliance, generated-code quality, or runtime correctness."
        ),
    }


def build_test_plan(root: Path, task: str, changed_paths: list[str] | None = None):
    if not task.strip():
        raise ValueError("Task cannot be empty")
    normalized = []
    for raw in changed_paths or []:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Changed paths must be safe project-relative paths: {raw}")
        normalized.append(path.as_posix())
    normalized = sorted(set(normalized))

    router = load_v18(root.resolve())
    route = router.route_task(root, task, max_specialists=20)
    domains = {item["name"] for item in route["domains"]}
    lowered = task.lower()
    code_changed = any(Path(p).suffix.lower() in {".luau", ".lua"} for p in normalized)
    code_changed = code_changed or any(
        token in lowered for token in ("script", "module", "luau", "code", "implement", "refactor")
    )
    checks = []

    def add(check_id, category, reason, tool_hints, evidence_required):
        if any(item["check_id"] == check_id for item in checks):
            return
        checks.append({
            "check_id": check_id,
            "category": category,
            "status": "NOT_RUN",
            "reason": reason,
            "tool_hints": tool_hints,
            "evidence_required": evidence_required,
        })

    add(
        "scope-and-diff-review", "review",
        "Confirm the changed paths, project source of truth, ownership boundaries, and acceptance criteria.",
        ["git diff", "project guidance", "work-item.json"],
        "Reviewed diff, affected-system map, and acceptance-criteria mapping.",
    )
    if code_changed:
        add(
            "luau-static-analysis", "static",
            "Luau source or code behavior is in scope; use the project's configured analyzer and lint rules.",
            ["luau-analyze", "Selene", "StyLua check mode"],
            "Exact analyzer/linter commands, versions, findings, and output logs.",
        )
        add(
            "targeted-unit-tests", "unit",
            "Changed code needs focused deterministic tests for local logic and boundary conditions.",
            ["project test harness", "TestEZ if already adopted", "existing unit-test command"],
            "Executed test command, test names, result summary, and log artifact.",
        )
    if domains & {"multiplayer", "security"} or any(x in lowered for x in ("remote", "replication", "client-server", "network")):
        add(
            "server-boundary-security", "security",
            "The task touches client input, remotes, authority, replication, or trust boundaries.",
            ["server-side validation tests", "remote contract tests"],
            "Cases for malformed input, ownership, distance/context, rate limits, and duplicate/replay behavior.",
        )
        add(
            "multi-client-studio", "multiplayer",
            "Networking and player lifecycle claims require more than a single-client or static check.",
            ["StudioTestService", "Roblox Studio testing modes", "Studio MCP when connected"],
            "Studio version, place/build identity, client count, scenario results, and logs.",
        )
    if "persistence" in domains or any(x in lowered for x in ("datastore", "save data", "profile migration")):
        add(
            "isolated-persistence-integration", "persistence",
            "Player data changes need isolated fixture coverage for load, save, retries, and recovery.",
            ["isolated test place", "test-only DataStore configuration", "migration fixtures"],
            "Fixture identity, schema versions, simulated failures, observed state, and recovery logs.",
        )
    if "economy" in domains or any(x in lowered for x in ("purchase", "currency", "developer product", "game pass")):
        add(
            "economy-transaction-integrity", "economy",
            "Currency or purchase changes require exact grants, idempotency, and replay protection.",
            ["deterministic transaction tests", "test-only purchase fixtures"],
            "Transaction IDs, expected/actual balances, duplicate-delivery results, and test fixture details.",
        )
    if "ui" in domains or any(x in lowered for x in ("mobile", "touch", "gamepad", "controller", "accessibility")):
        add(
            "cross-platform-input-matrix", "device",
            "UI or input changes must be checked on each affected input mode and layout class.",
            ["keyboard and mouse", "touch", "gamepad", "supported device matrix"],
            "Device/input configuration, screenshots or recordings, and interaction outcomes.",
        )
    if "character" in domains:
        add(
            "character-lifecycle-studio", "studio",
            "Character and avatar changes need engine-level spawn, respawn, rig, and animation checks.",
            ["Roblox Studio playtest", "R6/R15 test fixtures"],
            "Rig variants, spawn/respawn scenarios, observed behavior, and Studio output.",
        )
    if "performance" in domains or any(x in lowered for x in ("lag", "frame rate", "memory", "profile")):
        add(
            "performance-baseline-comparison", "performance",
            "Performance changes require comparable measurements on named client/server environments.",
            ["MicroProfiler", "Developer Console", "Performance Stats", "network simulation"],
            "Before/after captures, device/server configuration, frame/memory/network observations.",
        )
    if domains & {"character", "ui", "npc", "world", "assets", "multiplayer"} and code_changed:
        add(
            "studio-runtime-scenario", "studio",
            "Player-visible or engine-dependent behavior requires a real Studio runtime scenario.",
            ["Roblox Studio Test mode", "Studio MCP if connected"],
            "Studio version, place/build identity, exact scenario, observed behavior, and output artifact.",
        )
    if "release" in domains or any(x in lowered for x in ("publish", "deploy", "release", "package")):
        add(
            "reproducible-release-check", "release",
            "Release work must preserve package identity, checksum integrity, approval, and rollback boundaries.",
            ["CI workflow", "archive integrity tools", "SHA-256"],
            "Workflow run, commit/tag, archive checksums, approval record, and rollback reference.",
        )

    return {
        "schema_version": 1,
        "task": task,
        "changed_paths": normalized,
        "selected_skills": route["selected_skills"],
        "domains": sorted(domains),
        "checks": checks,
        "execution_note": (
            "Planning only: every check is NOT_RUN. This command does not execute Luau tools, "
            "Roblox Studio, multiplayer sessions, device tests, or live services."
        ),
    }


def validate_test_plan(root: Path, plan: dict):
    jsonschema = require_jsonschema()
    schema = read_json(root / "v19" / "schemas" / "test-plan.schema.json")
    jsonschema.Draft202012Validator(schema).validate(plan)
    return True


def validate_evidence(root: Path, file_path: Path):
    root = root.resolve()
    path = file_path if file_path.is_absolute() else root / file_path
    data = read_json(path)
    jsonschema = require_jsonschema()
    schema = read_json(root / "v19" / "schemas" / "verification-evidence.schema.json")
    jsonschema.Draft202012Validator(schema).validate(data)

    for check in data["checks"]:
        status = check["status"]
        if status in {"PASS", "FAIL"}:
            for field in ("environment", "tool_version", "command", "expected", "actual"):
                if not check[field].strip():
                    raise ValueError(f"{check['check_id']}: {status} requires non-empty {field}")
            if not data.get("build_identity", "").strip():
                raise ValueError(f"{check['check_id']}: {status} requires a build_identity")
            if not check["evidence_paths"]:
                raise ValueError(f"{check['check_id']}: {status} requires at least one evidence artifact")
        elif status in {"BLOCKED", "NOT_RUN", "NOT_APPLICABLE"} and not check["limitations"]:
            raise ValueError(f"{check['check_id']}: {status} requires a limitation or reason")

        for raw in check["evidence_paths"]:
            artifact = Path(raw)
            if artifact.is_absolute() or ".." in artifact.parts:
                raise ValueError(f"{check['check_id']}: evidence path escapes project root: {raw}")
            resolved = (root / artifact).resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise ValueError(f"{check['check_id']}: evidence path escapes project root: {raw}") from exc
            if not resolved.is_file() or resolved.stat().st_size <= 0:
                raise ValueError(f"{check['check_id']}: evidence artifact is missing or empty: {raw}")
    return {
        "status": "PASS",
        "work_item_id": data["work_item_id"],
        "checks": len(data["checks"]),
        "executed_checks": sum(1 for c in data["checks"] if c["status"] in {"PASS", "FAIL"}),
        "limitations": sum(1 for c in data["checks"] if c["status"] in {"BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}),
    }


def verify(root: Path):
    commands = [
        [sys.executable, "v18/tools/v18.py", "validate", "--root", str(root)],
        [sys.executable, "v19/tools/v19.py", "evaluate-routing", "--root", str(root),
         "--output", str(root / "v19/data/routing-benchmark-report.json")],
        [sys.executable, "v19/tools/audit_cumulative_package.py", "--root", str(root)],
        [sys.executable, "v18/tools/audit_cumulative_package.py", "--root", str(root)],
        [sys.executable, "v17/tools/audit_cumulative_package.py", "--root", str(root)],
    ]
    for index, command in enumerate(commands, 1):
        print(f"[{index}/{len(commands)}] {' '.join(command)}")
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    print("V19 cumulative verification passed.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    benchmark = sub.add_parser("evaluate-routing")
    benchmark.add_argument("--root", type=Path, default=Path("."))
    benchmark.add_argument("--max-specialists", type=int, default=20)
    benchmark.add_argument("--output", type=Path)

    plan = sub.add_parser("plan-tests")
    plan.add_argument("--root", type=Path, default=Path("."))
    plan.add_argument("--task", required=True)
    plan.add_argument("--changed", nargs="*", default=[])
    plan.add_argument("--output", type=Path)

    evidence = sub.add_parser("validate-evidence")
    evidence.add_argument("--root", type=Path, default=Path("."))
    evidence.add_argument("--file", required=True)

    check = sub.add_parser("verify")
    check.add_argument("--root", type=Path, default=Path("."))

    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "evaluate-routing":
            if not 1 <= args.max_specialists <= 20:
                raise ValueError("--max-specialists must be between 1 and 20")
            result = evaluate_routing(root, max_specialists=args.max_specialists)
            if args.output:
                target = args.output if args.output.is_absolute() else root / args.output
                write_json(target, result)
                print(f"Wrote {target}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["status"] == "PASS" else 1
        if args.command == "plan-tests":
            result = build_test_plan(root, args.task, args.changed)
            validate_test_plan(root, result)
            if args.output:
                target = args.output if args.output.is_absolute() else root / args.output
                write_json(target, result)
                print(f"Wrote {target}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if args.command == "validate-evidence":
            result = validate_evidence(root, args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if args.command == "verify":
            return verify(root)
    except Exception as exc:
        print(f"V19 {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
