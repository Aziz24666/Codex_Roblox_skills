#!/usr/bin/env python3
"""Audit V36 content inside a cumulative V1-V36-or-later package."""
from __future__ import annotations

import argparse
from pathlib import Path

MINIMUM_SKILLS = 248
HISTORICAL_SKILL_LABELS = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
)
REQUIRED = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX_V36.md",
    "v36/VERSION", "v36/INDEX_V36.md", "v36/tools/v36.py",
    "v36/tools/patch_cumulative_package.py", "v36/tools/audit_cumulative_package.py",
    "v36/tests/test_v36.py", "v36/docs/ACCESSIBILITY_AND_INTERACTION_REVIEW.md",
    "v36/docs/LOCALIZATION_AND_RESPONSIVE_UI.md", "v36/docs/QUALITY_MANIFEST_AND_AUDIT.md",
    "v36/examples/quality-manifest.example.json",
    ".agents/skills/roblox-accessibility-and-inclusive-interaction-v36/SKILL.md",
    ".agents/skills/roblox-responsive-ui-and-readability-v36/SKILL.md",
    ".agents/skills/roblox-localization-and-rtl-readiness-v36/SKILL.md",
    ".agents/skills/roblox-sensory-feedback-and-motion-settings-v36/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return ["Package root does not exist."]
    issues = [f"Missing required file: {path}" for path in REQUIRED if not (root / path).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) < MINIMUM_SKILLS:
        issues.append(f"Expected at least {MINIMUM_SKILLS} native skills for V36; found {len(skills)}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V36_ACCESSIBILITY_LOCALIZATION -->" not in agents:
        issues.append("AGENTS.md lacks V36 guidance.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    missing = [label for label in HISTORICAL_SKILL_LABELS if label not in readme]
    if missing:
        issues.append("README.md is missing cumulative compatibility labels: " + ", ".join(missing) + ".")
    version = (root / "v36" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v36" / "VERSION").is_file() else ""
    if version != "36.0.0":
        issues.append(f"Unexpected V36 source version: {version!r}.")
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
    skills_root = args.root.expanduser().resolve() / ".agents" / "skills"
    count = len(list(skills_root.glob("*/SKILL.md")))
    print(f"PASS: V36 content audit inside cumulative package ({count} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
