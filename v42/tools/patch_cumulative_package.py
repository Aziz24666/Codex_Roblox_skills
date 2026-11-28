#!/usr/bin/env python3
"""Install V42 into a verified cumulative V1-V41 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V42_LIVEOPS_EVENTS_CONFIG_MANAGEMENT -->"
GUIDANCE = """<!-- V42_LIVEOPS_EVENTS_CONFIG_MANAGEMENT -->
## V42 LiveOps, events, and experience configuration
Use Roblox Experience Configs for runtime feature flags and tunable values. In scripts, ConfigService is server-only and read-only; publish config changes through Creator Hub/Studio or the Open Cloud InExperienceConfig workflow. Stage and test changes first, retain the latest draftHash for optimistic concurrency, publish with a descriptive message, and read back the published values. ConfigSnapshot values are snapshots: refresh at a safe gameplay boundary when appropriate. Use explicit static fallbacks when initial loading fails. Event schedules must use timezone-aware timestamps and an idempotent server-side lifecycle. Keep secrets and credentials out of config values and source control. Rollback through revision restore stages a draft; it still requires a separately approved publish. V42 validates local JSON contracts only and never calls Roblox or publishes configuration.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path) -> int:
    root = package_root.expanduser().resolve()
    source = source_root.expanduser().resolve()
    repository = source.parent
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    if (source / "VERSION").read_text(encoding="utf-8").strip() != "42.0.0":
        raise ValueError("V42 source VERSION must be 42.0.0.")
    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected four V42 skills; found {len(skills)}.")
    skills_root = root / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    count = len(list(skills_root.glob("*/SKILL.md")))
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (skills_root / name / "SKILL.md").is_file()}
    if count == 268 and collisions:
        raise ValueError("V42 skill collision(s): " + ", ".join(sorted(collisions)))
    if count == 272 and collisions != names:
        raise ValueError("Already-patched V42 package has an incomplete skill set.")
    if count not in {268, 272}:
        raise ValueError(f"Expected 268 V41 skills or 272 already-patched skills; found {count}.")

    shutil.copytree(
        source, root / "v42", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "test-output"),
    )
    for skill in skills:
        target = skills_root / skill.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target / "SKILL.md")

    for version in ("v37", "v38", "v39", "v40", "v41"):
        auditor = repository / version / "tools" / "audit_cumulative_package.py"
        if auditor.is_file():
            target = root / version / "tools" / "audit_cumulative_package.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(auditor, target)

    agents = root / "AGENTS.md"
    if not agents.is_file():
        agents.write_text("# Codex project instructions\n", encoding="utf-8")
    agent_text = agents.read_text(encoding="utf-8")
    if MARKER not in agent_text:
        agents.write_text(agent_text.rstrip() + "\n\n" + GUIDANCE, encoding="utf-8")

    names_to_copy = (
        "README.md", "INDEX.md", "tools/repository_audit.py", "INDEX_V37.md", "INDEX_V38.md",
        "INDEX_V40.md", "INDEX_V41.md", "INDEX_V42.md",
        "RELEASE_NOTES_V37.md", "RELEASE_NOTES_V38.md", "RELEASE_NOTES_V39.md",
        "RELEASE_NOTES_V40.md", "RELEASE_NOTES_V41.md", "RELEASE_NOTES_V42.md",
    )
    for name in names_to_copy:
        candidate = repository / name
        if candidate.is_file():
            shutil.copy2(candidate, root / name)

    final_count = len(list(skills_root.glob("*/SKILL.md")))
    if final_count != 272:
        raise ValueError(f"Expected 272 cumulative native Codex skills; found {final_count}.")
    print(f"PASS: installed V42; cumulative native skills={final_count}.")
    return final_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        patch(args.package_root, args.source_root)
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
