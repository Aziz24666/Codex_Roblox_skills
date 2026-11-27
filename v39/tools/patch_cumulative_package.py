#!/usr/bin/env python3
"""Install V39 into a verified cumulative V1-V38 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER="<!-- V39_DETERMINISTIC_ECONOMY_PROGRESSION -->"
GUIDANCE="""<!-- V39_DETERMINISTIC_ECONOMY_PROGRESSION -->
## V39 deterministic economy and progression modeling
Use V39 for transparent gameplay currency source/sink inventories, deterministic progression thresholds, and bounded synthetic scenario comparisons. Keep all model inputs explicit, integer-based, and versioned. Treat cohorts as synthetic activity archetypes only; never import player IDs, account history, chat, purchases, or individual profiles. Recheck server authority, idempotent rewards, retry/concurrency behavior, and affordability in actual implementation reviews. V39 does not query Roblox telemetry, estimate revenue/retention, run Studio, or prove live balance. Do not add paid random outcomes, loot boxes, wagering, or gambling mechanics.
""".strip()+"\n"

def patch(package_root:Path,source_root:Path)->int:
    root=package_root.expanduser().resolve(); source=source_root.expanduser().resolve(); repository=source.parent
    if not root.is_dir(): raise ValueError("Cumulative package root must exist.")
    if (source/"VERSION").read_text(encoding="utf-8").strip()!="39.0.0": raise ValueError("V39 source VERSION must be 39.0.0.")
    skills=sorted((source/"skills").glob("*/SKILL.md"))
    if len(skills)!=4: raise ValueError(f"Expected four V39 skills; found {len(skills)}.")
    skills_root=root/".agents"/"skills"; skills_root.mkdir(parents=True,exist_ok=True)
    count=len(list(skills_root.glob("*/SKILL.md"))); names={x.parent.name for x in skills}
    collisions={name for name in names if (skills_root/name/"SKILL.md").is_file()}
    if count==256 and collisions: raise ValueError("V39 skill collision(s): "+", ".join(sorted(collisions)))
    if count==260 and collisions!=names: raise ValueError("Already-patched V39 package has an incomplete skill set.")
    if count not in {256,260}: raise ValueError(f"Expected 256 V38 skills or 260 already-patched skills; found {count}.")
    shutil.copytree(source,root/"v39",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".pytest_cache"))
    for skill in skills:
        target=skills_root/skill.parent.name; target.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,target/"SKILL.md")
    for version in ("v37","v38"):
        auditor=repository/version/"tools"/"audit_cumulative_package.py"
        if auditor.is_file():
            target=root/version/"tools"/"audit_cumulative_package.py"; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(auditor,target)
    agents=root/"AGENTS.md"
    if not agents.is_file(): agents.write_text("# Codex project instructions\n",encoding="utf-8")
    text=agents.read_text(encoding="utf-8")
    if MARKER not in text: agents.write_text(text.rstrip()+"\n\n"+GUIDANCE,encoding="utf-8")
    for name in ("README.md","INDEX.md","INDEX_V37.md","INDEX_V38.md","INDEX_V39.md","RELEASE_NOTES_V37.md","RELEASE_NOTES_V38.md","RELEASE_NOTES_V39.md"):
        candidate=repository/name
        if candidate.is_file(): shutil.copy2(candidate,root/name)
    total=len(list(skills_root.glob("*/SKILL.md")))
    if total!=260: raise ValueError(f"Expected 260 cumulative native Codex skills; found {total}.")
    print(f"PASS: installed V39; cumulative native skills={total}.")
    return total

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root",required=True,type=Path)
    parser.add_argument("--source-root",required=True,type=Path)
    args=parser.parse_args()
    try: patch(args.package_root,args.source_root); return 0
    except (OSError,ValueError) as exc: print(f"ERROR: {exc}"); return 2

if __name__=="__main__": raise SystemExit(main())
