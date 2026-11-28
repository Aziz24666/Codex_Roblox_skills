#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V40 package."""
from __future__ import annotations
import argparse
from pathlib import Path

EXPECTED_SKILLS = {264, 268, 272, 276}
HISTORICAL = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
    "252 native Codex skills", "256 native Codex skills", "260 native Codex skills",
    "264 native Codex skills", "268 native Codex skills", "272 native Codex skills", "276 native Codex skills",
)
REQUIRED = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md",
    "v37/VERSION", "v37/tools/v37.py", "v37/tools/audit_cumulative_package.py",
    "v38/VERSION", "v38/tools/v38.py", "v38/tools/audit_cumulative_package.py",
    "v39/VERSION", "v39/tools/v39.py", "v39/tools/audit_cumulative_package.py",
    "v40/VERSION", "v40/INDEX_V40.md", "v40/tools/v40.py", "v40/tools/patch_cumulative_package.py",
    "v40/tools/audit_cumulative_package.py", "v40/tests/test_v40.py",
    "v40/schemas/persistence-model.schema.json", "v40/examples/persistence-model.example.json",
    "v40/docs/PERSISTENCE_ARCHITECTURE.md", "v40/docs/MIGRATIONS_AND_RECEIPTS.md", "v40/docs/PERSISTENCE_CLI.md",
    ".agents/skills/roblox-profile-lifecycle-and-session-ownership/SKILL.md",
    ".agents/skills/roblox-resilient-data-saving-and-recovery/SKILL.md",
    ".agents/skills/roblox-safe-profile-schema-migrations/SKILL.md",
    ".agents/skills/roblox-idempotent-rewards-and-receipt-processing/SKILL.md",
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
    version = (root / "v40" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v40" / "VERSION").is_file() else ""
    if version != "40.0.0":
        issues.append(f"Unexpected V40 version: {version!r}.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if not any(label in readme for label in ("Current release: V40.0.0", "Current release: V41.0.0", "Current release: V42.0.0", "Current release: V43.0.0")) or not any(label in readme for label in ("264 native Codex skills", "268 native Codex skills", "272 native Codex skills", "276 native Codex skills")):
        issues.append("README does not describe V40 and 264 native skills.")
    missing = [label for label in HISTORICAL if label not in readme]
    if missing:
        issues.append("README is missing historical skill totals: " + ", ".join(missing) + ".")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V40_DATA_PERSISTENCE_TRANSACTION_INTEGRITY -->" not in agents:
        issues.append("AGENTS.md is missing V40 persistence and transaction guidance.")
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
    print(f"PASS: cumulative V1-V40 compatibility audit ({count} native skills).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
