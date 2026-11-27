#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V39 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS={260,264,268,272}
HISTORICAL=("207 native Codex skills","210 native Codex skills","213 native Codex skills","216 native Codex skills","220 native Codex skills","224 native Codex skills","228 native Codex skills","232 native Codex skills","236 native Codex skills","240 native Codex skills","244 native Codex skills","248 native Codex skills","252 native Codex skills","256 native Codex skills","260 native Codex skills","264 native Codex skills","268 native Codex skills","272 native Codex skills")
REQUIRED=(
 "AGENTS.md","README.md","LICENSE","INDEX.md","INDEX_V37.md","INDEX_V38.md","INDEX_V39.md",
 "v37/VERSION","v37/tools/v37.py","v37/tools/audit_cumulative_package.py",
 "v38/VERSION","v38/tools/v38.py","v38/tools/audit_cumulative_package.py",
 "v39/VERSION","v39/INDEX_V39.md","v39/tools/v39.py","v39/tools/patch_cumulative_package.py","v39/tools/audit_cumulative_package.py",
 "v39/tests/test_v39.py","v39/schemas/economy-model.schema.json","v39/examples/economy-model.example.json",
 "v39/docs/ECONOMY_MODEL_DESIGN.md","v39/docs/INTERPRETING_SIMULATION_RESULTS.md","v39/docs/ECONOMY_CLI.md",
 ".agents/skills/roblox-economy-source-and-sink-architecture/SKILL.md",
 ".agents/skills/roblox-deterministic-economy-simulation/SKILL.md",
 ".agents/skills/roblox-progression-pacing-and-reward-curves/SKILL.md",
 ".agents/skills/roblox-economy-fairness-and-abuse-review/SKILL.md",
)

def audit(root:Path)->list[str]:
    root=root.expanduser().resolve()
    if not root.is_dir(): return ["Package root is not a directory."]
    issues=[f"Missing required file: {p}" for p in REQUIRED if not (root/p).is_file()]
    skill_root=root/".agents"/"skills"; skills=list(skill_root.glob("*/SKILL.md")) if skill_root.is_dir() else []
    if len(skills) not in EXPECTED_SKILLS: issues.append(f"Expected V39/V40-compatible native skill count {sorted(EXPECTED_SKILLS)}; found {len(skills)}.")
    version=(root/"v39"/"VERSION").read_text(encoding="utf-8").strip() if (root/"v39"/"VERSION").is_file() else ""
    if version!="39.0.0": issues.append(f"Unexpected V39 version: {version!r}.")
    readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
    if not any(x in readme for x in ("Current release: V39.0.0","Current release: V40.0.0","Current release: V41.0.0","Current release: V42.0.0")) or not any(x in readme for x in ("260 native Codex skills","264 native Codex skills","268 native Codex skills","272 native Codex skills")): issues.append("README does not describe a V39/V40 cumulative package.")
    missing=[label for label in HISTORICAL if label not in readme]
    if missing: issues.append("README is missing historical skill totals: "+", ".join(missing)+".")
    agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
    if "<!-- V39_DETERMINISTIC_ECONOMY_PROGRESSION -->" not in agents: issues.append("AGENTS.md is missing V39 economy/progression guidance.")
    return issues

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--root",required=True,type=Path); args=parser.parse_args()
    issues=audit(args.root)
    if issues:
        for issue in issues: print("FAIL: "+issue)
        return 1
    print(f"PASS: V39 compatibility audit ({len(list((args.root.expanduser().resolve() / ".agents" / "skills").glob("*/SKILL.md")))} native skills)."); return 0

if __name__=="__main__": raise SystemExit(main())
