#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V32 package."""
from __future__ import annotations
import argparse
from pathlib import Path
EXPECTED_SKILLS=232
REQUIRED_FILES=(
"AGENTS.md","README.md","LICENSE","INDEX.md","INDEX_V31.md","INDEX_V32.md","tools/repository_audit.py",
"v31/VERSION","v31/tools/v31.py","v32/VERSION","v32/INDEX_V32.md","v32/tools/v32.py",
"v32/tools/patch_cumulative_package.py","v32/tools/audit_cumulative_package.py","v32/tests/test_v32.py",
"v32/docs/TEXT_FILTERING_AND_UGC.md","v32/docs/MODERATION_AND_APPEALS.md","v32/docs/PLAYER_SAFETY_BY_DESIGN.md",
"v32/schemas/moderation-policy.schema.json","v32/schemas/moderation-case.schema.json","v32/schemas/moderation-register.schema.json",
"v32/examples/moderation-policy.example.json","v32/examples/moderation-case.example.json","v32/examples/moderation-register.example.json",
".agents/skills/roblox-ugc-text-filtering-v32/SKILL.md",".agents/skills/roblox-player-report-triage-v32/SKILL.md",
".agents/skills/roblox-moderation-review-and-appeals-v32/SKILL.md",".agents/skills/roblox-player-safety-by-design-v32/SKILL.md")

def audit(root:Path)->list[str]:
    root=root.expanduser().resolve()
    if not root.is_dir(): return [f"Package root is not a directory: {root}"]
    problems=[f"Missing required file: {p}" for p in REQUIRED_FILES if not (root/p).is_file()]
    skills_root=root/".agents"/"skills"; skills=list(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills)!=EXPECTED_SKILLS: problems.append(f"Expected {EXPECTED_SKILLS} native skills, found {len(skills)}.")
    version=(root/"v32"/"VERSION").read_text(encoding="utf-8").strip() if (root/"v32"/"VERSION").is_file() else ""
    if version!="32.0.0": problems.append(f"Unexpected V32 version: {version!r}.")
    agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
    if "<!-- V32_PLAYER_SAFETY_AND_MODERATION -->" not in agents: problems.append("AGENTS.md is missing V32 player-safety and moderation instructions.")
    readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
    if "V32" not in readme or "232 native Codex skills" not in readme: problems.append("README.md does not describe the V32 cumulative package.")
    return problems

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--root",required=True,type=Path); a=p.parse_args()
    problems=audit(a.root)
    if problems:
        for item in problems: print(f"FAIL: {item}")
        return 1
    print(f"PASS: cumulative V1-V32 package audit ({EXPECTED_SKILLS} native skills)."); return 0
if __name__=="__main__": raise SystemExit(main())
