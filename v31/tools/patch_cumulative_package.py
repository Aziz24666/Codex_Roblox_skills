#!/usr/bin/env python3
"""Install V31 analytics governance into a cumulative V1-V30 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V31_PRIVACY_SAFE_ANALYTICS_AND_LIVEOPS -->"
RULES = """
<!-- V31_PRIVACY_SAFE_ANALYTICS_AND_LIVEOPS -->
## V31 privacy-safe analytics and LiveOps health

Use a small, purpose-bound catalog for custom analytics events. Keep AnalyticsService instrumentation server-authoritative, use stable event names and finite bounded custom-field values, and review custom fields for personal data or free text. Roblox documents limits of 100 custom event names, three custom fields, and 8,000 combined custom-field values; its custom events are server-side and do not send from Studio. Prefer aggregate health snapshots and sufficiently large cohorts; never export player-level telemetry, raw chat, personal identifiers, or individual-spender profiles into Codex reports. Define alert thresholds before inspecting results, hold stale or undersized evidence, and treat static findings as review leads. LiveOps changes, experiments, feature flags, and production operations remain human-approved. Preserve all V1-V30 rules, fair monetization, fixed outcomes, and the mandatory no-gambling policy.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v31.py").is_file():
        raise ValueError(f"V31 source directory is incomplete: {source_root}")
    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 4:
        raise ValueError(f"Expected 4 V31 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {224, 228}:
        raise ValueError(f"Expected 224 pre-V31 skills or an already-patched 228-skill package, found {existing}.")
    expected_names = {path.parent.name for path in skill_files}
    collisions = {name for name in expected_names if (target_skills / name / "SKILL.md").is_file()}
    if existing == 224 and collisions:
        raise ValueError("V31 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 228 and collisions != expected_names:
        raise ValueError("The 228-skill package does not contain the complete V31 skill set.")

    shutil.copytree(
        source_root, package_root / "v31", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
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
    for filename in (
        "README.md", "INDEX.md", "INDEX_V30.md", "INDEX_V31.md",
        "RELEASE_NOTES_V30.md", "RELEASE_NOTES_V31.md",
    ):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)
    source_audit = repository_root / "tools" / "repository_audit.py"
    if source_audit.is_file():
        destination = package_root / "tools" / source_audit.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_audit, destination)
    workflow = repository_root / ".github" / "workflows" / "v31-quality.yml"
    if workflow.is_file():
        destination = package_root / ".github" / "workflows"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, destination / workflow.name)

    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 228:
        raise ValueError(f"V31 package must contain 228 native skills after patching; found {installed}.")
    print(f"Installed V31 into {package_root}; cumulative skill count is {installed}.")
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
