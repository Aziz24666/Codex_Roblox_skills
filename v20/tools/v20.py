#!/usr/bin/env python3
"""V20 production-contract validation and deterministic routing evaluation."""
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
            "jsonschema is required. Install with: python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt"
        ) from exc
    return jsonschema


def load_v18(root: Path):
    path = root / "v18" / "tools" / "v18.py"
    if not path.is_file():
        raise FileNotFoundError(f"V18 router not found: {path}")
    spec = importlib.util.spec_from_file_location("v18_cli_for_v20", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load V18 router: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_contract(root: Path, file_path: Path):
    root = root.resolve()
    path = file_path if file_path.is_absolute() else root / file_path
    data = read_json(path)
    jsonschema = require_jsonschema()
    schema_path = root / "v20" / "schemas" / "production-contract.schema.json"
    schema = read_json(schema_path)
    errors = sorted(
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(data),
        key=lambda item: str(list(item.absolute_path)),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(part) for part in err.absolute_path) or '<root>'}: {err.message}"
            for err in errors[:12]
        )
        raise ValueError(f"Production contract schema validation failed: {detail}")

    issues = []
    environments = data["environments"]
    for name in ("development", "staging", "canary"):
        if environments[name]["data_store_mode"] != "isolated":
            issues.append(f"{name} must use an isolated data store")
    if environments["production"]["data_store_mode"] != "production":
        issues.append("production must be explicitly marked as production data")

    remote_ids = set()
    remote_names = set()
    for remote in data["authority"]["remote_operations"]:
        operation_id = remote["operation_id"]
        remote_name = remote["remote_name"]
        if operation_id in remote_ids:
            issues.append(f"duplicate remote operation_id: {operation_id}")
        if remote_name in remote_names:
            issues.append(f"duplicate remote_name: {remote_name}")
        remote_ids.add(operation_id)
        remote_names.add(remote_name)
        if remote["side_effect"] != "none" and not remote["idempotency_key"]:
            issues.append(f"{operation_id} has a side effect but no idempotency key")

    persistence = data["persistence"]
    if persistence["retry_policy"]["max_delay_seconds"] < persistence["retry_policy"]["initial_delay_seconds"]:
        issues.append("persistence max retry delay must be at least the initial delay")
    migrations = persistence["migrations"]
    expected_from = 1
    for migration in migrations:
        source, target = migration["from_version"], migration["to_version"]
        if target != source + 1:
            issues.append(f"migration {source}->{target} is not an adjacent version step")
        if source != expected_from:
            issues.append(f"migration chain gap or reordering: expected source version {expected_from}, got {source}")
        expected_from = target
        if not migration["reversible"] and not migration.get("rollback_plan", "").strip():
            issues.append(f"irreversible migration {source}->{target} needs a forward-recovery/rollback plan")
    if migrations and expected_from != persistence["schema_version"]:
        issues.append(
            f"migration chain ends at version {expected_from}, but schema_version is {persistence['schema_version']}"
        )
    if not migrations and persistence["schema_version"] != 1:
        issues.append("schema_version greater than one requires a complete migration chain from version one")

    products = data["economy"]["products"]
    product_ids = set()
    grant_ids = set()
    for product in products:
        if product["product_id"] in product_ids:
            issues.append(f"duplicate product_id: {product['product_id']}")
        if product["grant_id"] in grant_ids:
            issues.append(f"duplicate grant_id: {product['grant_id']}")
        product_ids.add(product["product_id"])
        grant_ids.add(product["grant_id"])

    if data["rollout"]["stages"] != ["development", "staging", "canary", "production"]:
        issues.append("rollout stages must be ordered development -> staging -> canary -> production")
    required_metrics = {
        "server_errors", "remote_rejections", "data_save_failures", "transaction_failures"
    }
    missing_metrics = sorted(required_metrics - set(data["observability"]["required_metrics"]))
    if missing_metrics:
        issues.append(f"observability is missing required metrics: {', '.join(missing_metrics)}")

    if issues:
        raise ValueError("Production contract is incomplete or inconsistent: " + "; ".join(issues))
    return {
        "status": "PASS",
        "project": data["project"]["name"],
        "remote_operations": len(remote_ids),
        "migrations": len(migrations),
        "fixed_price_products": len(products),
        "rollout_stages": data["rollout"]["stages"],
        "required_metrics": len(data["observability"]["required_metrics"]),
        "scope": "Static declaration validation only; no Roblox runtime or live-service behavior was executed."
    }


def evaluate_routing(root: Path, cases_path: Path | None = None, max_specialists: int = 20):
    root = root.resolve()
    cases_path = cases_path or (root / "v20" / "evals" / "routing-cases.json")
    dataset = read_json(cases_path)
    if dataset.get("schema_version") != 1 or not isinstance(dataset.get("cases"), list):
        raise ValueError("V20 routing benchmark must use schema_version 1 and a cases array")
    if not dataset["cases"]:
        raise ValueError("V20 routing benchmark cannot be empty")

    router = load_v18(root)
    rows = []
    seen = set()
    for case in dataset["cases"]:
        case_id, task = case.get("id"), case.get("task")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"Invalid or duplicate routing case ID: {case_id!r}")
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"{case_id}: task must be non-empty")
        seen.add(case_id)
        route = router.route_task(root, task, max_specialists=max_specialists)
        selected = set(route["selected_skills"])
        domains = {item["name"] for item in route["domains"]}
        required_skills = set(case.get("required_skills", []))
        required_domains = set(case.get("required_domains", []))
        forbidden = set(case.get("forbidden_skills", []))
        missing_skills = sorted(required_skills - selected)
        missing_domains = sorted(required_domains - domains)
        forbidden_selected = sorted(forbidden & selected)
        passed = not (missing_skills or missing_domains or forbidden_selected)
        rows.append({
            "id": case_id,
            "passed": passed,
            "missing_skills": missing_skills,
            "missing_domains": missing_domains,
            "forbidden_selected": forbidden_selected,
            "selected_skills": route["selected_skills"],
            "actual_domains": sorted(domains)
        })
    passed = sum(1 for row in rows if row["passed"])
    return {
        "schema_version": 1,
        "benchmark_id": dataset.get("benchmark_id", "roblox-codex-v20"),
        "status": "PASS" if passed == len(rows) else "FAIL",
        "summary": {"total_cases": len(rows), "passed_cases": passed, "failed_cases": len(rows) - passed},
        "cases": rows,
        "interpretation": (
            "This evaluates deterministic V18 router selection only. It does not measure LLM reasoning, "
            "implementation quality, Roblox runtime correctness, or production readiness."
        )
    }


def verify(root: Path):
    commands = [
        [sys.executable, "v19/tools/v19.py", "verify", "--root", str(root)],
    ]
    for index, command in enumerate(commands, 1):
        print(f"[{index}/{len(commands)}] {' '.join(command)}")
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    benchmark_path = root / "v20" / "data" / "routing-benchmark-report.json"
    report = evaluate_routing(root)
    write_json(benchmark_path, report)
    if report["status"] != "PASS":
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1
    contract = validate_contract(root, Path("v20/examples/production-contract.example.json"))
    print(json.dumps(contract, indent=2))
    audit = subprocess.run(
        [sys.executable, "v20/tools/audit_cumulative_package.py", "--root", str(root)],
        cwd=root, check=False
    )
    if audit.returncode:
        return audit.returncode
    print("V20 cumulative verification passed. Runtime/live-service checks remain environment-specific.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    benchmark = sub.add_parser("evaluate-routing")
    benchmark.add_argument("--root", type=Path, default=Path("."))
    benchmark.add_argument("--max-specialists", type=int, default=20)
    benchmark.add_argument("--output", type=Path)
    contract = sub.add_parser("validate-contract")
    contract.add_argument("--root", type=Path, default=Path("."))
    contract.add_argument("--file", required=True)
    check = sub.add_parser("verify")
    check.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "evaluate-routing":
            if not 1 <= args.max_specialists <= 20:
                raise ValueError("--max-specialists must be between 1 and 20")
            report = evaluate_routing(root, max_specialists=args.max_specialists)
            if args.output:
                target = args.output if args.output.is_absolute() else root / args.output
                write_json(target, report)
                print(f"Wrote {target}")
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["status"] == "PASS" else 1
        if args.command == "validate-contract":
            print(json.dumps(validate_contract(root, Path(args.file)), indent=2, ensure_ascii=False))
            return 0
        if args.command == "verify":
            return verify(root)
    except Exception as exc:
        print(f"V20 {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
