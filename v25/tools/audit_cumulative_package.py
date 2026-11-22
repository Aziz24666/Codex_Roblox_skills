#!/usr/bin/env python3
"""Audit a reconstructed V1-V25 package for required continuity components."""
from __future__ import annotations
import argparse
from pathlib import Path
EXPECTED_SKILLS = 207
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "INDEX.md", "INDEX_V25.md", "v25/VERSION", "v25/tools/v25.py",
    "v25/tools/patch_cumulative_package.py", "v25/docs/SESSION_CONTINUITY.md",
    "v25/tests/test_v25.py",
    "v23/tools/v23.py", "v23/tests/test_v23.py",
    "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
    "v24/tools/v24.py", "v24/docs/AUTOMATED_GROWTH_PIPELINE.md",
    ".agents/skills/roblox-codex-session-continuity/SKILL.md",
    ".agents/skills/roblox-resumable-task-execution/SKILL.md",
)
def audit(root: Path) -> list[str]:
    root = root.resolve()
    problems = [f"Missing required file: {item}" for item in REQUIRED_FILES if not (root / item).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = list(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) != EXPECTED_SKILLS:
        problems.append(f"Expected {EXPECTED_SKILLS} native skills, found {len(skills)}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V25_SESSION_CONTINUITY_RULES -->" not in agents:
        problems.append("AGENTS.md is missing the V25 continuity instructions.")
    version = (root / "v25" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v25" / "VERSION").is_file() else ""
    if version != "25.0.1":
        problems.append(f"Unexpected V25 version: {version!r}.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "V25" not in readme:
        problems.append("README.md does not identify the V25 package.")
    return problems
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Reconstructed package root.")
    args = parser.parse_args()
    problems = audit(args.root)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print(f"PASS: cumulative V1-V25 package audit ({EXPECTED_SKILLS} native skills).")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
