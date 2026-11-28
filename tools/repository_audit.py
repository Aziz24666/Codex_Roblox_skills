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
EXPECTED_SKILLS_V33 = 236
EXPECTED_SKILLS_V34 = 240
EXPECTED_SKILLS_V35 = 244
EXPECTED_SKILLS_V36 = 248
EXPECTED_SKILLS_V37 = 252
EXPECTED_SKILLS_V38 = 256
EXPECTED_SKILLS_V39 = 260
EXPECTED_SKILLS_V40 = 264
EXPECTED_SKILLS_V41 = 268
EXPECTED_SKILLS_V42 = 272
EXPECTED_SKILLS_V43 = 276
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
                    if not (root / "v35" / "VERSION").is_file() and (
                        target_path == "INDEX_V35.md" or target_path.startswith("v35/")
                    ):
                        continue
                    # A current README can be copied into an older cumulative overlay
                    # before the newer version directories have been installed. Defer
                    # those future-version links until the corresponding overlay lands.
                    defer_future_version = False
                    for newer_version in range(43, 35, -1):
                        if not (root / f"v{newer_version}" / "VERSION").is_file() and (
                            target_path == f"INDEX_V{newer_version}.md"
                            or target_path.startswith(f"v{newer_version}/")
                        ):
                            defer_future_version = True
                            break
                    if defer_future_version:
                        continue
                    if not (root / "v34" / "VERSION").is_file() and (
                        target_path == "INDEX_V34.md" or target_path.startswith("v34/")
                    ):
                        continue
                    if not (root / "v33" / "VERSION").is_file() and (
                        target_path == "INDEX_V33.md" or target_path.startswith("v33/")
                    ):
                        continue
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
    is_v33 = (root / "v33" / "VERSION").is_file()
    is_v34 = (root / "v34" / "VERSION").is_file()
    is_v35 = (root / "v35" / "VERSION").is_file()
    is_v36 = (root / "v36" / "VERSION").is_file()
    is_v37 = (root / "v37" / "VERSION").is_file()
    is_v38 = (root / "v38" / "VERSION").is_file()
    is_v39 = (root / "v39" / "VERSION").is_file()
    is_v40 = (root / "v40" / "VERSION").is_file()
    is_v41 = (root / "v41" / "VERSION").is_file()
    is_v42 = (root / "v42" / "VERSION").is_file()
    is_v43 = (root / "v43" / "VERSION").is_file()
    is_v27 = (root / "v27" / "VERSION").is_file()
    is_v26 = (root / "v26" / "VERSION").is_file()
    if is_v43:
        expected_skills = EXPECTED_SKILLS_V43
    elif is_v42:
        expected_skills = EXPECTED_SKILLS_V42
    elif is_v41:
        expected_skills = EXPECTED_SKILLS_V41
    elif is_v40:
        expected_skills = EXPECTED_SKILLS_V40
    elif is_v39:
        expected_skills = EXPECTED_SKILLS_V39
    elif is_v38:
        expected_skills = EXPECTED_SKILLS_V38
    elif is_v37:
        expected_skills = EXPECTED_SKILLS_V37
    elif is_v36:
        expected_skills = EXPECTED_SKILLS_V36
    elif is_v35:
        expected_skills = EXPECTED_SKILLS_V35
    elif is_v34:
        expected_skills = EXPECTED_SKILLS_V34
    elif is_v33:
        expected_skills = EXPECTED_SKILLS_V33
    elif is_v32:
        expected_skills = EXPECTED_SKILLS_V32
    elif is_v31:
        expected_skills = EXPECTED_SKILLS_V31
    elif is_v30:
        expected_skills = EXPECTED_SKILLS_V30
    elif is_v29:
        expected_skills = EXPECTED_SKILLS_V29
    elif is_v28:
        expected_skills = EXPECTED_SKILLS_V28
    elif is_v27:
        expected_skills = EXPECTED_SKILLS_V27
    elif is_v26:
        expected_skills = EXPECTED_SKILLS_V26
    else:
        expected_skills = EXPECTED_SKILLS_V25
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
    if is_v33:
        required += (
            "INDEX_V33.md", "v33/VERSION", "v33/INDEX_V33.md", "v33/tools/v33.py",
            "v33/tools/patch_cumulative_package.py", "v33/tools/audit_cumulative_package.py",
            "v33/tests/test_v33.py", "v33/docs/STUDIO_AUTOMATION.md",
            "v33/docs/MULTIPLAYER_AND_NETWORK_TESTING.md", "v33/docs/DEVICE_AND_INPUT_TESTING.md",
            "v33/docs/TEST_EVIDENCE_AND_REGRESSION.md",
            "v33/schemas/test-plan.schema.json", "v33/schemas/test-report.schema.json",
            "v33/examples/test-plan.example.json", "v33/examples/test-report.example.json",
            "v33/examples/test-report.local-static.example.json",
        )
    if is_v34:
        required += (
            "INDEX_V34.md", "v34/VERSION", "v34/INDEX_V34.md", "v34/tools/v34.py",
            "v34/tools/patch_cumulative_package.py", "v34/tools/audit_cumulative_package.py",
            "v34/tests/test_v34.py", "v34/docs/PERFORMANCE_SOAK_TESTING.md",
            "v34/docs/MICROPROFILER_AND_DASHBOARD_EVIDENCE.md",
            "v34/docs/REPEATED_BENCHMARKS_AND_ROLLOUT.md",
            "v34/schemas/soak-capture.schema.json", "v34/schemas/repeat-suite.schema.json",
            "v34/examples/soak-capture.example.json", "v34/examples/repeat-suite.example.json",
        )
    if is_v35:
        required += (
            "INDEX_V35.md", "v35/VERSION", "v35/INDEX_V35.md", "v35/tools/v35.py",
            "v35/tools/patch_cumulative_package.py", "v35/tools/audit_cumulative_package.py",
            "v35/tests/test_v35.py", "v35/docs/ASSET_CATALOG_AND_PROVENANCE.md",
            "v35/docs/CONTENT_BUDGETS_AND_DEPENDENCIES.md", "v35/docs/ASSET_RELEASE_AND_MIGRATION.md",
            "v35/schemas/asset-catalog.schema.json", "v35/schemas/asset-budget-policy.schema.json",
            "v35/examples/asset-catalog.example.json", "v35/examples/asset-budget-policy.example.json",
        )
    if is_v36:
        required += (
            "INDEX_V36.md", "v36/VERSION", "v36/INDEX_V36.md", "v36/tools/v36.py",
            "v36/tools/patch_cumulative_package.py", "v36/tools/audit_cumulative_package.py",
            "v36/tests/test_v36.py", "v36/docs/ACCESSIBILITY_AND_INTERACTION_REVIEW.md",
            "v36/docs/LOCALIZATION_AND_RESPONSIVE_UI.md", "v36/docs/QUALITY_MANIFEST_AND_AUDIT.md",
            "v36/examples/quality-manifest.example.json",
            ".agents/skills/roblox-accessibility-and-inclusive-interaction-v36/SKILL.md",
            ".agents/skills/roblox-responsive-ui-and-readability-v36/SKILL.md",
            ".agents/skills/roblox-localization-and-rtl-readiness-v36/SKILL.md",
            ".agents/skills/roblox-sensory-feedback-and-motion-settings-v36/SKILL.md",
        )
    if is_v37:
        required += (
            "INDEX_V37.md", "v37/VERSION", "v37/INDEX_V37.md", "v37/tools/v37.py",
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
    if is_v38:
        required += (
            "INDEX_V38.md", "v38/VERSION", "v38/INDEX_V38.md", "v38/tools/v38.py",
            "v38/tools/patch_cumulative_package.py", "v38/tools/audit_cumulative_package.py",
            "v38/tests/test_v38.py", "v38/schemas/incident.schema.json",
            "v38/examples/incident.example.json", "v38/docs/INCIDENT_TRIAGE_AND_SERVICE_HEALTH.md",
            "v38/docs/MITIGATION_APPROVAL_AND_ROLLBACK.md", "v38/docs/COMMUNICATION_AND_POSTMORTEM.md",
            "v38/docs/INCIDENT_CLI.md",
            ".agents/skills/roblox-production-incident-triage-and-severity-assessment/SKILL.md",
            ".agents/skills/roblox-privacy-safe-service-health-and-impact-analysis/SKILL.md",
            ".agents/skills/roblox-safe-mitigation-approval-and-recovery/SKILL.md",
            ".agents/skills/roblox-player-communications-and-postmortem-readiness/SKILL.md",
        )
    if is_v39:
        required += (
            "INDEX_V39.md", "v39/VERSION", "v39/INDEX_V39.md", "v39/tools/v39.py",
            "v39/tools/patch_cumulative_package.py", "v39/tools/audit_cumulative_package.py",
            "v39/tests/test_v39.py", "v39/schemas/economy-model.schema.json",
            "v39/examples/economy-model.example.json", "v39/docs/ECONOMY_MODEL_DESIGN.md",
            "v39/docs/INTERPRETING_SIMULATION_RESULTS.md", "v39/docs/ECONOMY_CLI.md",
            ".agents/skills/roblox-economy-source-and-sink-architecture/SKILL.md",
            ".agents/skills/roblox-deterministic-economy-simulation/SKILL.md",
            ".agents/skills/roblox-progression-pacing-and-reward-curves/SKILL.md",
            ".agents/skills/roblox-economy-fairness-and-abuse-review/SKILL.md",
        )
    if is_v40:
        required += (
            "INDEX_V40.md", "v40/VERSION", "v40/INDEX_V40.md", "v40/tools/v40.py",
            "v40/tools/patch_cumulative_package.py", "v40/tools/audit_cumulative_package.py",
            "v40/tests/test_v40.py", "v40/schemas/persistence-model.schema.json",
            "v40/examples/persistence-model.example.json", "v40/docs/PERSISTENCE_ARCHITECTURE.md",
            "v40/docs/MIGRATIONS_AND_RECEIPTS.md", "v40/docs/PERSISTENCE_CLI.md",
            ".agents/skills/roblox-profile-lifecycle-and-session-ownership/SKILL.md",
            ".agents/skills/roblox-resilient-data-saving-and-recovery/SKILL.md",
            ".agents/skills/roblox-safe-profile-schema-migrations/SKILL.md",
            ".agents/skills/roblox-idempotent-rewards-and-receipt-processing/SKILL.md",
        )
    if is_v41:
        required += (
            "INDEX_V41.md", "v41/VERSION", "v41/INDEX_V41.md", "v41/tools/v41.py",
            "v41/tools/patch_cumulative_package.py", "v41/tools/audit_cumulative_package.py",
            "v41/tests/test_v41.py", "v41/schemas/matchmaking-model.schema.json",
            "v41/examples/matchmaking-model.example.json", "v41/docs/MATCHMAKING_ARCHITECTURE.md",
            "v41/docs/PARTIES_AND_LOBBY_LIFECYCLE.md", "v41/docs/TELEPORT_AND_RECOVERY.md",
            "v41/docs/V41_CLI.md",
            ".agents/skills/roblox-skill-based-matchmaking-queue-design/SKILL.md",
            ".agents/skills/roblox-party-and-lobby-lifecycle/SKILL.md",
            ".agents/skills/roblox-cross-server-matchmaking-coordination/SKILL.md",
            ".agents/skills/roblox-teleport-reconnect-and-server-handoff/SKILL.md",
        )
    if is_v42:
        required += (
            "INDEX_V42.md", "v42/VERSION", "v42/INDEX_V42.md", "v42/tools/v42.py",
            "v42/tools/patch_cumulative_package.py", "v42/tools/audit_cumulative_package.py",
            "v42/tests/test_v42.py", "v42/schemas/liveops-model.schema.json",
            "v42/examples/liveops-model.example.json", "v42/docs/LIVEOPS_EVENT_LIFECYCLE.md",
            "v42/docs/EXPERIENCE_CONFIGS_AND_FEATURE_FLAGS.md",
            "v42/docs/SAFE_CONFIG_DEPLOYMENT_AND_ROLLBACK.md", "v42/docs/V42_CLI.md",
            ".agents/skills/roblox-live-event-lifecycle-and-scheduling/SKILL.md",
            ".agents/skills/roblox-experience-config-and-feature-flag-management/SKILL.md",
            ".agents/skills/roblox-safe-live-config-rollouts/SKILL.md",
            ".agents/skills/roblox-liveops-config-compatibility-and-rollback/SKILL.md",
        )
    if is_v43:
        required += (
            "INDEX_V43.md", "v43/VERSION", "v43/INDEX_V43.md", "v43/tools/v43.py",
            "v43/tools/patch_cumulative_package.py", "v43/tools/audit_cumulative_package.py",
            "v43/tests/test_v43.py", "v43/schemas/experiment-plan.schema.json",
            "v43/schemas/experiment-results-review.schema.json",
            "v43/examples/experiment-plan.example.json", "v43/examples/experiment-results.example.json",
            "v43/docs/EXPERIMENT_DESIGN_AND_METRICS.md", "v43/docs/ROBLOX_EXPERIMENTS_OPEN_CLOUD.md",
            "v43/docs/ANALYTICS_INSTRUMENTATION.md", "v43/docs/STATISTICAL_REVIEW_AND_DECISIONS.md",
            "v43/docs/V43_CLI.md",
            ".agents/skills/roblox-experiment-hypothesis-and-design/SKILL.md",
            ".agents/skills/roblox-native-experiments-and-open-cloud-lifecycle/SKILL.md",
            ".agents/skills/roblox-experiment-analytics-instrumentation/SKILL.md",
            ".agents/skills/roblox-experiment-results-and-decision-review/SKILL.md",
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
