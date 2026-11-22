#!/usr/bin/env python3
"""Audit a reconstructed cumulative V1-V28 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 216
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md", "INDEX_V28.md",
    "v23/tools/v23.py", "v23/tests/test_v23.py",
    "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
    "v25/VERSION", "v25/tools/v25.py", "v25/tests/test_v25.py",
    "v26/VERSION", "v26/tools/v26.py", "v26/tests/test_v26.py",
    "v27/VERSION", "v27/tools/v27.py", "v27/tests/test_v27.py",
    "v28/VERSION", "v28/INDEX_V28.md", "v28/tools/v28.py", "v28/tests/test_v28.py",
    "v28/tools/patch_cumulative_package.py", "v28/tools/audit_cumulative_package.py",
    "v28/docs/SERVER_AUTHORITY_AND_REMOTE_SECURITY.md", "v28/docs/DATASTORE_MIGRATION_SAFETY.md",
    "v28/docs/MULTIPLAYER_RELIABILITY_VALIDATION.md", "v28/docs/SECURITY_REPORT_REFERENCE.md",
    "v28/schemas/security-reliability-report.schema.json", "v28/schemas/migration-manifest.schema.json",
    ".agents/skills/roblox-server-authority-review-v28/SKILL.md",
    ".agents/skills/roblox-datastore-migration-safety-v28/SKILL.md",
    ".agents/skills/roblox-multiplayer-reliability-validation-v28/SKILL.md",
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
    version = (root / "v28" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v28" / "VERSION").is_file() else ""
    if version != "28.0.0":
        problems.append(f"Unexpected V28 version: {version!r}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V28_SERVER_AUTHORITY_AND_MIGRATION_SAFETY -->" not in agents:
        problems.append("AGENTS.md is missing the V28 server-authority and migration instructions.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "V28" not in readme or "216 native Codex skills" not in readme:
        problems.append("README.md does not describe the V28 cumulative package.")
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
    print(f"PASS: cumulative V1-V28 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
