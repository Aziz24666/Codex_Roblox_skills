#!/usr/bin/env python3
"""Install V45 into a verified cumulative V1-V44 package."""
from __future__ import annotations
import argparse,shutil
from pathlib import Path
MARKER="<!-- V45_QUEST_DIALOGUE_NARRATIVE_SYSTEMS -->"
GUIDANCE="""<!-- V45_QUEST_DIALOGUE_NARRATIVE_SYSTEMS -->
## V45 quest, dialogue, and narrative systems
Author quests and conversations as version-controlled graphs with stable IDs. Quest progression and prerequisite graphs must be acyclic; all quest nodes must be reachable and have a completion path. Dialogue loops are allowed only when every node still has a route to an ending. Keep authored definitions separate from player progress. Persist stable IDs rather than display text or array positions and explicitly migrate renamed/removed IDs. The server owns completion, dialogue choice availability, story flags, and durable side effects; clients submit intent only. Use idempotent transitions and V40 profile/reward patterns. V45 validates local metadata only: it does not inspect Luau, contact Roblox, execute migrations, verify localization, moderate content, or run Studio. Human review and real device playtests are required.
""".strip()+"\n"
def patch(package_root:Path,source_root:Path)->int:
 root=package_root.expanduser().resolve(); source=source_root.expanduser().resolve(); repo=source.parent
 if not root.is_dir(): raise ValueError("Cumulative package root must exist.")
 if not (source/"VERSION").is_file() or (source/"VERSION").read_text(encoding="utf-8").strip()!="45.0.0": raise ValueError("V45 source VERSION must be 45.0.0.")
 skills=sorted((source/"skills").glob("*/SKILL.md"))
 if len(skills)!=4: raise ValueError(f"Expected four V45 skills; found {len(skills)}.")
 skillroot=root/".agents"/"skills"; skillroot.mkdir(parents=True,exist_ok=True)
 count=len(list(skillroot.glob("*/SKILL.md"))); names={p.parent.name for p in skills}
 collisions={n for n in names if (skillroot/n/"SKILL.md").is_file()}
 if count==280 and collisions: raise ValueError("V45 skill collision(s): "+", ".join(sorted(collisions)))
 if count==284 and collisions!=names: raise ValueError("Already-patched V45 package has incomplete skill set.")
 if count not in {280,284}: raise ValueError(f"Expected 280 V44 skills or 284 patched skills; found {count}.")
 shutil.copytree(source,root/"v45",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".pytest_cache","test-output"))
 for skill in skills:
  dest=skillroot/skill.parent.name; dest.mkdir(parents=True,exist_ok=True); shutil.copy2(skill,dest/"SKILL.md")
 for number in range(37,46):
  src=repo/f"v{number}"/"tools"/"audit_cumulative_package.py"
  if src.is_file():
   dest=root/f"v{number}"/"tools"/"audit_cumulative_package.py"; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
 agents=root/"AGENTS.md"
 if not agents.is_file(): agents.write_text("# Codex project instructions\n",encoding="utf-8")
 text=agents.read_text(encoding="utf-8")
 if MARKER not in text: agents.write_text(text.rstrip()+"\n\n"+GUIDANCE,encoding="utf-8")
 names_to_copy=["README.md","INDEX.md","tools/repository_audit.py"]
 names_to_copy += [f"INDEX_V{n}.md" for n in range(37,46)]
 names_to_copy += [f"RELEASE_NOTES_V{n}.md" for n in range(37,46)]
 for name in names_to_copy:
  src=repo/name
  if src.is_file():
   dest=root/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
 final=len(list(skillroot.glob("*/SKILL.md")))
 if final!=284: raise ValueError(f"Expected 284 native skills; found {final}.")
 print(f"PASS: installed V45; cumulative native skills={final}."); return final
def main()->int:
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("--package-root",required=True,type=Path); p.add_argument("--source-root",required=True,type=Path); a=p.parse_args()
 try: patch(a.package_root,a.source_root); return 0
 except (OSError,ValueError) as e: print("ERROR: "+str(e)); return 2
if __name__=="__main__": raise SystemExit(main())
