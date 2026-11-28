#!/usr/bin/env python3
"""Audit the reconstructed cumulative V1-V44 package."""
from __future__ import annotations

import argparse
from pathlib import Path

EXPECTED_SKILLS = 280
HISTORICAL = (
    "207 native Codex skills", "210 native Codex skills", "213 native Codex skills",
    "216 native Codex skills", "220 native Codex skills", "224 native Codex skills",
    "228 native Codex skills", "232 native Codex skills", "236 native Codex skills",
    "240 native Codex skills", "244 native Codex skills", "248 native Codex skills",
    "252 native Codex skills", "256 native Codex skills", "260 native Codex skills",
    "264 native Codex skills", "268 native Codex skills", "272 native Codex skills",
    "276 native Codex skills", "280 native Codex skills",
)
REQUIRED = (
    "AGENTS.md", "README.md", "LICENSE", "INDEX.md", "INDEX_V37.md", "INDEX_V38.md",
    "INDEX_V39.md", "INDEX_V40.md", "INDEX_V41.md", "INDEX_V42.md", "INDEX_V43.md", "INDEX_V44.md",
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
    "v43/schemas/experiment-plan.schema.json", "v43/schemas/experiment-results-review.schema.json",
    "v43/examples/experiment-plan.example.json", "v43/examples/experiment-results.example.json",
    "v44/VERSION", "v44/INDEX_V44.md", "v44/tools/v44.py",
    "v44/tools/patch_cumulative_package.py", "v44/tools/audit_cumulative_package.py",
    "v44/tests/test_v44.py", "v44/tests/requirements-test.txt",
    "v44/schemas/feedback-study.schema.json", "v44/schemas/feedback-data.schema.json",
    "v44/examples/feedback-study.example.json", "v44/examples/feedback-data.example.json",
    "v44/docs/FEEDBACK_STUDY_DESIGN.md", "v44/docs/PRIVACY_CONSCIOUS_FEEDBACK.md",
    "v44/docs/QUALITATIVE_CODING_AND_SYNTHESIS.md",
    "v44/docs/FEEDBACK_TRIAGE_AND_TRACEABILITY.md", "v44/docs/V44_CLI.md",
    ".agents/skills/roblox-player-feedback-study-design/SKILL.md",
    ".agents/skills/roblox-privacy-conscious-feedback-collection/SKILL.md",
    ".agents/skills/roblox-playtest-feedback-thematic-analysis/SKILL.md",
    ".agents/skills/roblox-feedback-triage-and-action-traceability/SKILL.md",
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
    version_path = root / "v44" / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if version != "44.0.0":
        issues.append(f"Unexpected V44 version: {version!r}.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "Current release: V44.0.0" not in readme or "280 native Codex skills" not in readme:
        issues.append("README does not describe V44.0.0 and 280 native skills.")
    missing = [label for label in HISTORICAL if label not in readme]
    if missing:
        issues.append("README is missing historical skill totals: " + ", ".join(missing) + ".")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "<!-- V44_PLAYER_FEEDBACK_RESEARCH_OPERATIONS -->" not in agents:
        issues.append("AGENTS.md is missing V44 feedback-research guidance.")
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
    print(f"PASS: cumulative V1-V44 package audit ({EXPECTED_SKILLS} native skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
