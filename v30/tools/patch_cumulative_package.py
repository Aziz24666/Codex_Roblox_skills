#!/usr/bin/env python3
"""Install V30 release-readiness tools and skills into a cumulative V1-V29 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V30_PRODUCTION_RELEASE_READINESS -->"
RULES = """
<!-- V30_PRODUCTION_RELEASE_READINESS -->
## V30 production release readiness and evidence

Treat release plans as checklists and evidence indexes, not authorization. Validate source revision, staging/production gates, evidence paths, hashes, rollback plans, backups, and named human approvals before a release owner makes a manual decision. Keep publishing manual, use a staged rollout, rehearse rollback in an isolated environment, and never run migrations or production writes from an offline audit. Do not copy credentials into source, reports, prompts, or issues; use approved secret storage and rotate credentials if exposure is suspected. Preserve all V1-V29 requirements, including server authority, safe persistence, profiling evidence, fair monetization, and the mandatory no-gambling policy.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v30.py").is_file():
        raise ValueError(f"V30 source directory is incomplete: {source_root}")
    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 4:
        raise ValueError(f"Expected 4 V30 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {220, 224}:
        raise ValueError(f"Expected 220 pre-V30 skills or an already-patched 224-skill package, found {existing}.")
    expected_names = {path.parent.name for path in skill_files}
    collisions = {name for name in expected_names if (target_skills / name / "SKILL.md").is_file()}
    if existing == 220 and collisions:
        raise ValueError("V30 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 224 and collisions != expected_names:
        raise ValueError("The 224-skill package does not contain the complete V30 skill set.")

    shutil.copytree(source_root, package_root / "v30", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for skill_file in skill_files:
        destination = target_skills / skill_file.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_file, destination / "SKILL.md")

    agents = package_root / "AGENTS.md"
    if not agents.is_file():
        raise ValueError("Cumulative package is missing AGENTS.md.")
    agent_text = agents.read_text(encoding="utf-8")
    if MARKER not in agent_text:
        agents.write_text(agent_text.rstrip() + "\n\n" + RULES, encoding="utf-8")

    repository_root = source_root.parent
    for filename in ("README.md", "INDEX.md", "INDEX_V30.md", "RELEASE_NOTES_V30.md"):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)
    for filename in ("repository_audit.py",):
        source = repository_root / "tools" / filename
        if source.is_file():
            destination = package_root / "tools" / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    workflow = repository_root / ".github" / "workflows" / "v30-quality.yml"
    if workflow.is_file():
        destination = package_root / ".github" / "workflows"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, destination / workflow.name)

    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 224:
        raise ValueError(f"V30 package must contain 224 native skills after patching; found {installed}.")
    print(f"Installed V30 into {package_root}; cumulative skill count is {installed}.")
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    patch(args.package_root, args.source_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
