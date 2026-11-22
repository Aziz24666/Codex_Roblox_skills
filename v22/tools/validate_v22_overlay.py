#!/usr/bin/env python3
"""Validate V22 skill metadata, schemas, routing, and example contracts."""
from __future__ import annotations
import importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V22=ROOT/"v22"
EXPECTED={"roblox-creator-rewards-and-healthy-engagement","roblox-managed-pricing-and-regional-readiness","roblox-subscription-lifecycle-and-entitlement-operations","roblox-platform-revenue-portfolio-and-creator-economics","roblox-monetization-launch-and-policy-readiness"}
def fail(message): raise SystemExit("V22 overlay validation failed: "+message)
def main():
    version=(V22/"VERSION").read_text().strip()
    if not re.fullmatch(r"22\.\d+\.\d+",version): fail("invalid version")
    paths=sorted((V22/"codex-skills").glob("*/SKILL.md"))
    if len(paths)!=5: fail(f"expected five skills, found {len(paths)}")
    names=set()
    for path in paths:
        lines=path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0]!="---": fail(f"{path}: missing frontmatter")
        try: end=lines.index("---",1)
        except ValueError: fail(f"{path}: unterminated frontmatter")
        meta={}
        for line in lines[1:end]:
            key,sep,value=line.partition(":")
            if not sep: fail(f"{path}: malformed frontmatter")
            meta[key.strip()]=value.strip()
        name,desc=meta.get("name",""),meta.get("description","")
        if name!=path.parent.name or name in names or not desc or len(desc)>160: fail(f"{path}: invalid frontmatter")
        body="\n".join(lines[end+1:]).casefold()
        if "shared contracts" not in body or "no-gambling" not in body: fail(f"{path}: missing inherited safety contract")
        names.add(name)
    if names!=EXPECTED: fail("specialist inventory mismatch")
    import jsonschema
    for p in (V22/"schemas").glob("*.schema.json"): jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text()))
    additions=json.loads((V22/"workflow/routing-additions.json").read_text())
    routed={skill for group in additions["additions"].values() for skill in group.get("skills",[])}
    if not EXPECTED<=routed: fail("routing additions omit specialist skills")
    base=json.loads((ROOT/"v18/workflow/skill-routing.json").read_text())
    if set(additions["additions"])-set(base["domains"]): fail("unknown routing domain")
    cases=json.loads((V22/"evals/routing-cases.json").read_text()); ids=[x.get("id") for x in cases.get("cases",[])]
    if cases.get("schema_version")!=1 or len(ids)<5 or len(ids)!=len(set(ids)): fail("need five unique routing cases")
    spec=importlib.util.spec_from_file_location("v22_cli_overlay",V22/"tools/v22.py"); cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
    result=cli.validate_subscription_contract(ROOT,Path("v22/examples/subscription-contract.example.json"))
    if result["status"]!="PASS": fail("example subscription contract failed")
    print("V22 overlay validation passed: five skills, five cases, two schemas, subscription example PASS")
if __name__=="__main__": main()
