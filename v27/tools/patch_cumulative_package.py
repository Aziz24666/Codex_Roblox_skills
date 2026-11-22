#!/usr/bin/env python3
"""Install V27 Luau architecture tooling and skills into the reconstructed V1-V26 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V27_LUAU_ARCHITECTURE_RULES -->"
RULES = """
<!-- V27_LUAU_ARCHITECTURE_RULES -->
## V27 Luau architecture and analysis workflow

For Luau changes, inspect type-mode directives and use the official luau-analyze CLI when it is installed. Migrate gradually toward --!strict at stable module boundaries; never mass-add directives or suppress errors just to silence diagnostics.

Review static require dependencies, module cycles, possible unused modules, RemoteEvent/RemoteFunction call-handler contracts, and Rojo $path mappings. V27's offline dependency and remote inventories are conservative text-based heuristics: verify findings against the actual source and Studio DataModel before changing code. Do not delete or move modules based only on an unused/cycle report.

Run focused type checks, unit tests, Rojo validation/build, and Studio tests after architecture changes. Keep server authority, remote input validation, and project/place identity explicit. V27's tools are read-only apart from writing their generated report; no source script, Rojo project, or place file is changed by an audit.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v27.py").is_file():
        raise ValueError(f"V27 source directory is incomplete: {source_root}")

    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 3:
        raise ValueError(f"Expected 3 V27 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {210, 213}:
        raise ValueError(f"Expected 210 pre-V27 skills or an already-patched 213-skill package, found {existing}.")

    shutil.copytree(
        source_root, package_root / "v27", dirs_exist_ok=True,
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
        "README.md", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md",
        "RELEASE_NOTES_V25.md", "RELEASE_NOTES_V25_0_1.md", "RELEASE_NOTES_V26.md", "RELEASE_NOTES_V27.md",
    ):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)

    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 213:
        raise ValueError(f"V27 package must contain 213 native skills after patching; found {installed}.")
    print(f"Installed V27 into {package_root}; cumulative skill count is {installed}.")
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
