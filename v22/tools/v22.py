#!/usr/bin/env python3
"""V22 local pricing-readiness, subscription-contract, and routing tools."""
from __future__ import annotations
import argparse, importlib.util, json, re, subprocess, sys
from pathlib import Path

SKIP_DIRS={".git",".agents",".venv","node_modules","__pycache__",".pytest_cache","target","build","dist","v18","v19","v20","v21","v22"}
PRICE=re.compile(r"\b(?:priceInRobux|robuxPrice|passPrice|productPrice|displayPrice)\s*[:=]\s*(\d{1,8})\b",re.I)
DYNAMIC=re.compile(r"\b(?:GetProductInfoAsync|GetDeveloperProductsAsync|GetProductInfo)\s*\(")
PRICE_LEVEL=re.compile(r"\bGetUsersPriceLevelsAsync\s*\(")
SUBSCRIPTION=re.compile(r"\b(?:GetUserSubscriptionStatusAsync|GetSubscriptionProductInfoAsync|GetUserSubscriptionPaymentHistoryAsync|PromptSubscriptionPurchase)\b")

def read_json(path): return json.loads(path.read_text(encoding="utf-8"))
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def require_jsonschema():
    try: import jsonschema
    except ImportError as exc: raise RuntimeError("Install dependencies from v18/requirements-ci.txt") from exc
    return jsonschema

def audit_pricing(root):
    root=root.resolve(); findings=[]; scanned=0
    checks=[(PRICE,"HARDCODED_PRICE_LITERAL","review","A literal price assignment may become inaccurate under Managed Pricing."),
      (DYNAMIC,"DYNAMIC_PRICE_LOOKUP","info","Dynamic product-price lookup detected; verify it matches the purchase prompt."),
      (PRICE_LEVEL,"PRICE_LEVEL_API","info","Price-level API detected; review server-side gift and transfer safeguards."),
      (SUBSCRIPTION,"SUBSCRIPTION_API","info","Subscription API detected; verify server-confirmed status and lifecycle reconciliation.")]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".lua",".luau"}: continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts) or path.stat().st_size>1_000_000: continue
        if scanned>=5000: break
        scanned+=1
        try: lines=path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError,OSError): continue
        for number,line in enumerate(lines,1):
            for pattern,code,severity,message in checks:
                if pattern.search(line):
                    findings.append({"code":code,"path":path.relative_to(root).as_posix(),"line":number,"severity":severity,"evidence":line.strip()[:300],"message":message})
    summary={"files_scanned":scanned,"hard_coded_price_literals":sum(x["code"]=="HARDCODED_PRICE_LITERAL" for x in findings),
      "dynamic_price_lookup_sites":sum(x["code"]=="DYNAMIC_PRICE_LOOKUP" for x in findings),"price_level_api_sites":sum(x["code"]=="PRICE_LEVEL_API" for x in findings),
      "subscription_api_sites":sum(x["code"]=="SUBSCRIPTION_API" for x in findings)}
    return {"schema_version":1,"project_root":str(root),"summary":summary,"findings":findings,"next_steps":[
      "Review every literal-price finding; scanning cannot distinguish stale UI from intentional fixed configuration.",
      "Compare dynamic product information with the actual purchase prompt in an authorized test experience.",
      "For gifts and trades, verify current price-level safeguards on the server and test duplicate/concurrent transfers.",
      "Test subscription status, renewal, expiry, cancellation, reconciliation, and idempotent period grants.",
      "Confirm account eligibility and Managed Pricing configuration in Creator Dashboard; this scanner cannot inspect it."]}

def validate_subscription_contract(root,contract_path):
    root=root.resolve(); path=contract_path if contract_path.is_absolute() else root/contract_path
    data=read_json(path); js=require_jsonschema(); schema=read_json(root/"v22/schemas/subscription-contract.schema.json")
    errors=sorted(js.Draft202012Validator(schema,format_checker=js.FormatChecker()).iter_errors(data),key=lambda e:list(e.absolute_path))
    if errors: raise ValueError("Subscription contract schema validation failed: "+"; ".join(f"{'/'.join(map(str,e.absolute_path)) or '<root>'}: {e.message}" for e in errors[:10]))
    if len({x.strip().casefold() for x in data["benefits"]})!=len(data["benefits"]): raise ValueError("Subscription benefits contain duplicates")
    if not any(x in data["renewal_disclosure"].casefold() for x in ("renew","recurring","monthly")): raise ValueError("Renewal disclosure must explain recurring billing")
    if not any(x in data["cancellation_disclosure"].casefold() for x in ("cancel","cancellation")): raise ValueError("Cancellation disclosure must explain cancellation")
    return {"status":"PASS","product_id":data["product_id"],"benefit_count":len(data["benefits"]),"billing_cadence":data["billing_cadence"],"scope":"Static validation only; no Creator Dashboard or live subscription request was executed."}

def load_router(root):
    spec=importlib.util.spec_from_file_location("v18_router_for_v22",root/"v18/tools/v18.py")
    if spec is None or spec.loader is None: raise RuntimeError("Could not load inherited V18 router")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def evaluate_routing(root):
    root=root.resolve(); dataset=read_json(root/"v22/evals/routing-cases.json")
    if dataset.get("schema_version")!=1 or not isinstance(dataset.get("cases"),list) or not dataset["cases"]: raise ValueError("Invalid V22 routing corpus")
    router=load_router(root); seen=set(); rows=[]
    for case in dataset["cases"]:
        cid,task=case.get("id"),case.get("task")
        if not isinstance(cid,str) or not cid or cid in seen or not isinstance(task,str) or not task.strip(): raise ValueError(f"Invalid/duplicate routing case: {cid!r}")
        seen.add(cid); route=router.route_task(root,task)
        selected=set(route["selected_skills"]); domains={x["name"] for x in route["domains"]}
        missing_skills=sorted(set(case.get("required_skills",[]))-selected); missing_domains=sorted(set(case.get("required_domains",[]))-domains)
        rows.append({"id":cid,"passed":not missing_skills and not missing_domains,"missing_skills":missing_skills,"missing_domains":missing_domains,"selected_skills":route["selected_skills"],"actual_domains":sorted(domains)})
    passed=sum(x["passed"] for x in rows)
    return {"schema_version":1,"benchmark_id":dataset.get("benchmark_id","roblox-codex-v22"),"status":"PASS" if passed==len(rows) else "FAIL",
      "summary":{"total_cases":len(rows),"passed_cases":passed,"failed_cases":len(rows)-passed},"cases":rows,
      "interpretation":"Tests deterministic router selection only; it does not prove Codex reasoning, Roblox runtime correctness, platform eligibility, or earnings."}

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest="command",required=True)
    scan=sub.add_parser("audit-pricing"); scan.add_argument("--root",type=Path,default=Path(".")); scan.add_argument("--output",type=Path,default=Path("reports/v22-pricing-readiness.json"))
    val=sub.add_parser("validate-subscription-contract"); val.add_argument("--root",type=Path,default=Path(".")); val.add_argument("--file",type=Path,required=True)
    route=sub.add_parser("evaluate-routing"); route.add_argument("--root",type=Path,default=Path(".")); route.add_argument("--output",type=Path,default=Path("v22/data/routing-benchmark-report.json"))
    verify=sub.add_parser("verify"); verify.add_argument("--root",type=Path,default=Path("."))
    args=parser.parse_args()
    try:
        if args.command=="audit-pricing":
            report=audit_pricing(args.root); js=require_jsonschema(); schema=read_json(args.root.resolve()/"v22/schemas/pricing-readiness-report.schema.json")
            errors=list(js.Draft202012Validator(schema).iter_errors(report))
            if errors: raise ValueError("Generated report failed schema validation: "+"; ".join(e.message for e in errors[:5]))
            target=args.output if args.output.is_absolute() else args.root/args.output; write_json(target,report)
            print(json.dumps({"status":"PASS",**report["summary"],"output":str(target)},indent=2))
        elif args.command=="validate-subscription-contract": print(json.dumps(validate_subscription_contract(args.root,args.file),indent=2))
        elif args.command=="evaluate-routing":
            report=evaluate_routing(args.root); target=args.output if args.output.is_absolute() else args.root/args.output; write_json(target,report)
            print(json.dumps({**report["summary"],"status":report["status"],"output":str(target)},indent=2))
            if report["status"]!="PASS": return 1
        else:
            root=args.root.resolve(); validate_subscription_contract(root,Path("v22/examples/subscription-contract.example.json"))
            report=evaluate_routing(root)
            if report["status"]!="PASS": raise ValueError("V22 routing regressions failed")
            subprocess.run([sys.executable,str(root/"v22/tools/audit_cumulative_package.py"),"--root",str(root)],cwd=root,check=True)
            print("V22 verification passed.")
        return 0
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
