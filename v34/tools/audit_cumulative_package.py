#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V34 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 240
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V31.md", "INDEX_V32.md", "INDEX_V33.md", "INDEX_V34.md",
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
    "v34/VERSION", "v34/INDEX_V34.md", "v34/tools/v34.py",
    "v34/tools/patch_cumulative_package.py", "v34/tools/audit_cumulative_package.py", "v34/tests/test_v34.py",
    "v34/docs/PERFORMANCE_SOAK_TESTING.md", "v34/docs/MICROPROFILER_AND_DASHBOARD_EVIDENCE.md",
    "v34/docs/REPEATED_BENCHMARKS_AND_ROLLOUT.md",
    "v34/schemas/soak-capture.schema.json", "v34/schemas/repeat-suite.schema.json",
    "v34/examples/soak-capture.example.json", "v34/examples/repeat-suite.example.json",
    ".agents/skills/roblox-performance-soak-and-memory-trend-v34/SKILL.md",
    ".agents/skills/roblox-microprofiler-capture-triage-v34/SKILL.md",
    ".agents/skills/roblox-repeated-benchmark-and-regression-v34/SKILL.md",
    ".agents/skills/roblox-live-performance-rollout-monitoring-v34/SKILL.md",
    "v34/skills/roblox-performance-soak-and-memory-trend-v34/SKILL.md",
    "v34/skills/roblox-microprofiler-capture-triage-v34/SKILL.md",
    "v34/skills/roblox-repeated-benchmark-and-regression-v34/SKILL.md",
    "v34/skills/roblox-live-performance-rollout-monitoring-v34/SKILL.md",
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
    version_path = root / "v34" / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if version != "34.0.0":
        problems.append(f"Unexpected V34 version: {version!r}.")
    agent_path = root / "AGENTS.md"
    agents = agent_path.read_text(encoding="utf-8") if agent_path.is_file() else ""
    if "<!-- V34_PERFORMANCE_SOAK_AND_REPEATED_BENCHMARKS -->" not in agents:
        problems.append("AGENTS.md is missing V34 performance evidence instructions.")
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if "V34" not in readme or "240 native Codex skills" not in readme:
        problems.append("README.md does not describe the V34 cumulative package.")
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
    print(f"PASS: cumulative V1-V34 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
