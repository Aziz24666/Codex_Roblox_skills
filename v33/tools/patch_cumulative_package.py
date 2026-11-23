#!/usr/bin/env python3
"""Install the V33 automated QA layer into a cumulative V1-V32 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V33_AUTOMATED_QA_AND_REGRESSION -->"
RULES = """
<!-- V33_AUTOMATED_QA_AND_REGRESSION -->
## V33 automated QA and regression discipline

For each meaningful game-system change, create a small repeatable test plan with unique test IDs, explicit expected outcomes, setup requirements, platform coverage, and the correct execution mode. Separate static-local checks from Roblox Studio execution. Use Studio Test/Run and Server & Clients as appropriate; use StudioTestService only from its supported Studio plugin/test contexts, and respect its eight-client ceiling and one-session-at-a-time constraint. Use Device Simulator, Controller Emulator, Network Simulator, and VirtualInput only within their documented Studio boundaries. Never put Studio-only test APIs into published gameplay scripts. Every planned case must end as pass, fail, blocked, or not_run; blocked and not_run are not passes. Compare reports against a known baseline and investigate pass-to-fail regressions. Keep QA reports privacy-minimal: test IDs, fixed status/outcome codes, timestamps, environment codes, and opaque evidence references only. Do not include player IDs, usernames, raw chat, credentials, private tokens, private server identifiers, or arbitrary player records. A static inventory or passing GitHub Actions workflow does not prove a Roblox Studio test ran. Preserve all V1-V32 security, privacy, player-safety, human-moderation, transparent monetization, fixed paid-outcome, and mandatory no-gambling safeguards.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v33.py").is_file():
        raise ValueError(f"V33 source directory is incomplete: {source_root}")
    if (source_root / "VERSION").read_text(encoding="utf-8").strip() != "33.0.0":
        raise ValueError("V33 source VERSION must be 33.0.0.")
    skills = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected exactly 4 V33 skills, found {len(skills)}.")
    for skill in skills:
        content = skill.read_text(encoding="utf-8")
        if not content.startswith("---\n") or "name:" not in content.split("---", 2)[1]:
            raise ValueError(f"Skill metadata is missing or malformed: {skill}")
    target = package_root / ".agents" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    existing = len(list(target.glob("*/SKILL.md")))
    if existing not in {232, 236}:
        raise ValueError(f"Expected 232 pre-V33 skills or an already-patched 236-skill package, found {existing}.")
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (target / name / "SKILL.md").is_file()}
    if existing == 232 and collisions:
        raise ValueError("V33 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 236 and collisions != names:
        raise ValueError("The 236-skill package does not contain the complete V33 skill set.")
    shutil.copytree(
        source_root,
        package_root / "v33",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    for skill in skills:
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
        "README.md", "INDEX.md", "INDEX_V31.md", "INDEX_V32.md", "INDEX_V33.md",
        "RELEASE_NOTES_V31.md", "RELEASE_NOTES_V32.md", "RELEASE_NOTES_V33.md",
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
    for workflow_name in ("v32-quality.yml", "v33-quality.yml"):
        source = repo / ".github" / "workflows" / workflow_name
        if source.is_file():
            shutil.copy2(source, workflow_target / workflow_name)
    count = len(list(target.glob("*/SKILL.md")))
    if count != 236:
        raise ValueError(f"V33 package must contain 236 native skills after patching; found {count}.")
    print(f"Installed V33 into {package_root}; cumulative skill count is {count}.")
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
