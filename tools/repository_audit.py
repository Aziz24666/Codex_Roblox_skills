#!/usr/bin/env python3
"""Repository/package audit for syntax, structured data, skill metadata, and local links."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

EXPECTED_SKILLS_V25 = 207
EXPECTED_SKILLS_V26 = 210
EXPECTED_SKILLS_V27 = 213
EXPECTED_SKILLS_V28 = 216
EXPECTED_SKILLS_V29 = 220
EXPECTED_SKILLS_V30 = 224
EXPECTED_SKILLS_V31 = 228
EXPECTED_SKILLS_V32 = 232
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".venv", "venv"}
SKILL_METADATA = {
    "name": re.compile(r"(?m)^name\s*:\s*['\"]?([a-z0-9][a-z0-9-]*)['\"]?\s*$"),
    "description": re.compile(r"(?m)^description\s*:\s*(\S.*)$"),
}


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def markdown_targets(path: Path):
    text = path.read_text(encoding="utf-8")
    in_fence = False
    fence_token = None
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if not in_fence:
                in_fence, fence_token = True, token
            elif token == fence_token:
                in_fence, fence_token = False, None
            continue
        if in_fence:
            continue

        # Parse ordinary and image-style inline links without treating Markdown
        # code examples as links. Angle-bracket destinations may contain spaces.
        search_from = 0
        while True:
            marker = line.find("](", search_from)
            if marker < 0:
                break
            label_start = line.rfind("[", 0, marker)
            if label_start < 0:
                search_from = marker + 2
                continue
            target_start = marker + 2
            if target_start < len(line) and line[target_start] == "<":
                target_end = line.find(">", target_start + 1)
                close = line.find(")", target_end + 1) if target_end >= 0 else -1
                target = line[target_start + 1:target_end] if target_end >= 0 else ""
            else:
                close = line.find(")", target_start)
                raw = line[target_start:close] if close >= 0 else ""
                target = raw.split(None, 1)[0] if raw else ""
            if close < 0:
                search_from = marker + 2
                continue
            yield line_number, target
            search_from = close + 1


def audit(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return [f"Package root is not a directory: {root}"]

    problems: list[str] = []
    files = list(iter_files(root))
    python_count = json_count = markdown_count = 0

    for path in files:
        relative = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        try:
            if suffix == ".py":
                python_count += 1
                compile(path.read_text(encoding="utf-8"), relative, "exec")
            elif suffix == ".json":
                json_count += 1
                json.loads(path.read_text(encoding="utf-8"))
            elif suffix in {".md", ".markdown"}:
                markdown_count += 1
                for line_number, raw_target in markdown_targets(path):
                    target = unquote(raw_target.strip())
                    if not target or target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                        continue
                    target_path = target.split("#", 1)[0].split("?", 1)[0]
                    if not target_path:
                        continue
                    # Earlier cumulative overlays may carry the current README/INDEX
                    # before the V29 overlay is installed. Defer only V29-local links
                    # until its VERSION marker exists; the final V29 audit checks them.
                    if not (root / "v32" / "VERSION").is_file() and (
                        target_path == "INDEX_V32.md" or target_path.startswith("v32/")
                    ):
                        continue
                    if not (root / "v31" / "VERSION").is_file() and (
                        target_path == "INDEX_V31.md" or target_path.startswith("v31/")
                    ):
                        continue
                    if not (root / "v29" / "VERSION").is_file() and (
                        target_path == "INDEX_V29.md" or target_path.startswith("v29/")
                    ):
                        continue
                    candidate = root / target_path.lstrip("/") if target_path.startswith("/") else path.parent / target_path
                    try:
                        resolved = candidate.resolve()
                        if not resolved.is_relative_to(root) or not resolved.exists():
                            problems.append(f"Broken or out-of-package Markdown link: {relative}:{line_number} -> {raw_target}")
                    except (OSError, RuntimeError, ValueError):
                        problems.append(f"Unsafe Markdown link: {relative}:{line_number} -> {raw_target}")
        except (OSError, UnicodeError, SyntaxError, json.JSONDecodeError, ValueError) as exc:
            problems.append(f"Invalid {suffix or 'file'} {relative}: {exc}")

    skills_root = root / ".agents" / "skills"
    skills = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    is_v28 = (root / "v28" / "VERSION").is_file()
    is_v29 = (root / "v29" / "VERSION").is_file()
    is_v30 = (root / "v30" / "VERSION").is_file()
    is_v31 = (root / "v31" / "VERSION").is_file()
    is_v32 = (root / "v32" / "VERSION").is_file()
    is_v27 = (root / "v27" / "VERSION").is_file()
    is_v26 = (root / "v26" / "VERSION").is_file()
    expected_skills = EXPECTED_SKILLS_V32 if is_v32 else (EXPECTED_SKILLS_V31 if is_v31 else (EXPECTED_SKILLS_V30 if is_v30 else (EXPECTED_SKILLS_V29 if is_v29 else (EXPECTED_SKILLS_V28 if is_v28 else (
        EXPECTED_SKILLS_V27 if is_v27 else (
            EXPECTED_SKILLS_V26 if is_v26 else EXPECTED_SKILLS_V25
        )
    ))))
    if len(skills) != expected_skills:
        problems.append(f"Expected {expected_skills} native skills, found {len(skills)}.")
    names: dict[str, str] = {}
    for skill in skills:
        relative = skill.relative_to(root).as_posix()
        try:
            content = skill.read_text(encoding="utf-8")
            match = re.match(r"^---\s*\n(.*?)\n---(?:\s|$)", content, re.S)
            if not match:
                problems.append(f"Skill is missing YAML frontmatter: {relative}")
                continue
            metadata = match.group(1)
            name_match = SKILL_METADATA["name"].search(metadata)
            description_match = SKILL_METADATA["description"].search(metadata)
            if not name_match or not description_match:
                problems.append(f"Skill metadata needs a valid name and description: {relative}")
                continue
            name = name_match.group(1)
            if name in names:
                problems.append(f"Duplicate skill name {name!r}: {names[name]} and {relative}")
            names[name] = relative
        except (OSError, UnicodeError) as exc:
            problems.append(f"Could not read skill {relative}: {exc}")

    required = (
        "AGENTS.md", "README.md", "LICENSE", "INDEX_V25.md",
        "v23/tools/v23.py", "v23/tests/test_v23.py",
        "v23/schemas/opportunity-discovery-report.schema.json",
        "v25/tools/v25.py", "v25/tests/test_v25.py",
    )
    if is_v26:
        required += (
            "INDEX_V26.md", "v26/VERSION", "v26/tools/v26.py", "v26/tests/test_v26.py",
            "v26/tools/audit_cumulative_package.py", "v26/docs/STUDIO_MCP_WORKFLOW.md",
        )
    if is_v27:
        required += (
            "INDEX_V27.md", "v27/VERSION", "v27/tools/v27.py", "v27/tests/test_v27.py",
            "v27/tools/audit_cumulative_package.py", "v27/docs/LUAU_STATIC_ANALYSIS.md",
            "v27/docs/ROJO_PROJECT_VALIDATION.md",
        )
    if is_v28:
        required += (
            "INDEX_V28.md", "v28/VERSION", "v28/tools/v28.py", "v28/tests/test_v28.py",
            "v28/tools/audit_cumulative_package.py",
            "v28/docs/SERVER_AUTHORITY_AND_REMOTE_SECURITY.md",
            "v28/docs/DATASTORE_MIGRATION_SAFETY.md",
            "v28/docs/MULTIPLAYER_RELIABILITY_VALIDATION.md",
        )
    if is_v29:
        required += (
            "INDEX_V29.md", "v29/VERSION", "v29/INDEX_V29.md", "v29/tools/v29.py", "v29/tests/test_v29.py",
            "v29/tools/audit_cumulative_package.py", "v29/docs/PERFORMANCE_ENGINEERING.md",
            "v29/docs/DEVICE_PERFORMANCE_BUDGETS.md", "v29/docs/PROFILING_AND_REGRESSION_EVIDENCE.md",
        )
    if is_v30:
        required += (
            "INDEX_V30.md", "v30/VERSION", "v30/INDEX_V30.md", "v30/tools/v30.py",
            "v30/tools/patch_cumulative_package.py", "v30/tools/audit_cumulative_package.py",
            "v30/tests/test_v30.py", "v30/docs/PRODUCTION_RELEASE_READINESS.md",
            "v30/docs/RELEASE_EVIDENCE_AND_ROLLBACK.md",
            "v30/schemas/release-plan.schema.json", "v30/schemas/release-report.schema.json",
            "v30/examples/release-plan.staging.example.json",
        )
    if is_v31:
        required += (
            "INDEX_V31.md", "v31/VERSION", "v31/INDEX_V31.md", "v31/tools/v31.py",
            "v31/tools/patch_cumulative_package.py", "v31/tools/audit_cumulative_package.py",
            "v31/tests/test_v31.py", "v31/docs/ANALYTICS_EVENT_GOVERNANCE.md",
            "v31/docs/AGGREGATE_GAME_HEALTH_AND_LIVEOPS.md",
            "v31/schemas/event-catalog.schema.json", "v31/schemas/health-policy.schema.json",
            "v31/schemas/health-snapshot.schema.json",
            "v31/examples/event-catalog.example.json", "v31/examples/health-policy.example.json",
            "v31/examples/health-snapshot.example.json",
        )
    if is_v32:
        required += (
            "INDEX_V32.md", "v32/VERSION", "v32/INDEX_V32.md", "v32/tools/v32.py",
            "v32/tools/patch_cumulative_package.py", "v32/tools/audit_cumulative_package.py",
            "v32/tests/test_v32.py", "v32/docs/TEXT_FILTERING_AND_UGC.md",
            "v32/docs/MODERATION_AND_APPEALS.md", "v32/docs/PLAYER_SAFETY_BY_DESIGN.md",
            "v32/schemas/moderation-policy.schema.json", "v32/schemas/moderation-case.schema.json",
            "v32/schemas/moderation-register.schema.json",
            "v32/examples/moderation-policy.example.json", "v32/examples/moderation-case.example.json",
            "v32/examples/moderation-register.example.json",
        )
    for item in required:
        if not (root / item).is_file():
            problems.append(f"Missing required cumulative-package file: {item}")

    print(
        f"Audited {len(files)} files: {python_count} Python, {json_count} JSON, "
        f"{markdown_count} Markdown; {len(skills)} skills."
    )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Reconstructed cumulative package root.")
    args = parser.parse_args()
    problems = audit(args.root)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print("PASS: repository/package audit completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
