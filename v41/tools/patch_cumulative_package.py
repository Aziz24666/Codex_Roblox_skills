#!/usr/bin/env python3
"""Install V41 into a verified cumulative V1-V40 package."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

MARKER = "<!-- V41_MATCHMAKING_PARTY_MULTIPLAYER_ORCHESTRATION -->"
GUIDANCE = """<!-- V41_MATCHMAKING_PARTY_MULTIPLAYER_ORCHESTRATION -->
## V41 matchmaking, parties, and multiplayer orchestration
Use V41 for server-authoritative party membership, indivisible queue tickets, MemoryStore-based ephemeral matchmaking/assignment state, lease/version/fencing checks, and recoverable server-side TeleportAsync handoffs. Keep durable player progress in DataStores; MessagingService is best-effort notification only. Remove queue entries only after assignment is safely claimed. TeleportData is visible and unencrypted: pass only opaque non-sensitive references, then revalidate them at the destination. V41's validator/auditor and deterministic simulator process declared JSON and synthetic tickets only; they do not call Roblox services, run Studio, test real teleportation, or prove production fairness/concurrency safety.
""".strip() + "\n"


def patch(package_root: Path, source_root: Path) -> int:
    root = package_root.expanduser().resolve()
    source = source_root.expanduser().resolve()
    repository = source.parent
    if not root.is_dir():
        raise ValueError("Cumulative package root must exist.")
    if (source / "VERSION").read_text(encoding="utf-8").strip() != "41.0.0":
        raise ValueError("V41 source VERSION must be 41.0.0.")
    skills = sorted((source / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise ValueError(f"Expected four V41 skills; found {len(skills)}.")
    skills_root = root / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    count = len(list(skills_root.glob("*/SKILL.md")))
    names = {skill.parent.name for skill in skills}
    collisions = {name for name in names if (skills_root / name / "SKILL.md").is_file()}
    if count == 264 and collisions:
        raise ValueError("V41 skill collision(s): " + ", ".join(sorted(collisions)))
    if count == 268 and collisions != names:
        raise ValueError("Already-patched V41 package has an incomplete skill set.")
    if count not in {264, 268}:
        raise ValueError(f"Expected 264 V40 skills or 268 already-patched skills; found {count}.")

    shutil.copytree(source, root / "v41", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "test-output"))
    for skill in skills:
        target = skills_root / skill.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target / "SKILL.md")

    for version in ("v37", "v38", "v39", "v40"):
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
        "README.md", "INDEX.md", "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md", "INDEX_V41.md",
        "RELEASE_NOTES_V37.md", "RELEASE_NOTES_V38.md", "RELEASE_NOTES_V39.md", "RELEASE_NOTES_V40.md", "RELEASE_NOTES_V41.md",
    )
    for name in names_to_copy:
        candidate = repository / name
        if candidate.is_file():
            shutil.copy2(candidate, root / name)

    final_count = len(list(skills_root.glob("*/SKILL.md")))
    if final_count != 268:
        raise ValueError(f"Expected 268 cumulative native Codex skills; found {final_count}.")
    print(f"PASS: installed V41; cumulative native skills={final_count}.")
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
