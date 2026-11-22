#!/usr/bin/env python3
"""Audit V23 inventory, inherited skill contracts, opportunity catalogue, and manifests."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path

EXPECTED_SKILLS=201
V23_SKILLS={"roblox-monetization-opportunity-discovery","roblox-value-led-engagement-design","roblox-store-product-discovery-and-conversion","roblox-revenue-analytics-and-experimentation","roblox-monetization-growth-compliance"}
OLD_CONTRACTS=("## V18 shared workflow and handoff contract","## V19 verification and evaluation contract","## V20 production reliability contract","## V21 sustainable monetization contract","## V22 platform monetization contract")
V23_CONTRACT="## V23 value-led monetization and opportunity coverage contract"
EXCLUDED={".git",".venv","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache","target","build"}
MANIFESTS={
"SHA256SUMS.txt":{"SHA256SUMS.txt","V23_SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V23_SHA256SUMS.txt":{"V23_SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V22_SHA256SUMS.txt":{"V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V21_SHA256SUMS.txt":{"V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V20_SHA256SUMS.txt":{"V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V19_SHA256SUMS.txt":{"V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V18_SHA256SUMS.txt":{"V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
"V14_SHA256SUMS.txt":{"V14_SHA256SUMS.txt"}}

def check_manifests(root):
    files=sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
    all_paths={p.relative_to(root).as_posix() for p in files}; counts={}
    for name,excluded in MANIFESTS.items():
        manifest=root/name
        if not manifest.is_file(): raise ValueError("Missing manifest: "+name)
        found=set()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest,relative=line.split("  ",1)
            if relative in found: raise ValueError("Duplicate checksum row: "+relative)
            found.add(relative); target=root/relative
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest: raise ValueError("Checksum mismatch: "+relative)
        expected={p for p in all_paths if Path(p).name not in excluded}
        if found!=expected: raise ValueError(f"{name} coverage mismatch: missing={len(expected-found)}, extra={len(found-expected)}")
        counts[name]=len(found)
    return counts

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path(".")); root=parser.parse_args().root.resolve()
    installed=sorted((root/".agents/skills").glob("*/SKILL.md")); source=sorted((root/"v23/codex-skills").glob("*/SKILL.md"))
    if len(installed)!=EXPECTED_SKILLS: raise SystemExit(f"Expected {EXPECTED_SKILLS} installed skills, found {len(installed)}")
    if len(source)!=5: raise SystemExit("Expected five V23 source skills")
    by_name={p.parent.name:p for p in installed}
    for path in installed:
        body=path.read_text(encoding="utf-8")
        if V23_CONTRACT not in body: raise SystemExit(f"Missing V23 contract: {path}")
        if path.parent.name in V23_SKILLS:
            if "shared contracts" not in body.casefold() or "V18 no-gambling" not in body: raise SystemExit(f"Missing inherited safety contract: {path}")
        else:
            for marker in OLD_CONTRACTS:
                if marker not in body: raise SystemExit(f"Missing inherited contract {marker}: {path}")
    for path in source:
        target=by_name.get(path.parent.name)
        if target is None or target.read_bytes()!=path.read_bytes(): raise SystemExit("V23 source/install mismatch: "+path.parent.name)
    import jsonschema
    schemas=sorted((root/"v23/schemas").glob("*.schema.json"))
    for path in schemas: jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
    spec=importlib.util.spec_from_file_location("v23_audit_cli",root/"v23/tools/v23.py")
    cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
    catalog=cli.load_catalog(root/"v23/data/opportunity-catalog.json")
    if len(catalog)<40: raise SystemExit("V23 opportunity catalogue is incomplete")
    benchmark=json.loads((root/"v23/data/routing-benchmark-report.json").read_text(encoding="utf-8"))
    if benchmark.get("status")!="PASS" or benchmark.get("summary",{}).get("failed_cases")!=0: raise SystemExit("V23 routing benchmark failed")
    oldspec=importlib.util.spec_from_file_location("v22_audit_cli",root/"v22/tools/v22.py")
    old=importlib.util.module_from_spec(oldspec); oldspec.loader.exec_module(old)
    if old.validate_subscription_contract(root,Path("v22/examples/subscription-contract.example.json"))["status"]!="PASS": raise SystemExit("Inherited V22 subscription contract failed")
    files=sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
    if any(p.suffix in {".pyc",".pyo"} for p in files): raise SystemExit("Compiled Python bytecode found")
    checks=check_manifests(root)
    print(json.dumps({"status":"PASS","installed_skills":len(installed),"v23_skills":len(source),"catalogue_options":len(catalog),"schemas":len(schemas),"routing":benchmark["summary"],"manifests":checks,"files":len(files)},indent=2))
if __name__=="__main__": main()
