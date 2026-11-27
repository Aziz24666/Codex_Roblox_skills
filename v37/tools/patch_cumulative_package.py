#!/usr/bin/env python3
"""Install V37 into a verified cumulative V1-V36 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V37_PROJECT_IMPLEMENTATION_ORCHESTRATION -->"
RULES = """
<!-- V37_PROJECT_IMPLEMENTATION_ORCHESTRATION -->
## V37 project-aware implementation orchestration
Before substantial work in an existing game, confirm the real project root and perform a read-only reconnaissance pass. Map only observed project structure, entry points, data flow, conventions, and verification commands. Convert approved feature goals into small dependency-ordered tasks with explicit allowed paths, risks, human-review requirements, and verifiable acceptance criteria. Keep overlapping file scopes dependency-ordered. During implementation, stay within declared scope and stop for plan revision when scope must expand. Record actual changed paths and test outcomes; never invent CI, Studio, runtime, device, or multiplayer evidence. V37's offline validator checks supplied plan/report metadata and declared path scope only; it does not inspect source diffs, execute code, run Studio, or authenticate evidence references. Preserve all V1-V36 server-authority, persistence, privacy, player-safety, moderation, accessibility, transparent monetization, fixed paid outcomes, and mandatory no-gambling safeguards.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    root = package_root.expanduser().resolve()
    source = (source_root or Path(__file__).resolve().parents[1]).resolve()
    version_file = source / "VERSION"
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    if not version_file.is_file() or version_file.read_text(encoding="utf-8").strip() != "37.0.0":
        raise ValueError("V37 source VERSION must be 37.0.0.")

    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected exactly 4 V37 skills, found {len(skills)}.")
    target = root / ".agents" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    count = len(list(target.glob("*/SKILL.md")))
    if count not in {248, 252}:
        raise ValueError(f"Expected 248 pre-V37 skills or 252 already-patched skills, found {count}.")

    expected_names = {skill.parent.name for skill in skills}
    collisions = {name for name in expected_names if (target / name / "SKILL.md").is_file()}
    if count == 248 and collisions:
        raise ValueError("V37 skill path collision(s): " + ", ".join(sorted(collisions)))
    if count == 252 and collisions != expected_names:
        raise ValueError("The 252-skill package does not contain the complete V37 skill set.")

    shutil.copytree(source, root / "v37", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for skill in skills:
        destination = target / skill.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, destination / "SKILL.md")

    agents = root / "AGENTS.md"
    if not agents.is_file():
        raise ValueError("Cumulative package is missing AGENTS.md.")
    agent_content = agents.read_text(encoding="utf-8")
    if MARKER not in agent_content:
        agents.write_text(agent_content.rstrip() + "\n\n" + RULES, encoding="utf-8")

    repository = source.parent
    for name in (
        "README.md", "INDEX.md", "INDEX_V36.md", "INDEX_V37.md",
        "RELEASE_NOTES_V36.md", "RELEASE_NOTES_V37.md",
    ):
        source_file = repository / name
        if source_file.is_file():
            shutil.copy2(source_file, root / name)

    final_count = len(list(target.glob("*/SKILL.md")))
    if final_count != 252:
        raise ValueError(f"V37 cumulative package must contain 252 skills; found {final_count}.")
    print(f"PASS: installed V37; cumulative native skills={final_count}.")
    return final_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    patch(args.package_root, args.source_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
