#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V35 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS=244
REQUIRED_FILES=(
 "AGENTS.md","README.md","LICENSE","INDEX.md","INDEX_V31.md","INDEX_V32.md","INDEX_V33.md","INDEX_V34.md","INDEX_V35.md","tools/repository_audit.py",
 "v31/VERSION","v31/tools/v31.py","v32/VERSION","v32/INDEX_V32.md","v32/tools/v32.py","v33/VERSION","v33/INDEX_V33.md","v33/tools/v33.py",
 "v34/VERSION","v34/INDEX_V34.md","v34/tools/v34.py","v34/tools/patch_cumulative_package.py","v34/tools/audit_cumulative_package.py","v34/tests/test_v34.py",
 "v34/docs/PERFORMANCE_SOAK_TESTING.md","v34/docs/MICROPROFILER_AND_DASHBOARD_EVIDENCE.md","v34/docs/REPEATED_BENCHMARKS_AND_ROLLOUT.md",
 "v34/schemas/soak-capture.schema.json","v34/schemas/repeat-suite.schema.json","v34/examples/soak-capture.example.json","v34/examples/repeat-suite.example.json",
 "v35/VERSION","v35/INDEX_V35.md","v35/tools/v35.py","v35/tools/patch_cumulative_package.py","v35/tools/audit_cumulative_package.py","v35/tests/test_v35.py",
 "v35/docs/ASSET_CATALOG_AND_PROVENANCE.md","v35/docs/CONTENT_BUDGETS_AND_DEPENDENCIES.md","v35/docs/ASSET_RELEASE_AND_MIGRATION.md",
 "v35/schemas/asset-catalog.schema.json","v35/schemas/asset-budget-policy.schema.json","v35/examples/asset-catalog.example.json","v35/examples/asset-budget-policy.example.json",
 ".agents/skills/roblox-asset-catalog-and-dependency-governance-v35/SKILL.md",".agents/skills/roblox-asset-provenance-and-rights-review-v35/SKILL.md",
 ".agents/skills/roblox-device-aware-content-budgets-v35/SKILL.md",".agents/skills/roblox-asset-release-and-migration-v35/SKILL.md",
)

def audit(root:Path)->list[str]:
    root=root.expanduser().resolve()
    if not root.is_dir(): return [f"Package root is not a directory: {root}"]
    problems=[f"Missing required file: {item}" for item in REQUIRED_FILES if not (root/item).is_file()]
    skills_root=root/".agents"/"skills"; skills=sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills)!=EXPECTED_SKILLS: problems.append(f"Expected {EXPECTED_SKILLS} native skills, found {len(skills)}.")
    version=(root/"v35"/"VERSION").read_text(encoding="utf-8").strip() if (root/"v35"/"VERSION").is_file() else ""
    if version!="35.0.0": problems.append(f"Unexpected V35 version: {version!r}.")
    agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
    if "<!-- V35_ASSET_PIPELINE_GOVERNANCE -->" not in agents: problems.append("AGENTS.md is missing V35 asset pipeline governance instructions.")
    readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
    if "V35" not in readme or "244 native Codex skills" not in readme: problems.append("README.md does not describe the V35 cumulative package.")
    return problems

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--root",required=True,type=Path); args=parser.parse_args()
    problems=audit(args.root)
    if problems:
        for item in problems: print("FAIL: "+item)
        return 1
    print(f"PASS: cumulative V1-V35 package audit ({EXPECTED_SKILLS} native skills)."); return 0
if __name__=="__main__": raise SystemExit(main())
