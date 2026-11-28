#!/usr/bin/env python3
"""Audit reconstructed cumulative V1-V45 package."""
from __future__ import annotations
import argparse
from pathlib import Path
EXPECTED=284
HISTORICAL=tuple(f"{n} native Codex skills" for n in (207,210,213,216,220,224,228,232,236,240,244,248,252,256,260,264,268,272,276,280,284))
REQUIRED=("AGENTS.md","README.md","LICENSE","INDEX.md","INDEX_V37.md","INDEX_V38.md","INDEX_V39.md","INDEX_V40.md","INDEX_V41.md","INDEX_V42.md","INDEX_V43.md","INDEX_V44.md","INDEX_V45.md","tools/repository_audit.py",
"v37/VERSION","v37/tools/v37.py","v37/tools/audit_cumulative_package.py","v38/VERSION","v38/tools/v38.py","v38/tools/audit_cumulative_package.py",
"v39/VERSION","v39/tools/v39.py","v39/tools/audit_cumulative_package.py","v40/VERSION","v40/tools/v40.py","v40/tools/audit_cumulative_package.py",
"v41/VERSION","v41/tools/v41.py","v41/tools/audit_cumulative_package.py","v42/VERSION","v42/tools/v42.py","v42/tools/audit_cumulative_package.py",
"v43/VERSION","v43/tools/v43.py","v43/tools/audit_cumulative_package.py","v44/VERSION","v44/tools/v44.py","v44/tools/audit_cumulative_package.py",
"v45/VERSION","v45/INDEX_V45.md","v45/tools/v45.py","v45/tools/patch_cumulative_package.py","v45/tools/audit_cumulative_package.py",
"v45/tests/test_v45.py","v45/tests/requirements-test.txt","v45/schemas/narrative-project.schema.json","v45/examples/narrative-project.example.json",
"v45/docs/QUEST_GRAPH_ARCHITECTURE.md","v45/docs/BRANCHING_DIALOGUE_DESIGN.md","v45/docs/QUEST_PERSISTENCE_AND_CONTENT_MIGRATION.md","v45/docs/NARRATIVE_CONTENT_QA.md","v45/docs/V45_CLI.md",
".agents/skills/roblox-quest-graph-and-objective-architecture/SKILL.md",".agents/skills/roblox-branching-dialogue-and-choice-design/SKILL.md",
".agents/skills/roblox-quest-state-and-dialogue-integration/SKILL.md",".agents/skills/roblox-narrative-content-qa-and-localization/SKILL.md")
def audit(root:Path)->list[str]:
 root=root.expanduser().resolve()
 if not root.is_dir(): return ["Package root is not a directory."]
 issues=[f"Missing required file: {p}" for p in REQUIRED if not (root/p).is_file()]
 skills=list((root/".agents"/"skills").glob("*/SKILL.md"))
 if len(skills)!=EXPECTED: issues.append(f"Expected {EXPECTED} native skills; found {len(skills)}.")
 version=(root/"v45"/"VERSION").read_text(encoding="utf-8").strip() if (root/"v45"/"VERSION").is_file() else ""
 if version!="45.0.0": issues.append(f"Unexpected V45 version: {version!r}.")
 readme=(root/"README.md").read_text(encoding="utf-8") if (root/"README.md").is_file() else ""
 if "Current release: V45.0.0" not in readme or "284 native Codex skills" not in readme: issues.append("README does not describe published V45.0.0 and 284 skills.")
 missing=[x for x in HISTORICAL if x not in readme]
 if missing: issues.append("README is missing historical skill totals: "+", ".join(missing)+".")
 agents=(root/"AGENTS.md").read_text(encoding="utf-8") if (root/"AGENTS.md").is_file() else ""
 if "<!-- V45_QUEST_DIALOGUE_NARRATIVE_SYSTEMS -->" not in agents: issues.append("AGENTS.md is missing V45 quest/dialogue guidance.")
 return issues
def main()->int:
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("--root",required=True,type=Path); a=p.parse_args(); issues=audit(a.root)
 if issues:
  for item in issues: print("FAIL: "+item)
  return 1
 print("PASS: cumulative V1-V45 package audit (284 native skills)."); return 0
if __name__=="__main__": raise SystemExit(main())
