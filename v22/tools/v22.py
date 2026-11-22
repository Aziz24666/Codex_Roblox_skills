#!/usr/bin/env python3
"""V22 local pricing-readiness, subscription-contract, and routing tools."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", ".agents", ".venv", "node_modules", "__pycache__", ".pytest_cache",
    "target", "build", "dist", "v18", "v19", "v20", "v21", "v22",
}
MAX_FILES = 5000
MAX_FILE_BYTES = 1_000_000

PRICE_LITERAL = re.compile(
    r"\b(?:priceInRobux|robuxPrice|passPrice|productPrice|displayPrice)\s*[:=]\s*(\d{1,8})\b",
    re.IGNORECASE,
)
DYNAMIC_PRICE = re.compile(r"\b(?:GetProductInfoAsync|GetDeveloperProductsAsync)\s*\(")
LEGACY_PRODUCT_INFO = re.compile(r"\bGetProductInfo\s*\(")
PRICE_LEVEL = re.compile(r"\bGetUsersPriceLevelsAsync\s*\(")
SUBSCRIPTION_API = re.compile(
    r"\b(?:GetUserSubscriptionStatusAsync|GetSubscriptionProductInfoAsync|"
    r"GetUserSubscriptionPaymentHistoryAsync|PromptSubscriptionPurchase)\b"
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def require_jsonschema():
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("Install dependencies from v18/requirements-ci.txt") from exc
    return jsonschema


def audit_pricing(root: Path):
    """Scan Luau source heuristically and report incomplete inputs explicitly."""
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not an existing directory: {root}")

    findings = []
    files_considered = 0
    files_scanned = 0
    files_skipped_oversize = 0
    files_unreadable = 0
    scan_truncated = False

    checks = [
        (PRICE_LITERAL, "HARDCODED_PRICE_LITERAL", "review",
         "A literal price assignment may become inaccurate under Managed Pricing."),
        (DYNAMIC_PRICE, "DYNAMIC_PRICE_LOOKUP", "info",
         "A supported dynamic product-price lookup was detected; verify it matches the purchase prompt."),
        (LEGACY_PRODUCT_INFO, "LEGACY_PRODUCT_INFO_API", "review",
         "GetProductInfo is deprecated; review migration to GetProductInfoAsync."),
        (PRICE_LEVEL, "PRICE_LEVEL_API", "info",
         "Price-level API detected; review server-side gift and transfer safeguards."),
        (SUBSCRIPTION_API, "SUBSCRIPTION_API", "info",
         "Subscription API detected; verify server-confirmed status and lifecycle reconciliation."),
    ]

    for path in sorted(root.rglob("*")):
        try:
            if not path.is_file() or path.suffix.lower() not in {".lua", ".luau"}:
                continue
            relative = path.relative_to(root)
        except (OSError, ValueError):
            files_unreadable += 1
            continue

        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if files_considered >= MAX_FILES:
            scan_truncated = True
            break
        files_considered += 1

        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                files_skipped_oversize += 1
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            files_unreadable += 1
            continue

        files_scanned += 1
        for line_number, line in enumerate(lines, 1):
            for pattern, code, severity, message in checks:
                if pattern.search(line):
                    findings.append({
                        "code": code,
                        "path": relative.as_posix(),
                        "line": line_number,
                        "severity": severity,
                        "evidence": line.strip()[:300],
                        "message": message,
                    })

    summary = {
        "files_considered": files_considered,
        "files_scanned": files_scanned,
        "files_skipped_oversize": files_skipped_oversize,
        "files_unreadable": files_unreadable,
        "scan_truncated": scan_truncated,
        "max_files": MAX_FILES,
        "hard_coded_price_literals": sum(x["code"] == "HARDCODED_PRICE_LITERAL" for x in findings),
        "dynamic_price_lookup_sites": sum(x["code"] == "DYNAMIC_PRICE_LOOKUP" for x in findings),
        "legacy_product_info_sites": sum(x["code"] == "LEGACY_PRODUCT_INFO_API" for x in findings),
        "price_level_api_sites": sum(x["code"] == "PRICE_LEVEL_API" for x in findings),
        "subscription_api_sites": sum(x["code"] == "SUBSCRIPTION_API" for x in findings),
    }

    next_steps = [
        "Review every literal-price finding; scanning cannot distinguish stale UI from intentional fixed configuration.",
        "Compare dynamic product information with the actual purchase prompt in an authorized test experience.",
        "Migrate deprecated GetProductInfo calls to GetProductInfoAsync where appropriate.",
        "For gifts and trades, verify current price-level safeguards on the server and test duplicate/concurrent transfers.",
        "Test subscription status, renewal, expiry, cancellation, reconciliation, and idempotent period grants.",
        "Confirm account eligibility and Managed Pricing configuration in Creator Dashboard; this scanner cannot inspect it.",
        "Treat this report as a heuristic source scan, not proof of runtime behavior or pricing compliance.",
    ]
    if files_skipped_oversize:
        next_steps.append(
            f"{files_skipped_oversize} source file(s) exceeded the {MAX_FILE_BYTES}-byte scan limit and were not inspected."
        )
    if files_unreadable:
        next_steps.append(
            f"{files_unreadable} candidate source file(s) could not be read; investigate them before treating the scan as complete."
        )
    if scan_truncated:
        next_steps.append(
            f"The scan stopped at {MAX_FILES} candidate source files; use a narrower root or raise the reviewed limit."
        )

    return {
        "schema_version": 1,
        "project_root": str(root),
        "summary": summary,
        "findings": findings,
        "next_steps": next_steps,
    }


def validate_subscription_contract(root: Path, contract_path: Path):
    root = Path(root).resolve()
    path = contract_path if contract_path.is_absolute() else root / contract_path
    data = read_json(path)
    jsonschema = require_jsonschema()
    schema = read_json(root / "v22/schemas/subscription-contract.schema.json")
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors[:10]
        )
        raise ValueError(f"Subscription contract schema validation failed: {detail}")

    if len({item.strip().casefold() for item in data["benefits"]}) != len(data["benefits"]):
        raise ValueError("Subscription benefits contain duplicates")
    key = data["period_grant_key"].casefold()
    if "product_id" not in key or "billing_period_id" not in key:
        raise ValueError(
            "period_grant_key must include both product_id and billing_period_id "
            "to define a stable per-product, per-billing-period grant key"
        )
    if not any(token in data["renewal_disclosure"].casefold()
               for token in ("renew", "recurring", "monthly")):
        raise ValueError("Renewal disclosure must explain recurring billing")
    if not any(token in data["cancellation_disclosure"].casefold()
               for token in ("cancel", "cancellation")):
        raise ValueError("Cancellation disclosure must explain cancellation")

    return {
        "status": "PASS",
        "product_id": data["product_id"],
        "benefit_count": len(data["benefits"]),
        "billing_cadence": data["billing_cadence"],
        "scope": "Static declaration validation only; no Creator Dashboard or live subscription request was executed.",
    }


def load_router(root: Path):
    spec = importlib.util.spec_from_file_location("v18_router_for_v22", root / "v18/tools/v18.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load inherited V18 router")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_routing(root: Path):
    root = Path(root).resolve()
    dataset = read_json(root / "v22/evals/routing-cases.json")
    if dataset.get("schema_version") != 1 or not isinstance(dataset.get("cases"), list) or not dataset["cases"]:
        raise ValueError("Invalid V22 routing corpus")

    router = load_router(root)
    seen = set()
    rows = []
    for case in dataset["cases"]:
        case_id, task = case.get("id"), case.get("task")
        if (not isinstance(case_id, str) or not case_id or case_id in seen
                or not isinstance(task, str) or not task.strip()):
            raise ValueError(f"Invalid/duplicate routing case: {case_id!r}")
        seen.add(case_id)
        route = router.route_task(root, task)
        selected = set(route["selected_skills"])
        domains = {item["name"] for item in route["domains"]}
        missing_skills = sorted(set(case.get("required_skills", [])) - selected)
        missing_domains = sorted(set(case.get("required_domains", [])) - domains)
        rows.append({
            "id": case_id,
            "passed": not missing_skills and not missing_domains,
            "missing_skills": missing_skills,
            "missing_domains": missing_domains,
            "selected_skills": route["selected_skills"],
            "actual_domains": sorted(domains),
        })

    passed = sum(item["passed"] for item in rows)
    return {
        "schema_version": 1,
        "benchmark_id": dataset.get("benchmark_id", "roblox-codex-v22"),
        "status": "PASS" if passed == len(rows) else "FAIL",
        "summary": {"total_cases": len(rows), "passed_cases": passed, "failed_cases": len(rows) - passed},
        "cases": rows,
        "interpretation": "Tests deterministic router selection only; it does not prove Codex reasoning, Roblox runtime correctness, platform eligibility, or earnings.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("audit-pricing")
    scan.add_argument("--root", type=Path, default=Path("."))
    scan.add_argument("--output", type=Path, default=Path("reports/v22-pricing-readiness.json"))
    validate = subparsers.add_parser("validate-subscription-contract")
    validate.add_argument("--root", type=Path, default=Path("."))
    validate.add_argument("--file", type=Path, required=True)
    route = subparsers.add_parser("evaluate-routing")
    route.add_argument("--root", type=Path, default=Path("."))
    route.add_argument("--output", type=Path, default=Path("v22/data/routing-benchmark-report.json"))
    verify = subparsers.add_parser("verify")
    verify.add_argument("--root", type=Path, default=Path("."))

    args = parser.parse_args()
    try:
        if args.command == "audit-pricing":
            report = audit_pricing(args.root)
            jsonschema = require_jsonschema()
            schema = read_json(args.root.resolve() / "v22/schemas/pricing-readiness-report.schema.json")
            errors = list(jsonschema.Draft202012Validator(schema).iter_errors(report))
            if errors:
                raise ValueError("Generated report failed schema validation: "
                                 + "; ".join(error.message for error in errors[:5]))
            target = args.output if args.output.is_absolute() else args.root / args.output
            write_json(target, report)
            print(json.dumps({"status": "PASS", **report["summary"], "output": str(target)}, indent=2))
        elif args.command == "validate-subscription-contract":
            print(json.dumps(validate_subscription_contract(args.root, args.file), indent=2))
        elif args.command == "evaluate-routing":
            report = evaluate_routing(args.root)
            target = args.output if args.output.is_absolute() else args.root / args.output
            write_json(target, report)
            print(json.dumps({
                **report["summary"],
                "status": report["status"],
                "output": str(target),
                "failed_cases": [
                    {"id": row["id"], "missing_skills": row["missing_skills"], "missing_domains": row["missing_domains"]}
                    for row in report["cases"] if not row["passed"]
                ],
            }, indent=2))
            if report["status"] != "PASS":
                return 1
        else:
            root = args.root.resolve()
            validate_subscription_contract(root, Path("v22/examples/subscription-contract.example.json"))
            report = evaluate_routing(root)
            if report["status"] != "PASS":
                raise ValueError("V22 routing regressions failed")
            subprocess.run(
                [sys.executable, str(root / "v22/tools/audit_cumulative_package.py"), "--root", str(root)],
                cwd=root, check=True,
            )
            print("V22 verification passed.")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
