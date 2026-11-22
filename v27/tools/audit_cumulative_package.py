#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V27 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 213
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md",
    "v23/tools/v23.py", "v23/tests/test_v23.py",
    "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
    "v25/VERSION", "v25/tools/v25.py", "v25/tests/test_v25.py",
    "v26/VERSION", "v26/tools/v26.py", "v26/tests/test_v26.py",
    "v26/tools/patch_cumulative_package.py", "v26/tools/audit_cumulative_package.py",
    "v26/docs/STUDIO_MCP_WORKFLOW.md", "v26/docs/MULTIPLAYER_DEVICE_TESTING.md",
    "v26/docs/SAFE_AUTOMATION_BOUNDARIES.md", "v26/schemas/studio-test-plan.schema.json",
    "v27/VERSION", "v27/INDEX_V27.md", "v27/tools/v27.py", "v27/tests/test_v27.py",
    "v27/tools/patch_cumulative_package.py", "v27/tools/audit_cumulative_package.py",
    "v27/docs/LUAU_STATIC_ANALYSIS.md", "v27/docs/DEPENDENCY_AND_REMOTE_CONTRACTS.md",
    "v27/docs/ROJO_PROJECT_VALIDATION.md", "v27/docs/STRICT_TYPING_MIGRATION.md",
    "v27/schemas/architecture-report.schema.json",
    ".agents/skills/roblox-luau-static-analysis-v27/SKILL.md",
    ".agents/skills/roblox-luau-architecture-and-dependency-governance-v27/SKILL.md",
    ".agents/skills/roblox-remote-contract-and-rojo-validation-v27/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return [f"Package root is not a directory: {root}"]
    problems = [f"Missing required file: {item}" for item in REQUIRED_FILES if not (root / item).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = list(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) != EXPECTED_SKILLS:
        problems.append(f"Expected {EXPECTED_SKILLS} native skills, found {len(skills)}.")
    version = (root / "v27" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v27" / "VERSION").is_file() else ""
    if version != "27.0.0":
        problems.append(f"Unexpected V27 version: {version!r}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V27_LUAU_ARCHITECTURE_RULES -->" not in agents:
        problems.append("AGENTS.md is missing the V27 Luau architecture instructions.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "V27" not in readme or "213 native Codex skills" not in readme:
        problems.append("README.md does not describe the V27 cumulative package.")
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
    print(f"PASS: cumulative V1-V27 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
