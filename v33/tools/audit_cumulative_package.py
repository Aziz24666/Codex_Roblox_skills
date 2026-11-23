#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V33 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 236
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V31.md", "INDEX_V32.md", "INDEX_V33.md",
    "tools/repository_audit.py",
    "v31/VERSION", "v31/tools/v31.py",
    "v32/VERSION", "v32/INDEX_V32.md", "v32/tools/v32.py",
    "v32/tools/patch_cumulative_package.py", "v32/tools/audit_cumulative_package.py", "v32/tests/test_v32.py",
    "v32/docs/TEXT_FILTERING_AND_UGC.md", "v32/docs/MODERATION_AND_APPEALS.md", "v32/docs/PLAYER_SAFETY_BY_DESIGN.md",
    "v33/VERSION", "v33/INDEX_V33.md", "v33/tools/v33.py",
    "v33/tools/patch_cumulative_package.py", "v33/tools/audit_cumulative_package.py", "v33/tests/test_v33.py",
    "v33/docs/STUDIO_AUTOMATION.md", "v33/docs/MULTIPLAYER_AND_NETWORK_TESTING.md",
    "v33/docs/DEVICE_AND_INPUT_TESTING.md", "v33/docs/TEST_EVIDENCE_AND_REGRESSION.md",
    "v33/schemas/test-plan.schema.json", "v33/schemas/test-report.schema.json",
    "v33/examples/test-plan.example.json", "v33/examples/test-report.example.json",
    "v33/examples/test-report.local-static.example.json",
    ".agents/skills/roblox-studio-automated-playtesting-v33/SKILL.md",
    ".agents/skills/roblox-multiplayer-regression-testing-v33/SKILL.md",
    ".agents/skills/roblox-device-and-input-testing-v33/SKILL.md",
    ".agents/skills/roblox-test-evidence-and-defect-triage-v33/SKILL.md",
    "v33/skills/roblox-studio-automated-playtesting-v33/SKILL.md",
    "v33/skills/roblox-multiplayer-regression-testing-v33/SKILL.md",
    "v33/skills/roblox-device-and-input-testing-v33/SKILL.md",
    "v33/skills/roblox-test-evidence-and-defect-triage-v33/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return [f"Package root is not a directory: {root}"]
    problems = [f"Missing required file: {item}" for item in REQUIRED_FILES if not (root / item).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) != EXPECTED_SKILLS:
        problems.append(f"Expected {EXPECTED_SKILLS} native skills, found {len(skills)}.")
    version_path = root / "v33" / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if version != "33.0.0":
        problems.append(f"Unexpected V33 version: {version!r}.")
    agent_path = root / "AGENTS.md"
    agents = agent_path.read_text(encoding="utf-8") if agent_path.is_file() else ""
    if "<!-- V33_AUTOMATED_QA_AND_REGRESSION -->" not in agents:
        problems.append("AGENTS.md is missing V33 QA and regression instructions.")
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if "V33" not in readme or "236 native Codex skills" not in readme:
        problems.append("README.md does not describe the V33 cumulative package.")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    problems = audit(args.root)
    if problems:
        for item in problems:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: cumulative V1-V33 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
