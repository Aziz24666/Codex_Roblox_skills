#!/usr/bin/env python3
"""Install V26 Studio MCP tools and skills into the reconstructed cumulative package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V26_STUDIO_MCP_RULES -->"
RULES = """
<!-- V26_STUDIO_MCP_RULES -->
## V26 Roblox Studio MCP and test workflow

When a task needs live Studio access, check whether Roblox Studio's local MCP server is enabled and connected. Discover the connected Studio instances and use the intended studio_id; never assume GitHub Actions can reach the developer's local Studio process. Discover tool names and schemas from the live MCP server before using them.

Inspect the DataModel and scripts before editing. Keep edits scoped, read them back, inspect diffs, compile/test, and collect Studio logs or screenshots. Record exact test mode, client count, device/network settings, and whether a test actually ran. A planned or skipped test is never a PASS.

StudioTestService supports up to eight simulated clients per multiplayer test session and is plugin-facing. Device and Network Simulator features affect Studio tests only. Use synthetic data and isolated test places; never write production DataStores as part of ordinary automated validation.

Obtain explicit user approval before saving a modified place, publishing, overwriting/deleting user-owned assets, writing production DataStores, changing production economy configuration, or performing player-impacting Open Cloud operations. Apply least privilege. Preserve the inherited fair-monetization and no-gambling policy.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v26.py").is_file():
        raise ValueError(f"V26 source directory is incomplete: {source_root}")

    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 3:
        raise ValueError(f"Expected 3 V26 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {207, 210}:
        raise ValueError(f"Expected 207 pre-V26 skills or an already-patched 210-skill package, found {existing}.")

    shutil.copytree(
        source_root, package_root / "v26", dirs_exist_ok=True,
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
        "README.md", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md",
        "RELEASE_NOTES_V25.md", "RELEASE_NOTES_V25_0_1.md", "RELEASE_NOTES_V26.md",
    ):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)

    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 210:
        raise ValueError(f"V26 package must contain 210 native skills after patching; found {installed}.")
    print(f"Installed V26 into {package_root}; cumulative skill count is {installed}.")
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
