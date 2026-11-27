#!/usr/bin/env python3
"""Install the V35 asset-pipeline governance layer into a cumulative V1-V34 package."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path

MARKER="<!-- V35_ASSET_PIPELINE_GOVERNANCE -->"
RULES="""
<!-- V35_ASSET_PIPELINE_GOVERNANCE -->
## V35 asset pipeline governance and content validation

Maintain a project-owned asset catalog with stable internal keys, content kind, source/provenance evidence, ownership scope, rights-review state, moderation-review state, lifecycle, version, dependencies, target profiles, and measured metadata. Keep evidence in authorized project storage and reference it only through opaque IDs. The V35 CLI validates supplied catalog metadata and its dependency graph, checks user-recorded measurements against local source files when available, evaluates explicit per-device budgets, and compares catalog revisions for removals or provenance/review regressions. It does not infer copyright or Creator Store permissions, query Roblox asset services, inspect binary files, transfer ownership, publish assets, delete assets, or modify live experiences. Treat rights and moderation status as human-maintained assertions requiring evidence and reviewer approval. Do not commit credentials, private access tokens, private asset URLs, personal data, or arbitrary free-form notes into catalogs. Use V30 release approvals for rollout decisions. Preserve all V1-V34 security, privacy, player-safety, human-moderation, fair/transparent monetization, fixed paid outcomes, and mandatory no-gambling safeguards.
""".strip()+"\n"

def patch(package_root:Path,source_root:Path|None=None)->int:
    package_root=package_root.expanduser().resolve()
    if not package_root.is_dir(): raise ValueError(f"Package root does not exist: {package_root}")
    source_root=(source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root/"VERSION").is_file() or not (source_root/"tools"/"v35.py").is_file(): raise ValueError(f"V35 source directory is incomplete: {source_root}")
    if (source_root/"VERSION").read_text(encoding="utf-8").strip()!="35.0.0": raise ValueError("V35 source VERSION must be 35.0.0.")
    skills=sorted((source_root/"skills").glob("*/SKILL.md"))
    if len(skills)!=4: raise ValueError(f"Expected exactly 4 V35 skills, found {len(skills)}.")
    names=set()
    for skill in skills:
        content=skill.read_text(encoding="utf-8"); parts=content.split("---",2)
        if not content.startswith("---\n") or len(parts)!=3 or "name:" not in parts[1] or "description:" not in parts[1]: raise ValueError(f"Skill metadata is missing or malformed: {skill}")
        name=next((line.split(":",1)[1].strip() for line in parts[1].splitlines() if line.startswith("name:")),"")
        if not name or name in names: raise ValueError(f"Skill names must be present and unique: {skill}")
        names.add(name)
    target=package_root/".agents"/"skills"; target.mkdir(parents=True,exist_ok=True)
    existing=len(list(target.glob("*/SKILL.md")))
    if existing not in {240,244}: raise ValueError(f"Expected 240 pre-V35 skills or an already-patched 244-skill package, found {existing}.")
    expected={skill.parent.name for skill in skills}
    collisions={name for name in expected if (target/name/"SKILL.md").is_file()}
    if existing==240 and collisions: raise ValueError("V35 skill name collision(s): "+", ".join(sorted(collisions)))
    if existing==244 and collisions!=expected: raise ValueError("The 244-skill package does not contain the complete V35 skill set.")
    shutil.copytree(source_root,package_root/"v35",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".pytest_cache"))
    for skill in skills:
        destination=target/skill.parent.name; destination.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,destination/"SKILL.md")
    agents=package_root/"AGENTS.md"
    if not agents.is_file(): raise ValueError("Cumulative package is missing AGENTS.md.")
    text=agents.read_text(encoding="utf-8")
    if MARKER not in text: agents.write_text(text.rstrip()+"\n\n"+RULES,encoding="utf-8")
    repo=source_root.parent
    for name in ("README.md","INDEX.md","INDEX_V31.md","INDEX_V32.md","INDEX_V33.md","INDEX_V34.md","INDEX_V35.md","RELEASE_NOTES_V31.md","RELEASE_NOTES_V32.md","RELEASE_NOTES_V33.md","RELEASE_NOTES_V34.md","RELEASE_NOTES_V35.md"):
        source=repo/name
        if source.is_file(): shutil.copy2(source,package_root/name)
    audit=repo/"tools"/"repository_audit.py"
    if audit.is_file():
        destination=package_root/"tools"/audit.name; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(audit,destination)
    workflows=package_root/".github"/"workflows"; workflows.mkdir(parents=True,exist_ok=True)
    for name in ("v34-quality.yml","v35-quality.yml"):
        source=repo/".github"/"workflows"/name
        if source.is_file(): shutil.copy2(source,workflows/name)
    count=len(list(target.glob("*/SKILL.md")))
    if count!=244: raise ValueError(f"V35 package must contain 244 native skills after patching; found {count}.")
    print(f"Installed V35 into {package_root}; cumulative skill count is {count}.")
    return count

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--package-root",required=True,type=Path); parser.add_argument("--source-root",type=Path); args=parser.parse_args()
    patch(args.package_root,args.source_root); return 0
if __name__=="__main__": raise SystemExit(main())
