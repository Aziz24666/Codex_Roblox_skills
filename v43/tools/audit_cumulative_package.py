#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V43 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 276
HISTORICAL = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
    "252 native Codex skills", "256 native Codex skills", "260 native Codex skills",
    "264 native Codex skills", "268 native Codex skills", "272 native Codex skills",
    "276 native Codex skills",
)
REQUIRED = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md",
    "INDEX_V37.md", "INDEX_V38.md", "INDEX_V39.md", "INDEX_V40.md",
    "INDEX_V41.md", "INDEX_V42.md", "INDEX_V43.md",
    "tools/repository_audit.py",
    "v37/VERSION", "v37/tools/v37.py", "v37/tools/audit_cumulative_package.py",
    "v38/VERSION", "v38/tools/v38.py", "v38/tools/audit_cumulative_package.py",
    "v39/VERSION", "v39/tools/v39.py", "v39/tools/audit_cumulative_package.py",
    "v40/VERSION", "v40/tools/v40.py", "v40/tools/audit_cumulative_package.py",
    "v41/VERSION", "v41/tools/v41.py", "v41/tools/audit_cumulative_package.py",
    "v42/VERSION", "v42/tools/v42.py", "v42/tools/audit_cumulative_package.py",
    "v43/VERSION", "v43/INDEX_V43.md", "v43/tools/v43.py",
    "v43/tools/patch_cumulative_package.py", "v43/tools/audit_cumulative_package.py",
    "v43/tests/test_v43.py", "v43/tests/requirements-test.txt",
    "v43/schemas/experiment-plan.schema.json",
    "v43/schemas/experiment-results-review.schema.json",
    "v43/examples/experiment-plan.example.json",
    "v43/examples/experiment-results.example.json",
    "v43/docs/EXPERIMENT_DESIGN_AND_METRICS.md",
    "v43/docs/ROBLOX_EXPERIMENTS_OPEN_CLOUD.md",
    "v43/docs/ANALYTICS_INSTRUMENTATION.md",
    "v43/docs/STATISTICAL_REVIEW_AND_DECISIONS.md", "v43/docs/V43_CLI.md",
    ".agents/skills/roblox-experiment-hypothesis-and-design/SKILL.md",
    ".agents/skills/roblox-native-experiments-and-open-cloud-lifecycle/SKILL.md",
    ".agents/skills/roblox-experiment-analytics-instrumentation/SKILL.md",
    ".agents/skills/roblox-experiment-results-and-decision-review/SKILL.md",
)


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return ["Package root is not a directory."]
    issues = [f"Missing required file: {path}" for path in REQUIRED if not (root / path).is_file()]
    skills_root = root / ".agents" / "skills"
    skills = list(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if len(skills) != EXPECTED_SKILLS:
        issues.append(f"Expected {EXPECTED_SKILLS} native skills; found {len(skills)}.")
    version = (root / "v43" / "VERSION").read_text(encoding="utf-8").strip() if (root / "v43" / "VERSION").is_file() else ""
    if version != "43.0.0":
        issues.append(f"Unexpected V43 version: {version!r}.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "Current release: V43.0.0" not in readme or "276 native Codex skills" not in readme:
        issues.append("README does not describe V43 and 276 native skills.")
    missing = [label for label in HISTORICAL if label not in readme]
    if missing:
        issues.append("README is missing historical skill totals: " + ", ".join(missing) + ".")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V43_EXPERIMENTATION_DECISION_INTELLIGENCE -->" not in agents:
        issues.append("AGENTS.md is missing V43 experiment design and analytics guidance.")
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
    print(f"PASS: cumulative V1-V43 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
