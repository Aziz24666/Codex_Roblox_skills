#!/usr/bin/env python3
"""Audit V22 inventory, inherited skill contracts, schemas, routing, and manifests."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
EXPECTED_SKILLS=196
EXPECTED_V22_SKILLS=5
CONTRACTS=("## V18 shared workflow and handoff contract","## V19 verification and evaluation contract","## V20 production reliability contract","## V21 sustainable monetization contract","## V22 platform monetization contract")
EXCLUDED={".git",".venv","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache","target","build"}
MANIFESTS={
 "SHA256SUMS.txt":{"SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V22_SHA256SUMS.txt":{"V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V21_SHA256SUMS.txt":{"V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V20_SHA256SUMS.txt":{"V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V19_SHA256SUMS.txt":{"V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V18_SHA256SUMS.txt":{"V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
 "V14_SHA256SUMS.txt":{"V14_SHA256SUMS.txt"},
}
def check_manifests(root):
    files=sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
    all_paths={p.relative_to(root).as_posix() for p in files}; counts={}
    for name,excluded in MANIFESTS.items():
        manifest=root/name
        if not manifest.is_file(): raise ValueError("Missing manifest: "+name)
        found=set()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest,rel=line.split("  ",1)
            if rel in found: raise ValueError("Duplicate checksum row: "+rel)
            found.add(rel); target=root/rel
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest: raise ValueError("Checksum mismatch: "+rel)
        expected={rel for rel in all_paths if Path(rel).name not in excluded}
        if found!=expected: raise ValueError(f"{name} coverage mismatch: missing={len(expected-found)}, extra={len(found-expected)}")
        counts[name]=len(found)
    return counts
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path(".")); root=parser.parse_args().root.resolve()
    installed=sorted((root/".agents/skills").glob("*/SKILL.md")); source=sorted((root/"v22/codex-skills").glob("*/SKILL.md"))
    if len(installed)!=EXPECTED_SKILLS: raise SystemExit(f"Expected {EXPECTED_SKILLS} installed skills, found {len(installed)}")
    if len(source)!=EXPECTED_V22_SKILLS: raise SystemExit(f"Expected five V22 source skills, found {len(source)}")
    by_name={p.parent.name:p for p in installed}
    for path in installed:
        body=path.read_text(encoding="utf-8")
        for marker in CONTRACTS:
            if marker not in body: raise SystemExit(f"Missing skill contract {marker}: {path}")
    for path in source:
        target=by_name.get(path.parent.name)
        if target is None or target.read_bytes()!=path.read_bytes(): raise SystemExit(f"V22 source/install mismatch: {path.parent.name}")
    import jsonschema
    for p in sorted((root/"v22/schemas").glob("*.schema.json")): jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))
    spec=importlib.util.spec_from_file_location("v22_audit_cli",root/"v22/tools/v22.py")
    cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
    contract=cli.validate_subscription_contract(root,Path("v22/examples/subscription-contract.example.json"))
    if contract["status"]!="PASS": raise SystemExit("Subscription contract example failed")
    benchmark=json.loads((root/"v22/data/routing-benchmark-report.json").read_text(encoding="utf-8"))
    if benchmark.get("status")!="PASS" or benchmark.get("summary",{}).get("failed_cases")!=0: raise SystemExit("V22 routing benchmark failed")
    files=sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
    if any(p.suffix in {".pyc",".pyo"} for p in files): raise SystemExit("Compiled Python bytecode found")
    checks=check_manifests(root)
    print(json.dumps({"status":"PASS","installed_skills":len(installed),"v22_skills":len(source),"schemas":len(list((root/"v22/schemas").glob("*.schema.json"))),"routing":benchmark["summary"],"manifests":checks,"files":len(files)},indent=2))
if __name__=="__main__": main()
