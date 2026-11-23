#!/usr/bin/env python3
"""Install V32 player-safety and moderation checks into a cumulative V1-V31 package."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path
MARKER="<!-- V32_PLAYER_SAFETY_AND_MODERATION -->"
RULES="""
<!-- V32_PLAYER_SAFETY_AND_MODERATION -->
## V32 player safety and user-generated content

Filter all player-generated text that can be seen by other players. Use Roblox TextService from a server Script for custom non-chat text; if filtering fails, do not show the submitted text. Prefer native TextChatService for chat and never attempt to extract platform-integrated chat message contents. Treat source scans as leads, not proof that every displayed value is filtered. Keep moderation decisions human-reviewed, policy-based, consistent, and appealable. Keep reporter/target identities, raw chat, voice content, and original evidence inside authorized Roblox moderation systems; V32 case files accept only predefined codes and opaque references. Never automatically sanction a player from report counts, static code findings, or unverified heuristics. Review high-impact cases with a second authorized reviewer, publish clear rules, and preserve a fair appeal path. Use minimum necessary evidence and a project-owned retention schedule. Keep V1-V31 safeguards, including server authority, privacy-safe aggregate analytics, fixed paid outcomes, fair free progression, and the mandatory no-gambling policy.
""".strip()+"\n"

def patch(package_root:Path,source_root:Path|None=None)->int:
    package_root=package_root.expanduser().resolve()
    if not package_root.is_dir(): raise ValueError(f"Package root does not exist: {package_root}")
    source_root=(source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root/"VERSION").is_file() or not (source_root/"tools"/"v32.py").is_file(): raise ValueError(f"V32 source directory is incomplete: {source_root}")
    skills=sorted((source_root/"skills").glob("*/SKILL.md"))
    if len(skills)!=4: raise ValueError(f"Expected 4 V32 skills, found {len(skills)}.")
    target=package_root/".agents"/"skills"; target.mkdir(parents=True,exist_ok=True)
    existing=len(list(target.glob("*/SKILL.md")))
    if existing not in {228,232}: raise ValueError(f"Expected 228 pre-V32 skills or an already-patched 232-skill package, found {existing}.")
    names={p.parent.name for p in skills}; collisions={n for n in names if (target/n/"SKILL.md").is_file()}
    if existing==228 and collisions: raise ValueError("V32 skill name collision(s): "+", ".join(sorted(collisions)))
    if existing==232 and collisions!=names: raise ValueError("The 232-skill package does not contain the complete V32 skill set.")
    shutil.copytree(source_root,package_root/"v32",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".pytest_cache"))
    for skill in skills:
        dest=target/skill.parent.name; dest.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,dest/"SKILL.md")
    agents=package_root/"AGENTS.md"
    if not agents.is_file(): raise ValueError("Cumulative package is missing AGENTS.md.")
    text=agents.read_text(encoding="utf-8")
    if MARKER not in text: agents.write_text(text.rstrip()+"\n\n"+RULES,encoding="utf-8")
    repo=source_root.parent
    for name in ("README.md","INDEX.md","INDEX_V31.md","INDEX_V32.md","RELEASE_NOTES_V31.md","RELEASE_NOTES_V32.md"):
        src=repo/name
        if src.is_file(): shutil.copy2(src,package_root/name)
    audit=repo/"tools"/"repository_audit.py"
    if audit.is_file():
        dest=package_root/"tools"/audit.name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(audit,dest)
    workflow=repo/".github"/"workflows"/"v32-quality.yml"
    if workflow.is_file():
        dest=package_root/".github"/"workflows"; dest.mkdir(parents=True,exist_ok=True); shutil.copy2(workflow,dest/workflow.name)
    count=len(list(target.glob("*/SKILL.md")))
    if count!=232: raise ValueError(f"V32 package must contain 232 native skills after patching; found {count}.")
    print(f"Installed V32 into {package_root}; cumulative skill count is {count}.")
    return count

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--package-root",required=True,type=Path); p.add_argument("--source-root",type=Path)
    a=p.parse_args(); patch(a.package_root,a.source_root); return 0
if __name__=="__main__": raise SystemExit(main())
