#!/usr/bin/env python3
"""Install V43 into a verified cumulative V1-V42 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V43_EXPERIMENTATION_DECISION_INTELLIGENCE -->"
GUIDANCE = """<!-- V43_EXPERIMENTATION_DECISION_INTELLIGENCE -->
## V43 Roblox experiments and decision review
Use Creator Hub Experiments for native in-game config tests. Plan one causal hypothesis, one goal metric, a small set of learning/guardrail metrics, and review Roblox's MDE before scheduling. Native in-game experiments use a baseline and up to two treatments; the documented duration is 14-60 days. Let the planned duration complete unless an operator reviews critical early harm or SRM. Custom events are server-side and published-experience-only; keep event names stable and data minimal. Open Cloud experiment operations are asynchronous: poll operation IDs and check final results. Keep API credentials outside the repository and require human approval for writes and final rollout decisions. V43's CLI is offline and does not assign players, start/complete experiments, compute significance/MDE/SRM, select winners, or publish config.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path) -> int:
    root = package_root.expanduser().resolve()
    source = source_root.expanduser().resolve()
    repository = source.parent
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    if (source / "VERSION").read_text(encoding="utf-8").strip() != "43.0.0":
        raise ValueError("V43 source VERSION must be 43.0.0.")
    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected four V43 skills; found {len(skills)}.")

    skills_root = root / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    count = len(list(skills_root.glob("*/SKILL.md")))
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (skills_root / name / "SKILL.md").is_file()}
    if count == 272 and collisions:
        raise ValueError("V43 skill collision(s): " + ", ".join(sorted(collisions)))
    if count == 276 and collisions != names:
        raise ValueError("Already-patched V43 package has an incomplete skill set.")
    if count not in {272, 276}:
        raise ValueError(f"Expected 272 V42 skills or 276 already-patched skills; found {count}.")

    shutil.copytree(
        source, root / "v43", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "test-output"),
    )
    for skill in skills:
        target = skills_root / skill.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target / "SKILL.md")

    for version in ("v37", "v38", "v39", "v40", "v41", "v42"):
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
        "README.md", "INDEX.md", "tools/repository_audit.py",
        "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md",
        "INDEX_V41.md", "INDEX_V42.md", "INDEX_V43.md",
        "RELEASE_NOTES_V37.md", "RELEASE_NOTES_V38.md", "RELEASE_NOTES_V39.md",
        "RELEASE_NOTES_V40.md", "RELEASE_NOTES_V41.md", "RELEASE_NOTES_V42.md",
        "RELEASE_NOTES_V43.md",
    )
    for name in names_to_copy:
        candidate = repository / name
        if candidate.is_file():
            shutil.copy2(candidate, root / name)

    final_count = len(list(skills_root.glob("*/SKILL.md")))
    if final_count != 276:
        raise ValueError(f"Expected 276 cumulative native Codex skills; found {final_count}.")
    print(f"PASS: installed V43; cumulative native skills={final_count}.")
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
