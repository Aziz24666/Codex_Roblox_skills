#!/usr/bin/env python3
"""Install the V34 performance evidence layer into a cumulative V1-V33 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V34_PERFORMANCE_SOAK_AND_REPEATED_BENCHMARKS -->"
RULES = """
<!-- V34_PERFORMANCE_SOAK_AND_REPEATED_BENCHMARKS -->
## V34 performance soak, profiler evidence, and repeatability

Profile the correct side (client or server), preserve scenario/build/device/network/player-count metadata, and capture a time-ordered measurement series. Use stable workload and server-age information when investigating memory growth. A positive trend is a diagnostic lead, not proof of a leak. Require repeated baseline and candidate runs under matched conditions before treating a measured change as a regression. Compare medians across independent runs, inspect individual runs and noise, and use project-specific device budgets. MicroProfiler, Script Profiler, Developer Console, and Creator Dashboard evidence must be captured through their supported Roblox tools; the V34 CLI validates supplied structured numeric summaries only. Never claim offline CI collected live metrics. Use only aggregate performance information and opaque evidence references; exclude player identities, chat/voice content, credentials, private server identifiers, and raw logs. Keep any rollout pause or rollback under human approval and the existing V30 release procedure. Preserve all V1-V33 security, privacy, player-safety, human-moderation, transparent monetization, fixed paid-outcome, and mandatory no-gambling safeguards.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v34.py").is_file():
        raise ValueError(f"V34 source directory is incomplete: {source_root}")
    if (source_root / "VERSION").read_text(encoding="utf-8").strip() != "34.0.0":
        raise ValueError("V34 source VERSION must be 34.0.0.")
    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 4:
        raise ValueError(f"Expected exactly 4 V34 skills, found {len(skill_files)}.")
    for skill in skill_files:
        content = skill.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if not content.startswith("---\n") or len(parts) != 3 or "name:" not in parts[1] or "description:" not in parts[1]:
            raise ValueError(f"Skill metadata is missing or malformed: {skill}")
    target = package_root / ".agents" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    existing = len(list(target.glob("*/SKILL.md")))
    if existing not in {236, 240}:
        raise ValueError(f"Expected 236 pre-V34 skills or an already-patched 240-skill package, found {existing}.")
    names = {skill.parent.name for skill in skill_files}
    collisions = {name for name in names if (target / name / "SKILL.md").is_file()}
    if existing == 236 and collisions:
        raise ValueError("V34 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 240 and collisions != names:
        raise ValueError("The 240-skill package does not contain the complete V34 skill set.")
    shutil.copytree(
        source_root, package_root / "v34", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    for skill in skill_files:
        destination = target / skill.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, destination / "SKILL.md")
    agents = package_root / "AGENTS.md"
    if not agents.is_file():
        raise ValueError("Cumulative package is missing AGENTS.md.")
    agent_text = agents.read_text(encoding="utf-8")
    if MARKER not in agent_text:
        agents.write_text(agent_text.rstrip() + "\n\n" + RULES, encoding="utf-8")
    repo = source_root.parent
    for name in (
        "README.md", "INDEX.md", "INDEX_V31.md", "INDEX_V32.md", "INDEX_V33.md", "INDEX_V34.md",
        "RELEASE_NOTES_V31.md", "RELEASE_NOTES_V32.md", "RELEASE_NOTES_V33.md", "RELEASE_NOTES_V34.md",
    ):
        source = repo / name
        if source.is_file():
            shutil.copy2(source, package_root / name)
    audit_source = repo / "tools" / "repository_audit.py"
    if audit_source.is_file():
        destination = package_root / "tools" / audit_source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(audit_source, destination)
    workflow_target = package_root / ".github" / "workflows"
    workflow_target.mkdir(parents=True, exist_ok=True)
    for workflow_name in ("v33-quality.yml", "v34-quality.yml"):
        source = repo / ".github" / "workflows" / workflow_name
        if source.is_file():
            shutil.copy2(source, workflow_target / workflow_name)
    count = len(list(target.glob("*/SKILL.md")))
    if count != 240:
        raise ValueError(f"V34 package must contain 240 native skills after patching; found {count}.")
    print(f"Installed V34 into {package_root}; cumulative skill count is {count}.")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    patch(args.package_root, args.source_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
