#!/usr/bin/env python3
"""Install V28 security and reliability tooling into a cumulative V1-V27 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V28_SERVER_AUTHORITY_AND_MIGRATION_SAFETY -->"
RULES = """
<!-- V28_SERVER_AUTHORITY_AND_MIGRATION_SAFETY -->
## V28 server authority, persistence, and multiplayer reliability

Treat every client-supplied value as untrusted. Server code must independently validate arguments, bounds, ownership, permissions, state preconditions, and request frequency before high-impact operations. The server computes authoritative currency, damage, rewards, inventory, purchases, progression, and persistence outcomes. Make retry/duplicate semantics explicit and avoid granting or charging twice.

Version persistent data and keep migration transforms deterministic, idempotent, and safe to retry. Preserve unknown fields, verify backups and rollback in staging, and use synthetic data for routine migration tests. Do not automate production DataStore writes, Open Cloud operations, publishing, or live player-data changes. A static V28 report or migration-manifest validation is advisory and is not proof of security or a completed test. Preserve V1-V27 safeguards, including fair monetization and no-gambling rules.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v28.py").is_file():
        raise ValueError(f"V28 source directory is incomplete: {source_root}")
    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 3:
        raise ValueError(f"Expected 3 V28 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {213, 216}:
        raise ValueError(f"Expected 213 pre-V28 skills or an already-patched 216-skill package, found {existing}.")
    expected_names = {skill_file.parent.name for skill_file in skill_files}
    collisions = {
        name for name in expected_names if (target_skills / name / "SKILL.md").is_file()
    }
    if existing == 213 and collisions:
        raise ValueError("V28 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 216 and collisions != expected_names:
        raise ValueError("The 216-skill package does not contain the complete V28 skill set.")
    shutil.copytree(
        source_root, package_root / "v28", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    for skill_file in skill_files:
        destination = target_skills / skill_file.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_file, destination / "SKILL.md")
    agents_file = package_root / "AGENTS.md"
    if not agents_file.is_file():
        raise ValueError("Cumulative package is missing AGENTS.md.")
    agent_text = agents_file.read_text(encoding="utf-8")
    if MARKER not in agent_text:
        agents_file.write_text(agent_text.rstrip() + "\n\n" + RULES, encoding="utf-8")
    repository_root = source_root.parent
    for filename in (
        "README.md", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md", "INDEX_V28.md",
        "RELEASE_NOTES_V25.md", "RELEASE_NOTES_V25_0_1.md", "RELEASE_NOTES_V26.md",
        "RELEASE_NOTES_V27.md", "RELEASE_NOTES_V28.md",
    ):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)
    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 216:
        raise ValueError(f"V28 package must contain 216 native skills after patching; found {installed}.")
    print(f"Installed V28 into {package_root}; cumulative skill count is {installed}.")
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=None)
    args = parser.parse_args()
    patch(args.package_root, args.source_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
