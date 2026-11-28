#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V41 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS = {268, 272, 276, 280}
HISTORICAL = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
    "252 native Codex skills", "256 native Codex skills", "260 native Codex skills",
    "264 native Codex skills", "268 native Codex skills", "272 native Codex skills", "276 native Codex skills", "280 native Codex skills",
)
REQUIRED = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md", "INDEX_V41.md",
    "v37/VERSION", "v37/tools/v37.py", "v37/tools/audit_cumulative_package.py",
    "v38/VERSION", "v38/tools/v38.py", "v38/tools/audit_cumulative_package.py",
    "v39/VERSION", "v39/tools/v39.py", "v39/tools/audit_cumulative_package.py",
    "v40/VERSION", "v40/tools/v40.py", "v40/tools/audit_cumulative_package.py",
    "v41/VERSION", "v41/INDEX_V41.md", "v41/tools/v41.py", "v41/tools/patch_cumulative_package.py",
    "v41/tools/audit_cumulative_package.py", "v41/tests/test_v41.py",
    "v41/schemas/matchmaking-model.schema.json", "v41/examples/matchmaking-model.example.json",
    "v41/docs/MATCHMAKING_ARCHITECTURE.md", "v41/docs/PARTIES_AND_LOBBY_LIFECYCLE.md",
    "v41/docs/TELEPORT_AND_RECOVERY.md", "v41/docs/V41_CLI.md",
    ".agents/skills/roblox-skill-based-matchmaking-queue-design/SKILL.md",
    ".agents/skills/roblox-party-and-lobby-lifecycle/SKILL.md",
    ".agents/skills/roblox-cross-server-matchmaking-coordination/SKILL.md",
    ".agents/skills/roblox-teleport-reconnect-and-server-handoff/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return ["Package root is not a directory."]
    issues = [f"Missing required file: {path}" for path in REQUIRED if not (root / path).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = list(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) not in EXPECTED_SKILLS:
        issues.append(f"Expected {EXPECTED_SKILLS} native skills; found {len(skills)}.")
    version = (root / "v41" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v41" / "VERSION").is_file() else ""
    if version != "41.0.0":
        issues.append(f"Unexpected V41 version: {version!r}.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if not any(label in readme for label in ("Current release: V41.0.0", "Current release: V42.0.0", "Current release: V43.0.0", "Current release: V44.0.0")) or not any(label in readme for label in ("268 native Codex skills", "272 native Codex skills", "276 native Codex skills", "280 native Codex skills")):
        issues.append("README does not describe V41 and 268 native skills.")
    missing = [label for label in HISTORICAL if label not in readme]
    if missing:
        issues.append("README is missing historical skill totals: " + ", ".join(missing) + ".")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V41_MATCHMAKING_PARTY_MULTIPLAYER_ORCHESTRATION -->" not in agents:
        issues.append("AGENTS.md is missing V41 matchmaking and orchestration guidance.")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    issues = audit(args.root)
    if issues:
        for issue in issues:
            print("FAIL: " + issue)
        return 1
    count = len(list((args.root.expanduser().resolve() / ".agents" / "skills").glob("*/SKILL.md")))
    print(f"PASS: cumulative V1-V41 compatibility audit ({count} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
