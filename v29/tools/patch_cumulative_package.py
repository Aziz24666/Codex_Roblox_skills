#!/usr/bin/env python3
"""Install V29 performance engineering tools into a cumulative V1-V28 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V29_PERFORMANCE_ENGINEERING -->"
RULES = """
<!-- V29_PERFORMANCE_ENGINEERING -->
## V29 performance engineering and evidence

Profile before optimizing. Use Roblox Studio MicroProfiler, Script Profiler, Developer Console, and representative low-end mobile, high-end mobile, and desktop hardware. Record reproducible scene, player count, device, build, and capture conditions. Treat V29 static findings as heuristic review prompts, never as measured FPS, memory, CPU, network, or load-time results.

Set explicit device-specific budgets and compare externally captured measurements under equivalent conditions. Preserve correctness and readability, and re-profile after each focused change. Do not claim that a static scan or CI job ran a live Studio performance test. Preserve all V1-V28 safeguards, including server authority, secure persistence, fair monetization, and no-gambling rules.
""".strip() + "\n"

def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.expanduser().resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v29.py").is_file():
        raise ValueError(f"V29 source directory is incomplete: {source_root}")
    skill_files = sorted((source_root / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 4:
        raise ValueError(f"Expected 4 V29 skills, found {len(skill_files)}.")
    target_skills = package_root / ".agents" / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    existing = len(list(target_skills.glob("*/SKILL.md")))
    if existing not in {216, 220}:
        raise ValueError(f"Expected 216 pre-V29 skills or an already-patched 220-skill package, found {existing}.")
    expected_names = {path.parent.name for path in skill_files}
    collisions = {name for name in expected_names if (target_skills / name / "SKILL.md").is_file()}
    if existing == 216 and collisions:
        raise ValueError("V29 skill name collision(s): " + ", ".join(sorted(collisions)))
    if existing == 220 and collisions != expected_names:
        raise ValueError("The 220-skill package does not contain the complete V29 skill set.")
    shutil.copytree(source_root, package_root / "v29", dirs_exist_ok=True,
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
    for filename in (
        "README.md", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md", "INDEX_V28.md", "INDEX_V29.md",
        "RELEASE_NOTES_V25.md", "RELEASE_NOTES_V25_0_1.md", "RELEASE_NOTES_V26.md",
        "RELEASE_NOTES_V27.md", "RELEASE_NOTES_V28.md", "RELEASE_NOTES_V29.md",
    ):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)
    workflow = repository_root / ".github" / "workflows" / "v29-quality.yml"
    if workflow.is_file():
        destination = package_root / ".github" / "workflows"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, destination / workflow.name)
    installed = len(list(target_skills.glob("*/SKILL.md")))
    if installed != 220:
        raise ValueError(f"V29 package must contain 220 native skills after patching; found {installed}.")
    print(f"Installed V29 into {package_root}; cumulative skill count is {installed}.")
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
