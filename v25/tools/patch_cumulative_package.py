#!/usr/bin/env python3
"""Install the V25 continuity tools and skills into a reconstructed cumulative package."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path

MARKER = "<!-- V25_SESSION_CONTINUITY_RULES -->"
RULES = """
<!-- V25_SESSION_CONTINUITY_RULES -->
## V25 session continuity and interruption recovery

At the beginning of a resumed task, inspect the project's .codex/session/checkpoint.json and run the V25 status, verify, and resume commands when a checkpoint exists. Verify repository files and Git state before trusting a checkpoint.

For substantial work, define one small independently testable stage at a time. After completing a stage, changing an important decision, or before a risky/long operation, run v25/tools/v25.py checkpoint with verified completed items, current next actions, test results, changed files, and the known branch/commit. Before ending or handing work to another session, run v25/tools/v25.py handoff and leave the generated RESUME_PROMPT.md.

Never put raw conversation transcripts, credentials, API keys, passwords, tokens, or private user data in a checkpoint. Do not claim unverified work is complete. A checkpoint is a recovery aid, not a substitute for tests, version control, or user approval. Preserve all inherited V18-V24 fair-monetization and no-gambling constraints.
""".strip() + "\n"

def patch(package_root: Path, source_root: Path | None = None) -> int:
    package_root = package_root.resolve()
    if not package_root.is_dir():
        raise ValueError(f"Package root does not exist: {package_root}")
    source_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    if not (source_root / "VERSION").is_file() or not (source_root / "tools" / "v25.py").is_file():
        raise ValueError(f"V25 source directory is incomplete: {source_root}")
    shutil.copytree(source_root, package_root / "v25", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    skills_target = package_root / ".agents" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    installed = 0
    for skill_file in sorted((source_root / "skills").glob("*/SKILL.md")):
        skill_dir = skills_target / skill_file.parent.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_file, skill_dir / "SKILL.md")
        installed += 1
    if installed != 2:
        raise ValueError(f"Expected 2 V25 skills, found {installed}.")
    agents_file = package_root / "AGENTS.md"
    if not agents_file.is_file():
        raise ValueError("Cumulative package is missing AGENTS.md.")
    agents_text = agents_file.read_text(encoding="utf-8")
    if MARKER not in agents_text:
        agents_file.write_text(agents_text.rstrip() + "\n\n" + RULES, encoding="utf-8")
    repository_root = source_root.parent
    for filename in ("README.md", "INDEX_V25.md", "RELEASE_NOTES_V25.md"):
        source = repository_root / filename
        if source.is_file():
            shutil.copy2(source, package_root / filename)
    print(f"Installed V25 into {package_root}; added {installed} skills.")
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
