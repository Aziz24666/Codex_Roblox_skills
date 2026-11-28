#!/usr/bin/env python3
"""Install V44 into a verified cumulative V1-V43 package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V44_PLAYER_FEEDBACK_RESEARCH_OPERATIONS -->"
GUIDANCE = """<!-- V44_PLAYER_FEEDBACK_RESEARCH_OPERATIONS -->
## V44 player feedback and research operations
Start a feedback study with one specific decision question, neutral prompts, a defined audience/build/window, a voluntary notice, a short retention period, and a named owner role. Prefer structured categories and observed task outcomes over free text. Do not collect usernames, account IDs, email addresses, contact details, IPs, device fingerprints, precise location, credentials, or persistent cross-study identifiers in research datasets. Keep raw source material in an approved access-controlled system; put only study-scoped opaque references and coarse codes in project files. Route safety disclosures and security/production incidents through their separate human workflows. Report descriptive coded-submission counts only, suppress small cells, and do not claim the sample represents all players. V44 CLI is offline and cannot inspect raw text, detect PII, verify consent/deletion, authenticate evidence, or create external tasks. Human review is required.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path) -> int:
    root = package_root.expanduser().resolve()
    source = source_root.expanduser().resolve()
    repository = source.parent
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    version_file = source / "VERSION"
    if not version_file.is_file() or version_file.read_text(encoding="utf-8").strip() != "44.0.0":
        raise ValueError("V44 source VERSION must be 44.0.0.")
    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected four V44 skills; found {len(skills)}.")

    skills_root = root / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    count = len(list(skills_root.glob("*/SKILL.md")))
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (skills_root / name / "SKILL.md").is_file()}
    if count == 276 and collisions:
        raise ValueError("V44 skill collision(s): " + ", ".join(sorted(collisions)))
    if count == 280 and collisions != names:
        raise ValueError("Already-patched V44 package has an incomplete skill set.")
    if count not in {276, 280}:
        raise ValueError(f"Expected 276 V43 skills or 280 already-patched skills; found {count}.")

    shutil.copytree(
        source, root / "v44", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "test-output"),
    )
    for skill in skills:
        target = skills_root / skill.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target / "SKILL.md")

    # Carry forward the newest compatibility auditors from this repository checkout.
    for number in range(37, 44):
        auditor = repository / f"v{number}" / "tools" / "audit_cumulative_package.py"
        if auditor.is_file():
            target = root / f"v{number}" / "tools" / "audit_cumulative_package.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(auditor, target)

    agents = root / "AGENTS.md"
    if not agents.is_file():
        agents.write_text("# Codex project instructions\n", encoding="utf-8")
    agent_text = agents.read_text(encoding="utf-8")
    if MARKER not in agent_text:
        agents.write_text(agent_text.rstrip() + "\n\n" + GUIDANCE, encoding="utf-8")

    names_to_copy = ["README.md", "INDEX.md", "tools/repository_audit.py"]
    names_to_copy += [f"INDEX_V{number}.md" for number in range(37, 45)]
    names_to_copy += [f"RELEASE_NOTES_V{number}.md" for number in range(37, 45)]
    for name in names_to_copy:
        candidate = repository / name
        if candidate.is_file():
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, destination)

    final_count = len(list(skills_root.glob("*/SKILL.md")))
    if final_count != 280:
        raise ValueError(f"Expected 280 cumulative native Codex skills; found {final_count}.")
    print(f"PASS: installed V44; cumulative native skills={final_count}.")
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
