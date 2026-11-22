#!/usr/bin/env python3
"""V28 defensive Roblox remote, DataStore, and migration review utilities."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "28.0.0"
DEFAULT_REPORT = ".codex/reports/v28-security-reliability-report.json"
SKIP_DIRS = {
    ".git", ".codex", ".agents", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "__pycache__", "node_modules", "build", "dist", "target", ".venv", "venv",
}
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_PROJECT_FILES = 10_000
MAX_MANIFEST_BYTES = 1_000_000

REMOTE_BIND_RE = re.compile(
    r"""\b(?:local\s+)?(?P<var>[A-Za-z_]\w*)\s*=\s*[^=\n;]*?(?:WaitForChild|FindFirstChild)\s*\(\s*["'](?P<name>[^"']+)["']\s*\)"""
)
REMOTE_CALL_RE = re.compile(
    r"\b(?P<var>[A-Za-z_]\w*)\s*[:.]\s*(?P<api>FireServer|InvokeServer|FireClient|FireAllClients|InvokeClient|OnClientEvent)\b"
)
REMOTE_HANDLER_RE = re.compile(
    r"(?P<var>[A-Za-z_]\w*)\s*\.\s*(?P<kind>OnServerEvent|OnServerInvoke)\s*(?::\s*Connect\s*\(\s*function|=\s*function)\s*\((?P<params>[^)]*)\)",
    re.S,
)
DATASTORE_CALL_RE = re.compile(
    r"\b(?P<api>GetAsync|SetAsync|UpdateAsync|RemoveAsync|IncrementAsync|GetSortedAsync|SetIncrementSortedAsync|IncrementSortedAsync)\s*\("
)
DATASTORE_FACTORY_RE = re.compile(r"\b(?:GetDataStore|GetOrderedDataStore)\s*\(")
HIGH_IMPACT_RE = re.compile(
    r"\b(?:cash|coins?|currency|balance|wallet|damage|health|inventory|items?|rewards?|purchase|receipt|leaderstats|experience|xp|teleport|save|datastore)\b",
    re.I,
)
VALIDATION_RE = re.compile(
    r"\b(?:typeof|type|assert|clamp|IsA|IsDescendantOf|table\.find|table\.clone|validate|valid|allowlist|whitelist|limit)\b|(?:<=|>=|~=|==|(?<![<>=])<(?![=>])|(?<![<>=])>(?![=>]))",
    re.I,
)
OWNERSHIP_RE = re.compile(
    r"\b(?:UserId|IsDescendantOf|GetPlayerFromCharacter|owner|ownership|creator|player\.Character|Character\s*==)\b",
    re.I,
)
RATE_LIMIT_RE = re.compile(
    r"\b(?:cooldown|rate.?limit|token.?bucket|lastRequest|nextAllowed|requestWindow|requestsPer)\b|\b(?:os\.clock|time|tick)\s*\(",
    re.I,
)
IDEMPOTENCY_RE = re.compile(
    r"\b(?:request.?id|nonce|receipt|processed\w*|idempot|dedup|already.?handled|UpdateAsync)\b",
    re.I,
)
DATA_VERSION_RE = re.compile(r"\b(?:schema.?version|data.?version|current.?version|profileVersion)\b", re.I)
MIGRATION_RE = re.compile(r"\b(?:migrat(?:e|ion|ions|ing)|fromVersion|toVersion|schemaVersion\s*[<>=])\b", re.I)
BACKUP_RE = re.compile(r"\b(?:backup|snapshot|rollback|restore|archive)\b", re.I)
RETRY_RE = re.compile(r"\b(?:retry|backoff|attempts?|jitter)\b", re.I)
BUDGET_RE = re.compile(r"GetRequestBudgetForRequestType", re.I)
PROTECTED_CALL_RE = re.compile(r"\b(?:pcall|xpcall)\s*\(", re.I)
KNOWN_TEST_KINDS = {"valid", "invalid", "legacy", "repeat"}


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def iter_luau_files(root: Path, warnings: list[str], max_files: int = MAX_PROJECT_FILES) -> list[Path]:
    found: list[Path] = []
    total_bytes = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept: list[str] = []
        for dirname in sorted(dirnames):
            child = current / dirname
            if dirname in SKIP_DIRS:
                continue
            if child.is_symlink() or not is_within(child, root):
                warnings.append(f"Skipped symlink or out-of-root directory: {child.relative_to(root)}")
                continue
            kept.append(dirname)
        dirnames[:] = kept
        for filename in sorted(filenames):
            path = current / filename
            if path.suffix.lower() not in {".lua", ".luau"}:
                continue
            if path.is_symlink() or not is_within(path, root):
                warnings.append(f"Skipped symlink or out-of-root source: {path.relative_to(root)}")
                continue
            try:
                size = path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat source file: {path.relative_to(root)}")
                continue
            if size > MAX_FILE_BYTES:
                warnings.append(f"Skipped oversized source file ({size} bytes): {path.relative_to(root)}")
                continue
            if total_bytes + size > MAX_TOTAL_BYTES:
                warnings.append("Stopped at the 256 MiB aggregate source-size limit.")
                return found
            found.append(path)
            total_bytes += size
            if len(found) >= max_files:
                warnings.append(f"Stopped at the configured {max_files}-file limit.")
                return found
    return found


def safe_output_path(root: Path, raw: str) -> Path:
    supplied = Path(raw).expanduser()
    candidate = supplied if supplied.is_absolute() else root / supplied
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Output must be inside the selected project root.") from exc
    if not relative.parts or ".." in relative.parts:
        raise ValueError("Output must be a safe relative path inside the selected project root.")
    parent = root
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            raise ValueError("Output cannot traverse a symlinked directory.")
    parent.mkdir(parents=True, exist_ok=True)
    parent_real = parent.resolve(strict=True)
    if not parent_real.is_relative_to(root):
        raise ValueError("Output parent resolves outside the project root.")
    target = parent_real / relative.name
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError("Output must be a regular file path and cannot replace a symlink.")
    return target


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def read_sources(root: Path, warnings: list[str]) -> dict[Path, str]:
    sources: dict[Path, str] = {}
    for path in iter_luau_files(root, warnings):
        try:
            sources[path] = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            warnings.append(f"Could not read source file: {path.relative_to(root)}")
    return sources


def inspect_remotes(sources: dict[Path, str], root: Path) -> dict[str, Any]:
    client_calls: Counter[str] = Counter()
    server_calls: Counter[str] = Counter()
    server_handlers: Counter[str] = Counter()
    client_handlers: Counter[str] = Counter()
    handler_rows: list[dict[str, Any]] = []

    for path, source in sources.items():
        bindings = {m.group("var"): m.group("name") for m in REMOTE_BIND_RE.finditer(source)}
        for match in REMOTE_CALL_RE.finditer(source):
            variable, api = match.group("var"), match.group("api")
            remote = bindings.get(variable, variable)
            if api in {"FireServer", "InvokeServer"}:
                client_calls[remote] += 1
            elif api in {"FireClient", "FireAllClients", "InvokeClient"}:
                server_calls[remote] += 1
        for match in re.finditer(r"\b([A-Za-z_]\w*)\s*\.\s*OnClientEvent\b", source):
            client_handlers[bindings.get(match.group(1), match.group(1))] += 1
        for match in REMOTE_HANDLER_RE.finditer(source):
            variable = match.group("var")
            remote = bindings.get(variable, variable)
            kind = match.group("kind")
            server_handlers[remote] += 1
            # A bounded review window is not an AST or function-body parser.
            window = source[match.end():match.end() + 2400]
            signals = {
                "type_or_range_validation": bool(VALIDATION_RE.search(window)),
                "ownership_or_permission_check": bool(OWNERSHIP_RE.search(window)),
                "rate_limit_or_cooldown": bool(RATE_LIMIT_RE.search(window)),
                "duplicate_or_idempotency_signal": bool(IDEMPOTENCY_RE.search(window)),
            }
            high_impact = sorted(set(m.group(0).lower() for m in HIGH_IMPACT_RE.finditer(window)))
            flags: list[str] = []
            if high_impact and not (signals["type_or_range_validation"] or signals["ownership_or_permission_check"]):
                flags.append("high-impact operation has no obvious nearby validation or ownership signal")
            if high_impact and not signals["rate_limit_or_cooldown"]:
                flags.append("high-impact operation has no obvious nearby rate-limit signal")
            if high_impact and not signals["duplicate_or_idempotency_signal"]:
                flags.append("high-impact operation has no obvious nearby duplicate-request signal")
            line = source.count("\n", 0, match.start()) + 1
            handler_rows.append({
                "file": path.relative_to(root).as_posix(),
                "line": line,
                "remote_reference": remote,
                "handler": kind,
                "parameter_names": [part.strip().split(":")[0].strip() for part in match.group("params").split(",") if part.strip()],
                "nearby_signals": signals,
                "nearby_high_impact_terms": high_impact,
                "review_flags": flags,
                "analysis_window_characters": len(window),
                "window_based_heuristic": True,
            })

    unpaired = [
        {"remote_reference": name, "client_to_server_calls": count,
         "warning": "No matching statically named OnServerEvent/OnServerInvoke handler was found in scanned source."}
        for name, count in sorted(client_calls.items()) if server_handlers[name] == 0
    ]
    return {
        "client_to_server_calls": dict(sorted(client_calls.items())),
        "server_to_client_calls": dict(sorted(server_calls.items())),
        "server_handlers": dict(sorted(server_handlers.items())),
        "client_handlers": dict(sorted(client_handlers.items())),
        "handlers": sorted(handler_rows, key=lambda row: (row["file"], row["line"])),
        "unpaired_client_calls": unpaired,
        "note": "Names and safeguards are inferred from local text patterns; dynamic bindings and helper-module logic may be unresolved.",
    }


def inspect_datastores(sources: dict[Path, str], root: Path) -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    api_counts: Counter[str] = Counter()
    datastore_factories = 0
    signal_counts: Counter[str] = Counter()
    for path, source in sources.items():
        datastore_factories += len(DATASTORE_FACTORY_RE.findall(source))
        for match in DATASTORE_CALL_RE.finditer(source):
            api = match.group("api")
            api_counts[api] += 1
            line = source.count("\n", 0, match.start()) + 1
            risk = "destructive-write-review" if api == "RemoveAsync" else (
                "overwrite-concurrency-review" if api == "SetAsync" else (
                    "retry-idempotency-review" if api == "UpdateAsync" else "review"
                )
            )
            operations.append({
                "file": path.relative_to(root).as_posix(),
                "line": line,
                "api": api,
                "review_class": risk,
            })
        for label, pattern in (
            ("schema_version_markers", DATA_VERSION_RE),
            ("migration_markers", MIGRATION_RE),
            ("backup_or_rollback_markers", BACKUP_RE),
            ("protected_call_markers", PROTECTED_CALL_RE),
            ("retry_or_backoff_markers", RETRY_RE),
            ("request_budget_markers", BUDGET_RE),
        ):
            signal_counts[label] += len(pattern.findall(source))
    priorities: list[str] = []
    if api_counts["SetAsync"]:
        priorities.append("Review SetAsync call sites for concurrent overwrite and partial-profile replacement risks.")
    if api_counts["RemoveAsync"]:
        priorities.append("Review RemoveAsync call sites for deletion scope, confirmation, and recovery behavior.")
    if api_counts["UpdateAsync"] and signal_counts["retry_or_backoff_markers"] == 0:
        priorities.append("Review UpdateAsync retry behavior and ensure its transform is safe to execute more than once.")
    if datastore_factories and signal_counts["protected_call_markers"] == 0:
        priorities.append("Review DataStore service calls for bounded protected error handling.")
    if datastore_factories and signal_counts["schema_version_markers"] == 0:
        priorities.append("No explicit schema-version marker was detected; verify how legacy records are identified.")
    if signal_counts["migration_markers"] and signal_counts["backup_or_rollback_markers"] == 0:
        priorities.append("Migration-related tokens were detected without an obvious backup or rollback token.")
    return {
        "datastore_factory_calls": datastore_factories,
        "api_call_counts": dict(sorted(api_counts.items())),
        "operations": sorted(operations, key=lambda row: (row["file"], row["line"])),
        "signals": dict(sorted(signal_counts.items())),
        "review_priorities": priorities,
        "note": "Calls and safety signals are text-pattern matches, not proof of persistence semantics or migration correctness.",
    }


def build_report(root: Path) -> dict[str, Any]:
    warnings: list[str] = []
    sources = read_sources(root, warnings)
    remote_report = inspect_remotes(sources, root)
    datastore_report = inspect_datastores(sources, root)
    priorities = list(datastore_report["review_priorities"])
    if remote_report["unpaired_client_calls"]:
        priorities.append("Review client-to-server remotes with no statically matched server handler.")
    if any(row["review_flags"] for row in remote_report["handlers"]):
        priorities.append("Review server handlers with missing nearby validation, rate-limit, or duplicate-request signals.")
    if not remote_report["handlers"] and remote_report["client_to_server_calls"]:
        priorities.append("Client-to-server remotes were found, but no static server handlers were recognized.")
    return {
        "version": VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inventory": {
            "luau_files_read": len(sources),
            "remote_handlers": len(remote_report["handlers"]),
            "datastore_operations": len(datastore_report["operations"]),
        },
        "remote_security": remote_report,
        "datastore": datastore_report,
        "review_priorities": list(dict.fromkeys(priorities)),
        "warnings": warnings,
        "limits": {
            "max_file_bytes": MAX_FILE_BYTES,
            "max_aggregate_bytes": MAX_TOTAL_BYTES,
            "max_files": MAX_PROJECT_FILES,
        },
        "limitations": [
            "This is a local text-pattern scanner, not a Luau parser, type checker, server emulator, or penetration test.",
            "Handler safeguards are inspected in a bounded 2400-character window and may belong to another scope or helper.",
            "Dynamic remote names, wrappers, module indirection, generated code, and DataModel ancestry are not fully resolved.",
            "A detected token does not prove a safeguard is correct; a missing token does not prove a vulnerability.",
            "The tool does not connect to Roblox, execute scripts, access DataStores, call Open Cloud, or alter source files.",
        ],
    }


def validate_manifest_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Manifest root must be a JSON object."]
    required = (
        "schema_version", "environment", "dry_run", "production_writes",
        "current_schema_version", "target_schema_version", "preserve_unknown_fields",
        "backup", "rollback_plan", "migrations",
    )
    for key in required:
        if key not in data:
            errors.append(f"Missing required field: {key}.")
    if errors:
        return errors
    if data["schema_version"] != 1:
        errors.append("schema_version must equal 1.")
    if not isinstance(data["environment"], str) or data["environment"] not in {"synthetic", "staging"}:
        errors.append("environment must be synthetic or staging; production is not permitted.")
    if data["dry_run"] is not True:
        errors.append("dry_run must be true.")
    if data["production_writes"] is not False:
        errors.append("production_writes must be false.")
    if data["preserve_unknown_fields"] is not True:
        errors.append("preserve_unknown_fields must be true.")
    current, target = data["current_schema_version"], data["target_schema_version"]
    if not isinstance(current, int) or isinstance(current, bool) or current < 1:
        errors.append("current_schema_version must be a positive integer.")
    if not isinstance(target, int) or isinstance(target, bool) or target < 2:
        errors.append("target_schema_version must be an integer greater than 1.")
    if isinstance(current, int) and not isinstance(current, bool) and isinstance(target, int) and not isinstance(target, bool):
        if target <= current:
            errors.append("target_schema_version must be greater than current_schema_version.")
    backup = data["backup"]
    if not isinstance(backup, dict) or backup.get("required") is not True or backup.get("verified_in_staging") is not True:
        errors.append("backup must declare required=true and verified_in_staging=true.")
    elif not isinstance(backup.get("strategy"), str) or len(backup["strategy"].strip()) < 8:
        errors.append("backup.strategy must describe a concrete strategy (at least 8 characters).")
    if not isinstance(data["rollback_plan"], str) or len(data["rollback_plan"].strip()) < 20:
        errors.append("rollback_plan must provide a concrete recovery procedure (at least 20 characters).")
    migrations = data["migrations"]
    if not isinstance(migrations, list) or not migrations:
        errors.append("migrations must be a non-empty ordered array.")
        return errors
    if not isinstance(current, int) or isinstance(current, bool) or not isinstance(target, int) or isinstance(target, bool):
        return errors
    expected = current
    for index, migration in enumerate(migrations):
        prefix = f"migrations[{index}]"
        if not isinstance(migration, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        start, end = migration.get("from"), migration.get("to")
        if start != expected:
            errors.append(f"{prefix}.from must continue the sequence at schema version {expected}.")
        if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool) or end != start + 1:
            errors.append(f"{prefix} must advance exactly one schema version.")
        if migration.get("idempotent") is not True:
            errors.append(f"{prefix}.idempotent must be true.")
        if not isinstance(migration.get("description"), str) or len(migration["description"].strip()) < 8:
            errors.append(f"{prefix}.description must describe the migration.")
        tests = migration.get("tests")
        if not isinstance(tests, list):
            errors.append(f"{prefix}.tests must be an array.")
        else:
            kinds = {
                item.get("kind") for item in tests
                if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip() and isinstance(item.get("kind"), str)
            }
            missing = KNOWN_TEST_KINDS - kinds
            if missing:
                errors.append(f"{prefix}.tests is missing named coverage: {', '.join(sorted(missing))}.")
        if isinstance(start, int) and not isinstance(start, bool) and isinstance(end, int) and not isinstance(end, bool) and end == start + 1:
            expected = end
    if expected != target:
        errors.append(f"Migration sequence ends at version {expected}, not target_schema_version {target}.")
    return errors


def validate_manifest(root: Path, raw_path: str) -> tuple[list[str], Path]:
    supplied = Path(raw_path).expanduser()
    path = supplied if supplied.is_absolute() else root / supplied
    if path.is_symlink() or not is_within(path, root):
        return ["Manifest path must be a regular file inside the selected project root; symlinks are not allowed."], path
    try:
        input_relative = path.relative_to(root)
        if not input_relative.parts or ".." in input_relative.parts:
            return ["Manifest path must be a safe relative path inside the selected project root."], path
        cursor = root
        for part in input_relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return ["Manifest path cannot traverse a symlink."], path
        resolved = path.resolve(strict=True)
        if not resolved.is_file() or not resolved.is_relative_to(root):
            return ["Manifest must resolve to a regular file inside the selected project root."], path
        cursor = root
        for part in resolved.relative_to(root).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return ["Manifest path cannot traverse a symlink."], resolved
        if resolved.stat().st_size > MAX_MANIFEST_BYTES:
            return [f"Manifest exceeds the {MAX_MANIFEST_BYTES}-byte limit."], resolved
        data = json.loads(resolved.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return [f"Manifest not found: {path}"], path
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"Could not read manifest as valid UTF-8 JSON: {exc}"], path
    return validate_manifest_data(data), resolved


def command_doctor(root: Path) -> int:
    warnings: list[str] = []
    sources = read_sources(root, warnings)
    print(f"Project root: {root}")
    print(f"Luau files scanned: {len(sources)}")
    print(f"luau-analyze: {shutil.which('luau-analyze') or 'not found (optional)'}")
    print(f"rojo: {shutil.which('rojo') or 'not found (optional)'}")
    print(f"Static RemoteEvent/RemoteFunction handler patterns: {sum(len(REMOTE_HANDLER_RE.findall(text)) for text in sources.values())}")
    print(f"DataStore API call patterns: {sum(len(DATASTORE_CALL_RE.findall(text)) for text in sources.values())}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print("No Roblox service, DataStore, Open Cloud endpoint, or Studio process was contacted.")
    return 0


def command_audit(root: Path, raw_output: str, force: bool) -> int:
    output = safe_output_path(root, raw_output)
    if output.exists() and not force:
        raise FileExistsError(f"Report already exists: {output}. Review it or pass --force to replace it.")
    report = build_report(root)
    atomic_write_json(output, report)
    print(f"Wrote read-only V28 security/reliability report: {output.relative_to(root)}")
    print(f"Remote handlers: {report['inventory']['remote_handlers']}")
    print(f"DataStore operations: {report['inventory']['datastore_operations']}")
    print(f"Review priorities: {len(report['review_priorities'])}")
    print("Static findings are advisory; no game code or Roblox data was changed.")
    return 0


def command_validate_manifest(root: Path, raw_manifest: str) -> int:
    errors, path = validate_manifest(root, raw_manifest)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: migration manifest structure and safety declarations: {path.relative_to(root)}")
    print("This validates the plan only; it does not execute a migration or access any DataStore.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("doctor", "Inspect local project/tool availability without contacting Roblox services."),
        ("audit", "Generate a read-only remote and DataStore review report."),
        ("validate-migration", "Validate a synthetic/staging-only migration manifest; never execute it."),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--root", required=True, type=str, help="Existing game project root.")
        if name == "audit":
            command.add_argument("--output", default=DEFAULT_REPORT, help="Report path inside the project root.")
            command.add_argument("--force", action="store_true", help="Replace an existing report after review.")
        elif name == "validate-migration":
            command.add_argument("--manifest", required=True, help="Manifest JSON path inside the project root.")
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "doctor":
            return command_doctor(root)
        if args.command == "audit":
            return command_audit(root, args.output, args.force)
        return command_validate_manifest(root, args.manifest)
    except (ValueError, FileExistsError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
