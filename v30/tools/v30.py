#!/usr/bin/env python3
"""Offline Roblox release-readiness planning, evidence validation, and hygiene audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

VERSION = "30.0.0"
MAX_PLAN_BYTES = 1 * 1024 * 1024
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024
MAX_FILES = 10_000
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
SKIP_DIRS = {
    ".git", ".agents", ".codex", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules",
    "target", "build", "dist", ".idea", ".vscode",
}
ENVIRONMENTS = {"development", "staging", "production"}
GATE_IDS = {
    "functional_tests", "multiplayer_tests", "server_authority", "persistence",
    "security_review", "performance_review", "studio_smoke", "rollback_drill",
    "monetization_policy", "migration_validation",
}
PRODUCTION_GATES = {
    "functional_tests", "multiplayer_tests", "server_authority", "persistence",
    "security_review", "performance_review", "studio_smoke", "rollback_drill",
    "monetization_policy",
}
STAGING_GATES = {
    "functional_tests", "server_authority", "persistence",
    "security_review", "studio_smoke",
}
APPROVAL_ROLES = {"release_owner", "qa_lead", "security_reviewer"}
SECRET_PATTERNS = (
    ("named_credential_assignment", re.compile(
        r"(?i)\b(?:ROBLOX_OPEN_CLOUD_API_KEY|OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|PRIVATE_KEY|CLIENT_SECRET|ACCESS_TOKEN)\b\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{12,}"
    )),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("generic_token_assignment", re.compile(
        r"""(?i)\b(?:api[_-]?key|secret|access[_-]?token)\b\s*[:=]\s*["'][A-Za-z0-9_./+=-]{20,}["']"""
    )),
)
ENV_TEMPLATE_NAMES = {".env.example", ".env.sample", ".env.template"}
DEFAULT_PLAN = ".codex/releases/release-plan.json"
DEFAULT_AUDIT = ".codex/reports/v30-release-hygiene-audit.json"


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_project_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw.strip() or "\x00" in raw:
        raise ValueError("Evidence paths must be non-empty relative paths.")
    if "\\" in raw or PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute() or PureWindowsPath(raw).drive:
        raise ValueError("Evidence paths must use portable relative paths with forward slashes.")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("Evidence path must stay inside the selected project root.")
    candidate = root.joinpath(*relative.parts)
    probe = root
    for part in relative.parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Evidence path cannot traverse a symlink.")
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Evidence path resolves outside the selected project root or does not exist.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Evidence path must identify an existing regular file.")
    return resolved


def safe_output_path(root: Path, raw: str) -> Path:
    target = safe_project_path(root, raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve(strict=True)
    if not parent.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent / target.name


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def load_json_file(root: Path, raw: str, limit: int = MAX_PLAN_BYTES) -> tuple[Path, Any]:
    path = safe_project_path(root, raw, must_exist=True)
    try:
        if path.stat().st_size > limit:
            raise ValueError(f"{path.relative_to(root)} exceeds the {limit}-byte input limit.")
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path, data


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_evidence(root: Path, record: dict[str, Any], label: str, errors: list[str]) -> None:
    evidence = record.get("evidence", "")
    digest = record.get("sha256", "")
    if digest and (not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest)):
        errors.append(f"{label}.sha256 must be a 64-character hexadecimal SHA-256 digest.")
        return
    if not evidence:
        if digest:
            errors.append(f"{label} supplies a SHA-256 digest without an evidence path.")
        return
    try:
        path = safe_project_path(root, evidence, must_exist=True)
        if path.stat().st_size > MAX_EVIDENCE_BYTES:
            errors.append(f"{label}.evidence exceeds the {MAX_EVIDENCE_BYTES}-byte evidence-file limit.")
            return
        if digest and hash_file(path).lower() != digest.lower():
            errors.append(f"{label}.sha256 does not match the referenced evidence file.")
    except (OSError, ValueError) as exc:
        errors.append(f"{label}.evidence is invalid: {exc}")


def validate_plan(data: Any, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Release plan must be a JSON object."]
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")

    release = data.get("release")
    if not isinstance(release, dict):
        errors.append("release must be an object.")
        release = {}
    version = release.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        errors.append("release.version must be a semantic version such as 1.2.3.")
    environment = release.get("environment")
    if not isinstance(environment, str) or environment not in ENVIRONMENTS:
        errors.append("release.environment must be development, staging, or production.")
    revision = release.get("source_revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[a-fA-F0-9]{7,64}", revision):
        errors.append("release.source_revision must be a 7-64 character hexadecimal commit identifier.")
    if not valid_timestamp(release.get("created_at")):
        errors.append("release.created_at must be an ISO-8601 timestamp with a timezone.")
    summary = release.get("change_summary")
    if not isinstance(summary, str) or not summary.strip() or len(summary) > 500:
        errors.append("release.change_summary must be a non-empty string of at most 500 characters.")

    controls = data.get("controls")
    if not isinstance(controls, dict):
        errors.append("controls must be an object.")
        controls = {}
    if controls.get("publishing_mode") != "manual":
        errors.append("controls.publishing_mode must be manual; V30 never publishes automatically.")
    if controls.get("human_approval_required") is not True:
        errors.append("controls.human_approval_required must be true.")
    if not isinstance(controls.get("staged_rollout"), bool):
        errors.append("controls.staged_rollout must be a boolean.")
    if environment == "production" and controls.get("staged_rollout") is not True:
        errors.append("Production releases must require a staged rollout.")
    if not isinstance(controls.get("data_store_migration"), bool):
        errors.append("controls.data_store_migration must be a boolean.")

    for field in ("rollback_plan", "backup_reference"):
        value = controls.get(field, "")
        if value and not isinstance(value, str):
            errors.append(f"controls.{field} must be a relative evidence path or an empty string.")
        elif value:
            try:
                path = safe_project_path(root, value, must_exist=True)
                if path.stat().st_size > MAX_EVIDENCE_BYTES:
                    errors.append(f"controls.{field} exceeds the evidence-file size limit.")
            except (OSError, ValueError) as exc:
                errors.append(f"controls.{field} is invalid: {exc}")
        elif environment == "production":
            errors.append(f"Production releases require controls.{field}.")

    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be an array.")
        gates = []
    seen_gates: set[str] = set()
    gate_status: dict[str, str] = {}
    for index, gate in enumerate(gates):
        label = f"gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be an object.")
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or gate_id not in GATE_IDS:
            errors.append(f"{label}.id is unknown.")
            continue
        if gate_id in seen_gates:
            errors.append(f"Duplicate gate id: {gate_id}.")
            continue
        seen_gates.add(gate_id)
        status = gate.get("status")
        if not isinstance(status, str) or status not in {"passed", "failed", "blocked", "not_run", "not_applicable"}:
            errors.append(f"{label}.status is invalid.")
            continue
        gate_status[gate_id] = status
        if status == "passed":
            if not gate.get("evidence"):
                errors.append(f"{label} cannot be marked passed without an evidence file.")
            _check_evidence(root, gate, label, errors)
        elif gate.get("evidence") or gate.get("sha256"):
            _check_evidence(root, gate, label, errors)
        notes = gate.get("notes", "")
        if not isinstance(notes, str) or len(notes) > 1000:
            errors.append(f"{label}.notes must be a string of at most 1000 characters.")

    if environment in ENVIRONMENTS:
        required = set(STAGING_GATES if environment == "staging" else PRODUCTION_GATES)
        if environment == "development":
            required = {"functional_tests"}
        if controls.get("data_store_migration") is True:
            required.add("migration_validation")
        for gate_id in sorted(required):
            if gate_id not in gate_status:
                errors.append(f"Required release gate is missing: {gate_id}.")
            elif gate_status[gate_id] != "passed":
                errors.append(f"Required release gate {gate_id} is {gate_status[gate_id]}, not passed.")

    approvals = data.get("approvals")
    if not isinstance(approvals, list):
        errors.append("approvals must be an array.")
        approvals = []
    approval_by_role: dict[str, dict[str, Any]] = {}
    for index, approval in enumerate(approvals):
        label = f"approvals[{index}]"
        if not isinstance(approval, dict):
            errors.append(f"{label} must be an object.")
            continue
        role = approval.get("role")
        if not isinstance(role, str) or not role.strip():
            errors.append(f"{label}.role must be a non-empty string.")
            continue
        if role in approval_by_role:
            errors.append(f"Duplicate approval role: {role}.")
        approval_by_role[role] = approval
        if not isinstance(approval.get("name"), str) or not approval["name"].strip():
            errors.append(f"{label}.name must be a non-empty string.")
        if approval.get("approved") is not True:
            errors.append(f"{label} must explicitly record approved: true.")
        if not valid_timestamp(approval.get("approved_at")):
            errors.append(f"{label}.approved_at must be an ISO-8601 timestamp with a timezone.")
        _check_evidence(root, approval, label, errors)
        if not approval.get("evidence"):
            errors.append(f"{label} must reference review evidence.")

    if environment == "production":
        for role in sorted(APPROVAL_ROLES):
            if role not in approval_by_role:
                errors.append(f"Production release approval is missing: {role}.")
        if controls.get("data_store_migration") is True and "data_owner" not in approval_by_role:
            errors.append("Production migration requires a data_owner approval.")

    return errors


def make_plan(version: str, environment: str, source_revision: str, summary: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    gate_ids = sorted(GATE_IDS - {"migration_validation"})
    if environment == "production":
        gate_ids.append("migration_validation")
    return {
        "schema_version": 1,
        "release": {
            "version": version,
            "environment": environment,
            "source_revision": source_revision,
            "created_at": now,
            "change_summary": summary,
        },
        "controls": {
            "publishing_mode": "manual",
            "human_approval_required": True,
            "staged_rollout": environment == "production",
            "data_store_migration": False,
            "rollback_plan": "",
            "backup_reference": "",
        },
        "gates": [
            {"id": gate_id, "status": "not_run", "evidence": "", "sha256": "", "notes": ""}
            for gate_id in gate_ids
        ],
        "approvals": [],
        "limitations": [
            "This manifest is a planning and evidence index, not proof that a test or approval is authentic.",
            "V30 does not publish places, update production configuration, execute migrations, or write player data.",
            "A human release owner must verify evidence in the authorized Roblox environment.",
        ],
    }


def iter_project_files(root: Path, max_files: int, warnings: list[str]) -> list[Path]:
    files: list[Path] = []
    total_bytes = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept: list[str] = []
        for name in sorted(dirnames):
            child = current / name
            if name in SKIP_DIRS:
                continue
            if child.is_symlink() or not child.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root directory: {child.relative_to(root)}")
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = current / name
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root file: {path.relative_to(root)}")
                continue
            try:
                size = path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat file: {path.relative_to(root)}")
                continue
            if size > MAX_FILE_BYTES:
                continue
            if total_bytes + size > MAX_TOTAL_BYTES:
                warnings.append("Stopped at the 128 MiB aggregate scan limit.")
                return files
            files.append(path)
            total_bytes += size
            if len(files) >= max_files:
                warnings.append(f"Stopped at the configured {max_files}-file scan limit.")
                return files
    return files


def _audit_rojo_project(path: Path, root: Path, findings: list[dict[str, Any]]) -> None:
    try:
        if path.stat().st_size > MAX_PLAN_BYTES:
            findings.append({"severity": "warning", "code": "rojo_project_too_large",
                             "file": path.relative_to(root).as_posix(), "line": None,
                             "message": "Rojo project file exceeds the JSON audit size limit."})
            return
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        findings.append({"severity": "warning", "code": "rojo_project_invalid_json",
                         "file": path.relative_to(root).as_posix(), "line": None,
                         "message": "Rojo project configuration is not valid UTF-8 JSON."})
        return
    if not isinstance(data, dict) or not isinstance(data.get("tree"), dict):
        findings.append({"severity": "warning", "code": "rojo_tree_missing",
                         "file": path.relative_to(root).as_posix(), "line": None,
                         "message": "Rojo project configuration should contain a tree object."})
        return

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            raw = node.get("$path")
            if isinstance(raw, str):
                try:
                    safe_project_path(root, raw, must_exist=False)
                    if not (root / raw).exists():
                        raise ValueError("mapped path does not exist.")
                except ValueError as exc:
                    findings.append({"severity": "warning", "code": "rojo_path_invalid",
                                     "file": path.relative_to(root).as_posix(), "line": None,
                                     "message": f"A mapped Rojo path is unavailable or unsafe: {exc}"})
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(data["tree"])


def audit_project(root: Path, max_files: int = MAX_FILES) -> dict[str, Any]:
    warnings: list[str] = []
    files = iter_project_files(root, max(1, min(max_files, MAX_FILES)), warnings)
    findings: list[dict[str, Any]] = []
    scanned_text_files = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.name.lower().startswith(".env") and path.name.lower() not in ENV_TEMPLATE_NAMES:
            findings.append({
                "severity": "warning", "code": "environment_file_in_project",
                "file": relative, "line": None,
                "message": "Review this environment file: keep credentials out of source control and provide only sanitized examples.",
            })
        if path.name.endswith(".project.json"):
            _audit_rojo_project(path, root, findings)
        if path.suffix.lower() not in {".lua", ".luau", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".env"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        scanned_text_files += 1
        for line_number, line in enumerate(text.splitlines(), 1):
            for code, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append({
                        "severity": "high", "code": code, "file": relative,
                        "line": line_number,
                        "message": "Credential-like material may be present. The matched value is intentionally not copied into this report; verify and rotate exposed credentials.",
                    })
                    break
            if len(findings) >= 500:
                warnings.append("Stopped recording at the 500-finding report limit.")
                break
        if len(findings) >= 500:
            break
    counts = {level: sum(1 for item in findings if item["severity"] == level) for level in ("high", "warning")}
    return {
        "report_type": "v30_release_hygiene_audit", "schema_version": 1, "version": VERSION,
        "project_root_name": root.name,
        "inventory": {"files_discovered": len(files), "text_files_scanned": scanned_text_files},
        "finding_counts": counts, "findings": findings, "warnings": warnings,
        "execution_status": "static_local_audit_only",
        "limitations": [
            "This is a bounded local text and configuration review, not a complete secret scanner or security assessment.",
            "A warning can be a false positive; review the referenced file without copying secrets into reports or issues.",
            "The audit cannot confirm Git history, Roblox dashboard settings, place contents, live service state, or policy eligibility.",
            "No project source is modified and no Roblox service, Studio session, or production environment is contacted.",
        ],
    }


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    warnings: list[str] = []
    files = iter_project_files(root, MAX_FILES, warnings)
    print(f"Project: {root}")
    print(f"Project files discovered: {len(files)}")
    print("Optional local tools:")
    for executable in ("git", "rojo", "luau-analyze"):
        print(f"  {executable}: {shutil.which(executable) or 'not found on PATH'}")
    print("No configured command is executed and no Roblox connection is attempted.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    if args.environment not in ENVIRONMENTS:
        raise ValueError("--environment must be development, staging, or production.")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", args.version):
        raise ValueError("--version must be semantic version text such as 1.2.3.")
    if not re.fullmatch(r"[a-fA-F0-9]{7,64}", args.source_revision):
        raise ValueError("--source-revision must be a 7-64 character hexadecimal commit identifier.")
    output = safe_output_path(root, args.output)
    plan = make_plan(args.version, args.environment, args.source_revision, args.summary)
    atomic_write_json(output, plan)
    print(f"Review-only release plan created: {output}")
    print("All gates start as not_run. Edit the plan only after collecting real evidence.")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    plan_path, plan = load_json_file(root, args.plan)
    errors = validate_plan(plan, root)
    environment = plan.get("release", {}).get("environment") if isinstance(plan, dict) and isinstance(plan.get("release"), dict) else None
    report = {
        "report_type": "v30_release_plan_validation", "schema_version": 1,
        "plan": plan_path.relative_to(root).as_posix(),
        "environment": environment, "valid": not errors, "errors": errors,
        "limitations": [
            "Validation checks manifest structure, referenced files, policy gates, and stated approvals only.",
            "It does not authenticate people, verify that evidence came from Roblox Studio, or grant release authorization.",
            "The publishing operation remains manual and outside this tool.",
        ],
    }
    if args.output:
        output = safe_output_path(root, args.output)
        atomic_write_json(output, report)
        print(f"Validation report written: {output}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: release plan structure and required evidence references validated.")
    print("This is not a publish authorization.")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    report = audit_project(root, args.max_files)
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    print(f"Read-only release hygiene audit written: {output}")
    print(f"Files: {report['inventory']['files_discovered']}; high findings: {report['finding_counts']['high']}; warnings: {report['finding_counts']['warning']}")
    print("Static audit only; inspect findings manually before release.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Inspect local project inventory and optional tools.")
    doctor.add_argument("--root", required=True)
    doctor.set_defaults(func=command_doctor)

    plan = sub.add_parser("plan", help="Create a review-only release plan template.")
    plan.add_argument("--root", required=True)
    plan.add_argument("--version", required=True)
    plan.add_argument("--environment", choices=sorted(ENVIRONMENTS), required=True)
    plan.add_argument("--source-revision", required=True)
    plan.add_argument("--summary", default="Describe the release changes.")
    plan.add_argument("--output", default=DEFAULT_PLAN)
    plan.set_defaults(func=command_plan)

    validate = sub.add_parser("validate", help="Validate a release plan and its evidence references.")
    validate.add_argument("--root", required=True)
    validate.add_argument("--plan", default=DEFAULT_PLAN)
    validate.add_argument("--output", default=".codex/reports/v30-release-validation.json")
    validate.set_defaults(func=command_validate)

    audit = sub.add_parser("audit", help="Run a bounded, read-only release hygiene audit.")
    audit.add_argument("--root", required=True)
    audit.add_argument("--output", default=DEFAULT_AUDIT)
    audit.add_argument("--max-files", type=int, default=MAX_FILES)
    audit.set_defaults(func=command_audit)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
