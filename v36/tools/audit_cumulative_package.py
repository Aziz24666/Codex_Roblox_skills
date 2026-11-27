#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V36 package."""
from __future__ import annotations
import argparse
from pathlib import Path
HISTORICAL_SKILL_LABELS=("207 native Codex skills","210 native Codex skills","213 native Codex skills","216 native Codex skills","220 native Codex skills","224 native Codex skills","228 native Codex skills","232 native Codex skills","236 native Codex skills","240 native Codex skills","244 native Codex skills","248 native Codex skills")
REQUIRED=("AGENTS.md","README.md","LICENSE","INDEX_V36.md","v36/VERSION","v36/INDEX_V36.md","v36/tools/v36.py","v36/tools/patch_cumulative_package.py","v36/tools/audit_cumulative_package.py","v36/tests/test_v36.py","v36/docs/ACCESSIBILITY_AND_INTERACTION_REVIEW.md","v36/docs/LOCALIZATION_AND_RESPONSIVE_UI.md","v36/docs/QUALITY_MANIFEST_AND_AUDIT.md","v36/examples/quality-manifest.example.json")
def audit(root:Path)->list[str]:
    root=root.expanduser().resolve()
    if not root.is_dir(): return ["Package root does not exist."]
    issues=[f"Missing required file: {p}" for p in REQUIRED if not (root/p).is_file()]
    skills=list((root/".agents"/"skills").glob("*/SKILL.md"))
    if len(skills)!=248: issues.append(f"Expected 248 native skills, found {len(skills)}.")
    agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
    if "<!-- V36_ACCESSIBILITY_LOCALIZATION -->" not in agents: issues.append("AGENTS.md lacks V36 guidance.")
    readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
    missing=[label for label in HISTORICAL_SKILL_LABELS if label not in readme]
    if missing: issues.append("README.md is missing cumulative compatibility labels: "+", ".join(missing)+".")
    return issues
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--root",required=True,type=Path); a=p.parse_args(); issues=audit(a.root)
    if issues:
        for x in issues: print("FAIL: "+x)
        return 1
    print("PASS: cumulative V1-V36 package audit (248 native skills)."); return 0
if __name__=="__main__": raise SystemExit(main())
