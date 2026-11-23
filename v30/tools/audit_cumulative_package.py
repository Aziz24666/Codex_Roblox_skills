#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V30 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS = 224
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V30.md",
    "tools/repository_audit.py",
    "v30/VERSION", "v30/INDEX_V30.md", "v30/tools/v30.py",
    "v30/tools/patch_cumulative_package.py", "v30/tools/audit_cumulative_package.py",
    "v30/tests/test_v30.py", "v30/docs/PRODUCTION_RELEASE_READINESS.md",
    "v30/docs/RELEASE_EVIDENCE_AND_ROLLBACK.md",
    "v30/schemas/release-plan.schema.json", "v30/schemas/release-report.schema.json",
    "v30/examples/release-plan.staging.example.json",
    ".agents/skills/roblox-production-release-readiness-v30/SKILL.md",
    ".agents/skills/roblox-release-evidence-management-v30/SKILL.md",
    ".agents/skills/roblox-rollback-and-incident-response-v30/SKILL.md",
    ".agents/skills/roblox-environment-configuration-hygiene-v30/SKILL.md",
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
    version = (root / "v30" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v30" / "VERSION").is_file() else ""
    if version != "30.0.0":
        problems.append(f"Unexpected V30 version: {version!r}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V30_PRODUCTION_RELEASE_READINESS -->" not in agents:
        problems.append("AGENTS.md is missing the V30 production release-readiness instructions.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "V30" not in readme or "224 native Codex skills" not in readme:
        problems.append("README.md does not describe the V30 cumulative package.")
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
    print(f"PASS: cumulative V1-V30 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
