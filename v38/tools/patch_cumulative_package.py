#!/usr/bin/env python3
"""Install V38 into a verified cumulative V1-V37 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V38_PRODUCTION_INCIDENT_RESPONSE -->"
GUIDANCE = """<!-- V38_PRODUCTION_INCIDENT_RESPONSE -->
## V38 production incident response
For production incidents, separate observed facts from hypotheses, assign a human incident commander, use timezone-aware chronology and aggregate-only evidence, and reassess severity as evidence changes. Keep player identifiers, chat, support records, contact details, credentials, and individual histories out of incident records. Require explicit human approval for high-risk mitigation, rollback, or restore actions; define a recovery point, stop conditions, and post-action verification before acting. Review required player notices before closure and prepare a blameless postmortem for critical/high incidents. V38's offline CLI validates supplied metadata only: it does not query Roblox services, inspect telemetry, scan for PII, authenticate evidence/approval references, execute operations, restore data, or send communications.
""".strip() + "\n"

def patch(package_root: Path, source_root: Path) -> int:
    root=package_root.expanduser().resolve(); source=source_root.expanduser().resolve()
    if not root.is_dir(): raise ValueError("Cumulative package root must exist.")
    if (source/"VERSION").read_text(encoding="utf-8").strip()!="38.0.0": raise ValueError("V38 source VERSION must be 38.0.0.")
    skills=sorted((source/"skills").glob("*/SKILL.md"))
    if len(skills)!=4: raise ValueError(f"Expected 4 V38 skills; found {len(skills)}.")
    skills_root=root/".agents"/"skills"; skills_root.mkdir(parents=True,exist_ok=True)
    count=len(list(skills_root.glob("*/SKILL.md")))
    names={x.parent.name for x in skills}
    collisions={name for name in names if (skills_root/name/"SKILL.md").is_file()}
    if count==252 and collisions: raise ValueError("V38 skill collision(s): "+", ".join(sorted(collisions)))
    if count==256 and collisions!=names: raise ValueError("Already-patched package has an incomplete V38 skill set.")
    if count not in {252,256}: raise ValueError(f"Expected 252 V37 skills or 256 already-patched skills; found {count}.")
    shutil.copytree(source,root/"v38",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".pytest_cache"))
    for skill in skills:
        target=skills_root/skill.parent.name; target.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,target/"SKILL.md")
    repository=source.parent
    old_auditor=repository/"v37"/"tools"/"audit_cumulative_package.py"
    if old_auditor.is_file():
        target=root/"v37"/"tools"/"audit_cumulative_package.py"; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(old_auditor,target)
    agents=root/"AGENTS.md"
    if not agents.is_file(): agents.write_text("# Codex project instructions\n",encoding="utf-8")
    agent_text=agents.read_text(encoding="utf-8")
    if MARKER not in agent_text: agents.write_text(agent_text.rstrip()+"\n\n"+GUIDANCE,encoding="utf-8")
    for name in ("README.md","INDEX.md","INDEX_V37.md","INDEX_V38.md","RELEASE_NOTES_V37.md","RELEASE_NOTES_V38.md"):
        item=repository/name
        if item.is_file(): shutil.copy2(item,root/name)
    final=len(list(skills_root.glob("*/SKILL.md")))
    if final!=256: raise ValueError(f"Expected 256 cumulative native skills; found {final}.")
    print(f"PASS: installed V38; cumulative native skills={final}.")
    return final

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root",required=True,type=Path)
    parser.add_argument("--source-root",required=True,type=Path)
    args=parser.parse_args()
    try: patch(args.package_root,args.source_root); return 0
    except (OSError,ValueError) as exc: print(f"ERROR: {exc}"); return 2

if __name__=="__main__": raise SystemExit(main())
