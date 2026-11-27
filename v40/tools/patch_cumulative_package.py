#!/usr/bin/env python3
"""Install V40 into a verified cumulative V1-V39 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V40_DATA_PERSISTENCE_TRANSACTION_INTEGRITY -->"
GUIDANCE = """<!-- V40_DATA_PERSISTENCE_TRANSACTION_INTEGRITY -->
## V40 advanced data persistence and transaction integrity
Use V40 to define server-authoritative profile lifecycle, per-key session ownership, bounded retry and autosave policies, schema migration chains, and idempotent reward/receipt commits. Keep same-profile mutations and deduplication markers in one UpdateAsync transform where atomicity is required. Use PurchaseId for developer-product receipt idempotency; expect redelivery and concurrent callbacks. Acknowledge only after durable commit; reconcile unknown write outcomes before retrying. Use isolated test experiences for Studio DataStore access and production migrations. V40 validates declared JSON metadata only; it does not inspect Luau, connect to Roblox services, verify backups, or prove that locks and writes are race-free.
""".strip() + "\n"

def patch(package_root: Path, source_root: Path) -> int:
    root = package_root.expanduser().resolve()
    source = source_root.expanduser().resolve()
    repository = source.parent
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    if (source / "VERSION").read_text(encoding="utf-8").strip() != "40.0.0":
        raise ValueError("V40 source VERSION must be 40.0.0.")
    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected four V40 skills; found {len(skills)}.")
    skills_root = root / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    count = len(list(skills_root.glob("*/SKILL.md")))
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (skills_root / name / "SKILL.md").is_file()}
    if count == 260 and collisions:
        raise ValueError("V40 skill collision(s): " + ", ".join(sorted(collisions)))
    if count == 264 and collisions != names:
        raise ValueError("Already-patched V40 package has an incomplete skill set.")
    if count not in {260, 264}:
        raise ValueError(f"Expected 260 V39 skills or 264 already-patched skills; found {count}.")
    shutil.copytree(source, root / "v40", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for skill in skills:
        target = skills_root / skill.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target / "SKILL.md")
    for version in ("v37", "v38", "v39"):
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
    for name in (
        "README.md", "INDEX.md", "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md",
        "RELEASE_NOTES_V37.md", "RELEASE_NOTES_V38.md", "RELEASE_NOTES_V39.md", "RELEASE_NOTES_V40.md",
    ):
        candidate = repository / name
        if candidate.is_file():
            shutil.copy2(candidate, root / name)
    final_count = len(list(skills_root.glob("*/SKILL.md")))
    if final_count != 264:
        raise ValueError(f"Expected 264 cumulative native Codex skills; found {final_count}.")
    print(f"PASS: installed V40; cumulative native skills={final_count}.")
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
