#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V38 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS=256
HISTORICAL=("207 native Codex skills","210 native Codex skills","213 native Codex skills","216 native Codex skills","220 native Codex skills","224 native Codex skills","228 native Codex skills","232 native Codex skills","236 native Codex skills","240 native Codex skills","244 native Codex skills","248 native Codex skills","252 native Codex skills","256 native Codex skills")
REQUIRED=(
 "AGENTS.md","README.md","LICENSE","INDEX.md","INDEX_V37.md","INDEX_V38.md",
 "v37/VERSION","v37/tools/v37.py","v37/tools/audit_cumulative_package.py",
 "v38/VERSION","v38/INDEX_V38.md","v38/tools/v38.py","v38/tools/patch_cumulative_package.py",
 "v38/tools/audit_cumulative_package.py","v38/tests/test_v38.py","v38/schemas/incident.schema.json",
 "v38/examples/incident.example.json","v38/docs/INCIDENT_TRIAGE_AND_SERVICE_HEALTH.md",
 "v38/docs/MITIGATION_APPROVAL_AND_ROLLBACK.md","v38/docs/COMMUNICATION_AND_POSTMORTEM.md","v38/docs/INCIDENT_CLI.md",
 ".agents/skills/roblox-production-incident-triage-and-severity-assessment/SKILL.md",
 ".agents/skills/roblox-privacy-safe-service-health-and-impact-analysis/SKILL.md",
 ".agents/skills/roblox-safe-mitigation-approval-and-recovery/SKILL.md",
 ".agents/skills/roblox-player-communications-and-postmortem-readiness/SKILL.md",
)

def audit(root: Path) -> list[str]:
    root=root.expanduser().resolve()
    if not root.is_dir(): return ["Package root is not a directory."]
    issues=[f"Missing required file: {p}" for p in REQUIRED if not (root/p).is_file()]
    skill_root=root/".agents"/"skills"; skills=list(skill_root.glob("*/SKILL.md")) if skill_root.is_dir() else []
    if len(skills)!=EXPECTED_SKILLS: issues.append(f"Expected {EXPECTED_SKILLS} native skills; found {len(skills)}.")
    version=(root/"v38"/"VERSION").read_text(encoding="utf-8").strip() if (root/"v38"/"VERSION").is_file() else ""
    if version!="38.0.0": issues.append(f"Unexpected V38 version: {version!r}.")
    readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
    if "Current release: V38.0.0" not in readme or "256 native Codex skills" not in readme: issues.append("README does not describe V38 and 256 skills.")
    missing=[x for x in HISTORICAL if x not in readme]
    if missing: issues.append("README is missing historical skill totals: "+", ".join(missing)+".")
    agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
    if "<!-- V38_PRODUCTION_INCIDENT_RESPONSE -->" not in agents: issues.append("AGENTS.md is missing V38 incident-response guidance.")
    return issues

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--root",required=True,type=Path); args=parser.parse_args()
    issues=audit(args.root)
    if issues:
        for issue in issues: print("FAIL: "+issue)
        return 1
    print(f"PASS: cumulative V1-V38 package audit ({EXPECTED_SKILLS} native skills)."); return 0

if __name__=="__main__": raise SystemExit(main())
