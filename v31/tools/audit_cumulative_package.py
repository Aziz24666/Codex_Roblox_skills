#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V31 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS = 228
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V30.md", "INDEX_V31.md",
    "tools/repository_audit.py",
    "v30/VERSION", "v30/tools/v30.py",
    "v31/VERSION", "v31/INDEX_V31.md", "v31/tools/v31.py",
    "v31/tools/patch_cumulative_package.py", "v31/tools/audit_cumulative_package.py",
    "v31/tests/test_v31.py", "v31/docs/ANALYTICS_EVENT_GOVERNANCE.md",
    "v31/docs/AGGREGATE_GAME_HEALTH_AND_LIVEOPS.md",
    "v31/schemas/event-catalog.schema.json", "v31/schemas/health-policy.schema.json",
    "v31/schemas/health-snapshot.schema.json",
    "v31/examples/event-catalog.example.json", "v31/examples/health-policy.example.json",
    "v31/examples/health-snapshot.example.json",
    ".agents/skills/roblox-analytics-instrumentation-governance-v31/SKILL.md",
    ".agents/skills/roblox-privacy-safe-game-health-analytics-v31/SKILL.md",
    ".agents/skills/roblox-liveops-operations-readiness-v31/SKILL.md",
    ".agents/skills/roblox-experiment-design-and-guardrails-v31/SKILL.md",
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
    version = (root / "v31" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v31" / "VERSION").is_file() else ""
    if version != "31.0.0":
        problems.append(f"Unexpected V31 version: {version!r}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V31_PRIVACY_SAFE_ANALYTICS_AND_LIVEOPS -->" not in agents:
        problems.append("AGENTS.md is missing the V31 privacy-safe analytics and LiveOps instructions.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "V31" not in readme or "228 native Codex skills" not in readme:
        problems.append("README.md does not describe the V31 cumulative package.")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    problems = audit(args.root)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print(f"PASS: cumulative V1-V31 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
