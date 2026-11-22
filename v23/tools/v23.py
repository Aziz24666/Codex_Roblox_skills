#!/usr/bin/env python3
"""V23 opportunity discovery, risk review, and routing evaluation."""
from __future__ import annotations
import argparse, importlib.util, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG_PATH=ROOT/"data/opportunity-catalog.json"
SCAN_EXTENSIONS={".lua",".luau",".md",".json",".toml",".yaml",".yml",".txt",".xml",".rbxmx",".rbxlx",".csv",".ini"}
SKIP_DIRS={".git",".agents",".codex",".venv","venv","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".cache","target","build","dist","coverage","reports","v15","v16","v17","v18","v19","v20","v21","v22","v23","v24","v25"}
SKIP_ROOT_FILES={"readme.md","index.md","index_v23.md","index_v24.md","index_v25.md","agents.md","package_inventory.md"}
MAX_FILES=10000
MAX_FILE_BYTES=1_000_000
PAYMENT_RE=re.compile(r"\b(?:robux|paid|purchase|developer product|promptproductpurchase|promptgamepasspurchase|currency pack|buy now)\b",re.I)
RANDOM_RE=re.compile(r"\b(?:random|rng|spin|gacha|loot\s*box|mystery|reroll|luck|odds|weighted drop|chance[- ](?:based|modifier|boost|roll))\b",re.I)
PRESSURE_RE=re.compile(r"\b(?:buy now|last chance|act fast|hurry|ends in|countdown|only \d+ left|limited time)\b",re.I)
ENGAGEMENT_RE=re.compile(r"\b(?:afk|idle farm|forced wait|artificial delay|session length|playtime gate)\b",re.I)
REWARD_RE=re.compile(r"\b(?:reward|streak|session|playtime|robux|purchase|benefit)\b",re.I)
FORCED_AD_RE=re.compile(r"\b(?:must watch|watch an ad to continue|required ad|forced ad)\b",re.I)

def read_json(path): return json.loads(path.read_text(encoding="utf-8"))
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def load_catalog(path=CATALOG_PATH):
    catalog = read_json(path)
    if not isinstance(catalog, list) or len(catalog) < 40:
        raise ValueError("The V23 opportunity catalogue must contain at least 40 entries")
    ids: set[str] = set()
    required = {
        "id", "category", "name", "monetization_route", "signals", "player_value",
        "offer_shape", "implementation_effort", "risk_level", "guardrail", "deterministic",
    }
    text_fields = (
        "id", "category", "name", "monetization_route", "player_value",
        "offer_shape", "implementation_effort", "risk_level", "guardrail",
    )
    forbidden = re.compile(
        r"\b(?:loot\s*box|gacha|paid spin|mystery purchase|paid reroll|random reward)\b",
        re.I,
    )
    for index, row in enumerate(catalog, 1):
        if not isinstance(row, dict) or not required <= set(row):
            raise ValueError(f"Opportunity catalogue entry {index} is missing required fields")
        for field in text_fields:
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"Opportunity catalogue entry {index} has invalid {field!r}")
        if row["id"] in ids:
            raise ValueError(f"Missing or duplicate opportunity id: {row['id']!r}")
        ids.add(row["id"])
        if row["deterministic"] is not True:
            raise ValueError(f"Opportunity {row['id']!r} must have a deterministic, known outcome")
        signals = row["signals"]
        if (
            not isinstance(signals, list)
            or not all(isinstance(item, str) and item.strip() for item in signals)
            or len(signals) != len(set(signals))
        ):
            raise ValueError(f"Opportunity {row['id']!r} has invalid or duplicate signals")
        if forbidden.search(row["name"] + " " + row["offer_shape"] + " " + row["monetization_route"]):
            raise ValueError("The catalogue must not recommend paid random outcomes")
        if row["implementation_effort"] not in {"low", "medium", "high"}:
            raise ValueError(f"Opportunity {row['id']!r} has an invalid implementation_effort")
        if row["risk_level"] not in {"Low", "Medium", "High"}:
            raise ValueError(f"Opportunity {row['id']!r} has an invalid risk_level")
        if "always_review" in row and not isinstance(row["always_review"], bool):
            raise ValueError(f"Opportunity {row['id']!r} has an invalid always_review flag")
    return catalog


def normalize_exclude_paths(root, exclude_paths):
    """Normalize caller-supplied scan exclusions to project-relative paths."""
    normalized = set()
    if isinstance(exclude_paths, (str, Path)):
        exclude_paths = (exclude_paths,)
    for raw_path in exclude_paths or ():
        candidate = Path(raw_path).expanduser()
        if candidate.is_absolute():
            candidate = candidate.resolve(strict=False)
            try:
                candidate = candidate.relative_to(root)
            except ValueError:
                continue
        else:
            candidate = Path(*candidate.parts)
            if any(part == ".." for part in candidate.parts):
                raise ValueError(f"Exclude path must not escape the project root: {raw_path!r}")
        if candidate == Path("."):
            raise ValueError("Exclude path cannot be the project root.")
        normalized.add(candidate)
    return normalized


def collect_project_files(root, max_files, max_file_bytes, exclude_paths=None):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not an existing directory: {root}")
    if max_files < 1 or max_file_bytes < 1:
        raise ValueError("Scan limits must be positive integers")

    excluded = normalize_exclude_paths(root, exclude_paths)
    records = []
    considered = scanned = oversized = unreadable = skipped_symlink = 0
    truncated = False
    for path in sorted(root.rglob("*")):
        try:
            relative = path.relative_to(root)
            if any(relative == item or item in relative.parents for item in excluded):
                continue
            if any(part.casefold() in SKIP_DIRS for part in relative.parts):
                continue
            if len(relative.parts) == 1 and path.name.casefold() in SKIP_ROOT_FILES:
                continue
            if path.is_symlink():
                skipped_symlink += 1
                continue
            if not path.is_file() or path.suffix.lower() not in SCAN_EXTENSIONS:
                continue
            # Resolve the full path as well: a regular-looking file below a symlinked
            # parent directory must not let a project scan escape its selected root.
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                skipped_symlink += 1
                continue
        except (OSError, RuntimeError, ValueError):
            unreadable += 1
            continue

        if considered >= max_files:
            truncated = True
            break
        considered += 1
        try:
            if resolved.stat().st_size > max_file_bytes:
                oversized += 1
                continue
            lines = resolved.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            unreadable += 1
            continue
        scanned += 1
        records.append((relative.as_posix(), lines))

    return root, records, {
        "files_considered": considered,
        "files_scanned": scanned,
        "files_skipped_oversize": oversized,
        "files_unreadable": unreadable,
        "files_skipped_symlink": skipped_symlink,
        "scan_truncated": truncated,
        "max_files": max_files,
    }


def audit_risks(records,opportunities):
    findings=[]
    source_ext={".lua",".luau",".json",".toml",".yaml",".yml",".xml",".rbxmx",".rbxlx"}
    for relative,lines in records:
        if Path(relative).suffix.lower() not in source_ext: continue
        for index,line in enumerate(lines):
            context=" ".join(lines[max(0,index-2):min(len(lines),index+3)])
            code=message=None; severity="review"
            if PAYMENT_RE.search(context) and RANDOM_RE.search(context):
                code="PAID_RANDOM_OUTCOME"; severity="blocker"
                message="Payment-related and random-outcome terms occur close together. Inspect the flow; V18 forbids paid chance outcomes and indirect Robux-funded random rewards."
            elif PRESSURE_RE.search(context) and PAYMENT_RE.search(context):
                code="PRESSURE_COPY_OR_TIMER"; message="Purchase-related text appears near urgency or countdown language. Confirm any deadline is genuine and do not pressure players."
            elif ENGAGEMENT_RE.search(context) and REWARD_RE.search(context):
                code="ARTIFICIAL_PLAYTIME_LOOP"; message="AFK, forced-wait, or session-length terms appear near rewards. Review for artificial engagement manipulation."
            elif FORCED_AD_RE.search(context):
                code="FORCED_AD_PATTERN"; message="A required-ad pattern was detected. Keep ads optional and never gate essential gameplay behind advertising."
            if code and not any(x["code"]==code and x["path"]==relative and x["line"]==index+1 for x in findings):
                findings.append({"code":code,"path":relative,"line":index+1,"severity":severity,"evidence":line.strip()[:300] or context.strip()[:300],"message":message})
            if len(findings)>=100: break
        if len(findings)>=100: break
    matched={x["id"]:x["fit_score"] for x in opportunities}
    if matched.get("private-servers",0)>0 and matched.get("robux-beta-access",0)>0:
        findings.append({"code":"ACCESS_MODEL_COLLISION","path":"<opportunity-catalogue>","line":1,"severity":"review","evidence":"Both private-server and Robux paid-access ideas match project evidence.","message":"Roblox documents these as mutually exclusive experience-level configurations. Choose one after verifying current platform settings."})
    return findings

def discover_opportunities(root, max_files=MAX_FILES, max_file_bytes=MAX_FILE_BYTES, exclude_paths=None):
    root, records, scan = collect_project_files(root, max_files, max_file_bytes, exclude_paths=exclude_paths)
    catalog=load_catalog(); opportunities=[]
    for item in catalog:
        matched=set(); evidence=[]
        for relative,lines in records:
            for number,line in enumerate(lines,1):
                lowered=line.casefold()
                for signal in item["signals"]:
                    if signal.casefold() in lowered:
                        matched.add(signal)
                        if len(evidence)<8: evidence.append({"path":relative,"line":number,"signal":signal,"excerpt":line.strip()[:240] or signal})
        matched=sorted(matched); distinct_paths=len({x["path"] for x in evidence})
        if matched:
            score=min(100,33+13*len(matched)+4*min(distinct_paths,5))
            status="evidence_supported" if len(matched)>=2 else "weak_evidence"
            priority="HIGH" if score>=78 else "MEDIUM" if score>=58 else "EXPLORE"
        elif item.get("always_review"):
            score,status,priority=25,"platform_review","PLATFORM_REVIEW"
        else: score,status,priority=0,"not_detected","NOT_DETECTED"
        row={key:item[key] for key in ("id","category","name","monetization_route","player_value","offer_shape","implementation_effort","risk_level","guardrail","deterministic")}
        row.update({"always_review":bool(item.get("always_review",False)),"fit_score":score,"status":status,"priority":priority,"matched_signals":matched,"evidence":evidence})
        opportunities.append(row)
    opportunities.sort(key=lambda x:(-x["fit_score"],x["category"],x["name"]))
    risks=audit_risks(records,opportunities)
    summary={**scan,"catalogue_options":len(opportunities),
        "evidence_supported":sum(x["status"]=="evidence_supported" for x in opportunities),
        "weak_evidence":sum(x["status"]=="weak_evidence" for x in opportunities),
        "not_detected":sum(x["status"]=="not_detected" for x in opportunities),
        "platform_review":sum(x["status"]=="platform_review" for x in opportunities),"risk_findings":len(risks)}
    steps=[
        "Review the full ranked catalogue; implement only options that match a real game feature and improve player value.",
        "Validate demand with playtests and aggregate analytics before building or pricing new products.",
        "Keep the core game enjoyable without spending and make paid benefits optional, fixed, and clearly disclosed.",
        "Keep in-experience purchases, Creator Rewards, ads, avatar/affiliate products, and Creator Store earnings as separate streams.",
        "Verify current Roblox eligibility, price behavior, and product rules in Creator Dashboard before release.",
        "Test server-authoritative receipts, exact grants, idempotency, persistence, and rejoin reconciliation for each paid product.",
        "Use aggregate retention and purchase funnel metrics; never profile or pressure individual players based on spending history."]
    if risks: steps.insert(0,"Resolve or manually clear every risk finding before shipping; paid random outcomes are hard blockers under the V18 no-gambling rule.")
    if scan["files_skipped_oversize"] or scan["files_unreadable"] or scan["scan_truncated"]: steps.append("The scan is incomplete. Narrow the project root or inspect skipped/unreadable files.")
    return {"schema_version":1,"project_root":str(root),"summary":summary,"opportunities":opportunities,"risk_findings":risks,
        "excluded_mechanics":["gambling or wagering","paid random rewards and mystery purchases","paid spins, loot boxes, and paid rerolls","paid chance, luck, odds, or random-upgrade modifiers","indirect chance paths funded by Robux-purchased currency, tickets, keys, or gems"],
        "next_steps":steps,"interpretation":"Fit scores rank code/design evidence density, not revenue, conversion probability, demand, eligibility, or guaranteed Robux. Platform-program and Creator Store routes require separate eligibility checks. This heuristic scanner does not replace human review or live testing."}

def evaluate_routing(root):
    root = Path(root).expanduser().resolve()
    dataset = read_json(root / "v23/evals/routing-cases.json")
    if (
        not isinstance(dataset, dict)
        or dataset.get("schema_version") != 1
        or not isinstance(dataset.get("cases"), list)
        or not dataset["cases"]
    ):
        raise ValueError("Invalid V23 routing corpus")
    spec = importlib.util.spec_from_file_location("v23_router", root / "v18/tools/v18.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load inherited V18 router")
    router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(router)

    seen = set()
    rows = []
    for case in dataset["cases"]:
        if not isinstance(case, dict):
            raise ValueError("Every V23 routing case must be a JSON object")
        cid, task = case.get("id"), case.get("task")
        if not isinstance(cid, str) or not cid or cid in seen or not isinstance(task, str) or not task.strip():
            raise ValueError(f"Invalid or duplicate routing case: {cid!r}")
        for key in ("required_skills", "required_domains"):
            values = case.get(key, [])
            if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
                raise ValueError(f"Routing case {cid!r} has invalid {key}")
        seen.add(cid)
        result = router.route_task(root, task)
        selected = set(result["selected_skills"])
        domains = {item["name"] for item in result["domains"]}
        missing_skills = sorted(set(case.get("required_skills", [])) - selected)
        missing_domains = sorted(set(case.get("required_domains", [])) - domains)
        rows.append({
            "id": cid,
            "passed": not missing_skills and not missing_domains,
            "missing_skills": missing_skills,
            "missing_domains": missing_domains,
            "selected_skills": result["selected_skills"],
            "actual_domains": sorted(domains),
        })
    passed = sum(item["passed"] for item in rows)
    return {
        "schema_version": 1,
        "benchmark_id": dataset.get("benchmark_id", "roblox-codex-v23"),
        "status": "PASS" if passed == len(rows) else "FAIL",
        "summary": {
            "total_cases": len(rows),
            "passed_cases": passed,
            "failed_cases": len(rows) - passed,
        },
        "cases": rows,
        "interpretation": "Tests deterministic routing only; it does not prove model reasoning, Studio behavior, platform eligibility, or earnings.",
    }


def resolve_output_path(root: Path, output: Path) -> Path:
    project_root = Path(root).expanduser().resolve()
    candidate = output if output.is_absolute() else project_root / output
    target = candidate.resolve()
    if not target.is_relative_to(project_root):
        raise ValueError("Report output must remain inside the selected project root.")
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    discover = sub.add_parser("discover-opportunities")
    discover.add_argument("--root", type=Path, default=Path("."))
    discover.add_argument("--output", type=Path, default=Path("reports/v23-opportunities.json"))
    discover.add_argument("--max-files", type=int, default=MAX_FILES)
    discover.add_argument("--max-file-bytes", type=int, default=MAX_FILE_BYTES)
    route = sub.add_parser("evaluate-routing")
    route.add_argument("--root", type=Path, default=Path("."))
    route.add_argument("--output", type=Path, default=Path("v23/data/routing-benchmark-report.json"))
    verify = sub.add_parser("verify")
    verify.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        if args.command == "discover-opportunities":
            report = discover_opportunities(args.root, max_files=args.max_files, max_file_bytes=args.max_file_bytes)
            try:
                import jsonschema
            except ImportError as exc:
                raise RuntimeError("Install CI dependencies from requirements-ci.txt") from exc
            schema = read_json(ROOT / "schemas/opportunity-discovery-report.schema.json")
            jsonschema.Draft202012Validator(schema).validate(report)
            target = resolve_output_path(args.root, args.output)
            write_json(target, report)
            print(json.dumps({"status": "PASS", **report["summary"], "output": str(target)}, indent=2))
        elif args.command == "evaluate-routing":
            report = evaluate_routing(args.root)
            target = resolve_output_path(args.root, args.output)
            write_json(target, report)
            print(json.dumps({"status": report["status"], **report["summary"], "output": str(target)}, indent=2))
            if report["status"] != "PASS":
                return 1
        else:
            if len(load_catalog()) < 40:
                raise ValueError("Opportunity catalogue is incomplete")
            report = evaluate_routing(args.root)
            if report["status"] != "PASS":
                raise ValueError("V23 routing regressions failed")
            root = Path(args.root).expanduser().resolve()
            write_json(root / "v23/data/routing-benchmark-report.json", report)
            print("V23 verification passed.")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__=="__main__": raise SystemExit(main())
