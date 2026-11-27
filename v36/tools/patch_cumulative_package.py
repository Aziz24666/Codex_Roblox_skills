#!/usr/bin/env python3
"""Install V36 into a verified cumulative V1-V35 package."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path
MARKER="<!-- V36_ACCESSIBILITY_LOCALIZATION -->"
RULES="""
<!-- V36_ACCESSIBILITY_LOCALIZATION -->
## V36 accessibility, responsive UI, and localization review
Inventory player-facing surfaces and review input navigation, readable text, non-color cues, contrast, critical-audio alternatives, reduced motion, localization, text expansion, and RTL behavior. Use the V36 offline manifest validator and audit to track review gaps. These checks do not inspect Studio instances, screenshots, runtime behavior, or certify accessibility; verify on actual target devices. Do not collect or store player health information or infer disabilities. Preserve all V1-V35 security, privacy, safety, moderation, transparent monetization, fixed paid outcomes, and no-gambling safeguards.
""".strip()+"\n"

def patch(package_root:Path,source_root:Path|None=None)->int:
    root=package_root.expanduser().resolve()
    source=(source_root or Path(__file__).resolve().parents[1]).resolve()
    if not root.is_dir(): raise ValueError("Cumulative package root must exist.")
    if (source/"VERSION").read_text(encoding="utf-8").strip()!="36.0.0": raise ValueError("V36 VERSION must be 36.0.0.")
    skills=sorted((source/"skills").glob("*/SKILL.md"))
    if len(skills)!=4: raise ValueError(f"Expected exactly 4 V36 skills, found {len(skills)}.")
    target=root/".agents"/"skills"; target.mkdir(parents=True,exist_ok=True)
    count=len(list(target.glob("*/SKILL.md")))
    if count not in {244,248}: raise ValueError(f"Expected 244 pre-V36 skills or 248 already-patched skills, found {count}.")
    names={x.parent.name for x in skills}
    collisions={n for n in names if (target/n/"SKILL.md").is_file()}
    if count==244 and collisions: raise ValueError("V36 skill path collision: "+", ".join(sorted(collisions)))
    if count==248 and collisions!=names: raise ValueError("Incomplete V36 skill set in package.")
    shutil.copytree(source,root/"v36",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    for skill in skills:
        dest=target/skill.parent.name; dest.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,dest/"SKILL.md")
    agents=root/"AGENTS.md"
    if not agents.is_file(): raise ValueError("Cumulative package is missing AGENTS.md.")
    content=agents.read_text(encoding="utf-8")
    if MARKER not in content: agents.write_text(content.rstrip()+"\n\n"+RULES,encoding="utf-8")
    for name in ("README.md","INDEX.md","INDEX_V35.md","INDEX_V36.md","RELEASE_NOTES_V36.md"):
        src=source.parent/name
        if src.is_file(): shutil.copy2(src,root/name)
    count=len(list(target.glob("*/SKILL.md")))
    if count!=248: raise ValueError(f"Expected 248 skills after V36 patch, found {count}.")
    print(f"PASS: installed V36; cumulative native skills={count}.")
    return count

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--package-root",required=True,type=Path); p.add_argument("--source-root",type=Path); a=p.parse_args(); patch(a.package_root,a.source_root); return 0
if __name__=="__main__": raise SystemExit(main())
