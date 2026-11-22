#!/usr/bin/env python3
"""Validate V23 metadata, opportunity catalogue, routing, and schema."""
from __future__ import annotations
import importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V23=ROOT/"v23"
EXPECTED={"roblox-monetization-opportunity-discovery","roblox-value-led-engagement-design","roblox-store-product-discovery-and-conversion","roblox-revenue-analytics-and-experimentation","roblox-monetization-growth-compliance"}
def fail(message): raise SystemExit("V23 overlay validation failed: "+message)
def main():
    version=(V23/"VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"23\.\d+\.\d+",version): fail("invalid version")
    paths=sorted((V23/"codex-skills").glob("*/SKILL.md"))
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
        if "shared contracts" not in body or "no-gambling" not in body: fail(f"{path}: missing inherited no-gambling contract")
        names.add(name)
    if names!=EXPECTED: fail("specialist inventory mismatch")
    import jsonschema
    schema=json.loads((V23/"schemas/opportunity-discovery-report.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    spec=importlib.util.spec_from_file_location("v23_cli_overlay",V23/"tools/v23.py")
    cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
    if len(cli.load_catalog())<40: fail("opportunity catalogue must contain at least 40 entries")
    additions=json.loads((V23/"workflow/routing-additions.json").read_text(encoding="utf-8"))
    routed={skill for group in additions["additions"].values() for skill in group.get("skills",[])}
    if not EXPECTED<=routed: fail("routing additions omit V23 specialist skills")
    base=json.loads((ROOT/"v18/workflow/skill-routing.json").read_text(encoding="utf-8"))
    if set(additions["additions"])-set(base["domains"]): fail("unknown routing domain")
    cases=json.loads((V23/"evals/routing-cases.json").read_text(encoding="utf-8"))
    ids=[x.get("id") for x in cases.get("cases",[])]
    if cases.get("schema_version")!=1 or len(ids)<5 or len(ids)!=len(set(ids)): fail("need five unique routing cases")
    print(f"V23 overlay validation passed: {len(paths)} skills, {len(cli.load_catalog())} opportunities, {len(ids)} routing cases")
if __name__=="__main__": main()
