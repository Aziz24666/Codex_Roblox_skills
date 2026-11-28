#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V37 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = {252, 256, 260, 264, 268, 272, 276, 280, 284}
HISTORICAL_SKILL_LABELS = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
    "252 native Codex skills", "256 native Codex skills", "260 native Codex skills", "264 native Codex skills", "268 native Codex skills", "272 native Codex skills", "276 native Codex skills", "280 native Codex skills", "284 native Codex skills",
)
REQUIRED_FILES = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V36.md", "INDEX_V37.md",
    "tools/repository_audit.py",
    "v36/VERSION", "v36/tools/v36.py", "v36/tools/audit_cumulative_package.py",
    "v37/VERSION", "v37/INDEX_V37.md", "v37/tools/v37.py",
    "v37/tools/patch_cumulative_package.py", "v37/tools/audit_cumulative_package.py",
    "v37/tests/test_v37.py", "v37/docs/PROJECT_RECONNAISSANCE_AND_CHANGE_IMPACT.md",
    "v37/docs/FEATURE_PLANNING_AND_DEPENDENCY_GRAPHS.md",
    "v37/docs/IMPLEMENTATION_EVIDENCE_AND_HANDOFF.md", "v37/docs/PLAN_AND_REPORT_CLI.md",
    "v37/schemas/implementation-plan.schema.json", "v37/schemas/implementation-report.schema.json",
    "v37/examples/implementation-plan.example.json", "v37/examples/implementation-report.example.json",
    ".agents/skills/roblox-project-reconnaissance-and-architecture-mapping-v37/SKILL.md",
    ".agents/skills/roblox-feature-decomposition-and-dependency-planning-v37/SKILL.md",
    ".agents/skills/roblox-scoped-implementation-and-change-impact-v37/SKILL.md",
    ".agents/skills/roblox-implementation-verification-and-handoff-v37/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return [f"Package root is not a directory: {root}"]
    issues = [f"Missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) not in EXPECTED_SKILLS:
        issues.append(f"Expected a V37-or-newer cumulative skill count {sorted(EXPECTED_SKILLS)}, found {len(skills)}.")
    version = (root / "v37" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v37" / "VERSION").is_file() else ""
    if version != "37.0.0":
        issues.append(f"Unexpected V37 version: {version!r}.")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V37_PROJECT_IMPLEMENTATION_ORCHESTRATION -->" not in agents:
        issues.append("AGENTS.md is missing the V37 project implementation orchestration guidance.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    current_release = any(label in readme for label in ("Current release: V37.0.0", "Current release: V38.0.0", "Current release: V39.0.0", "Current release: V40.0.0", "Current release: V41.0.0", "Current release: V42.0.0", "Current release: V43.0.0", "Current release: V44.0.0", "Current release: V45.0.0", "Current release: V45.0.0 (proposed)"))
    current_count = any(label in readme for label in ("252 native Codex skills", "256 native Codex skills", "260 native Codex skills", "264 native Codex skills", "268 native Codex skills", "272 native Codex skills", "276 native Codex skills", "280 native Codex skills", "284 native Codex skills"))
    if not current_release or not current_count:
        issues.append("README.md does not describe a V37-or-newer cumulative package.")
    missing_labels = [label for label in HISTORICAL_SKILL_LABELS if label not in readme]
    if missing_labels:
        issues.append("README.md is missing historical compatibility labels: " + ", ".join(missing_labels) + ".")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    problems = audit(args.root)
    if problems:
        for item in problems:
            print("FAIL: " + item)
        return 1
    count = len(list((args.root.expanduser().resolve() / ".agents" / "skills").glob("*/SKILL.md")))
    print(f"PASS: V37 compatibility audit ({count} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
