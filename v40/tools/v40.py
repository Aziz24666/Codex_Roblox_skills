#!/usr/bin/env python3
"""Offline validator and auditor for Roblox profile persistence contracts."""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "40.0.0"
MAX_INPUT_BYTES = 1024 * 1024
MAX_DATASTORE_VALUE_BYTES = 4_194_304
TOP_FIELDS = {"schema_version", "model_id", "profile_store", "session", "saving", "fields", "migrations", "transactions"}
PROFILE_FIELDS = {"store_name", "scope", "schema_version", "minimum_supported_version", "key_strategy", "profile_size_budget_bytes"}
SESSION_FIELDS = {"locking_enabled", "lock_method", "lease_seconds", "refresh_interval_seconds", "wait_on_conflict", "fail_closed_on_uncertain_ownership", "owner_token_required", "release_on_player_removal", "release_on_shutdown"}
SAVING_FIELDS = {"write_method", "autosave_interval_seconds", "shutdown_budget_seconds", "retry_attempts", "initial_backoff_ms", "max_backoff_ms", "exponential_backoff", "jitter", "serialize_writes_per_key", "budget_aware", "stagger_autosaves", "save_on_leave", "flush_on_shutdown", "unknown_write_outcome"}
PROFILE_FLAG_FIELDS = {"locking_enabled", "wait_on_conflict", "fail_closed_on_uncertain_ownership", "owner_token_required", "release_on_player_removal", "release_on_shutdown"}
SAVING_FLAG_FIELDS = {"exponential_backoff", "jitter", "serialize_writes_per_key", "budget_aware", "stagger_autosaves", "save_on_leave", "flush_on_shutdown"}
FIELD_FIELDS = {"field_id", "data_type", "category", "default_value", "max_encoded_bytes", "client_mutable", "server_validation_required"}
MIGRATION_FIELDS = {"migration_id", "from_version", "to_version", "idempotent", "backup_required", "dry_run_required", "preserve_unknown_fields", "rollback_strategy", "test_case_ids"}
TRANSACTION_FIELDS = {"operation_id", "transaction_kind", "idempotency_key_source", "dedupe_field_id", "commit_strategy", "same_update_contains_effect_and_marker", "acknowledge_after_commit", "concurrent_delivery_policy", "unknown_outcome_policy"}
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
SAFE_STORE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,50}$")
DATA_TYPES = {"integer", "number", "string", "boolean", "array", "object"}
CATEGORIES = {"gameplay_currency", "progression", "inventory", "cosmetic", "setting", "transaction_ledger", "session_metadata"}
AUTHORITATIVE_CATEGORIES = {"gameplay_currency", "progression", "inventory", "transaction_ledger", "session_metadata"}
ROLLBACK_STRATEGIES = {"restore_backup", "forward_fix", "manual_only"}
TRANSACTION_KINDS = {"developer_product_receipt", "gameplay_reward", "inventory_exchange"}
SENSITIVE_FIELD_NAMES = {"email", "phone", "address", "real_name", "full_name", "birthdate", "password", "access_token", "auth_token", "ip_address", "chat_history", "support_transcript", "private_message"}

def is_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum

def is_bool(value: Any) -> bool:
    return isinstance(value, bool)

def is_slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value))

def check_fields(value: dict, expected: set[str], label: str) -> list[str]:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    errors = []
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return errors

def value_matches_type(value: Any, data_type: str) -> bool:
    if data_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if data_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if data_type == "string":
        return isinstance(value, str)
    if data_type == "boolean":
        return isinstance(value, bool)
    if data_type == "array":
        return isinstance(value, list)
    if data_type == "object":
        return isinstance(value, dict)
    return False

def validate_model(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Model must be a JSON object."]
    errors += check_fields(data, TOP_FIELDS, "model")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        errors.append("schema_version must be integer 1.")
    if not is_slug(data.get("model_id")):
        errors.append("model_id must be a lowercase slug (2-40 characters).")

    profile = data.get("profile_store")
    profile_version = minimum_version = None
    profile_budget = None
    if not isinstance(profile, dict):
        errors.append("profile_store must be an object.")
        profile = {}
    else:
        errors += check_fields(profile, PROFILE_FIELDS, "profile_store")
        for name in ("store_name", "scope"):
            value = profile.get(name)
            if not isinstance(value, str) or not SAFE_STORE_NAME.fullmatch(value):
                errors.append(f"profile_store.{name} must be 1-50 letters, digits, underscores, or hyphens.")
        profile_version = profile.get("schema_version")
        minimum_version = profile.get("minimum_supported_version")
        if not is_int(profile_version, 1, 1000):
            errors.append("profile_store.schema_version must be an integer from 1 to 1000.")
        if not is_int(minimum_version, 1, 1000):
            errors.append("profile_store.minimum_supported_version must be an integer from 1 to 1000.")
        elif is_int(profile_version, 1, 1000) and minimum_version > profile_version:
            errors.append("minimum_supported_version cannot exceed schema_version.")
        if profile.get("key_strategy") != "user_id_key":
            errors.append("profile_store.key_strategy must be user_id_key.")
        profile_budget = profile.get("profile_size_budget_bytes")
        if not is_int(profile_budget, 65536, MAX_DATASTORE_VALUE_BYTES):
            errors.append(f"profile_store.profile_size_budget_bytes must be an integer from 65536 to {MAX_DATASTORE_VALUE_BYTES}.")

    session = data.get("session")
    if not isinstance(session, dict):
        errors.append("session must be an object.")
        session = {}
    else:
        errors += check_fields(session, SESSION_FIELDS, "session")
        if session.get("locking_enabled") is not True:
            errors.append("session.locking_enabled must be true for writable player profiles.")
        if session.get("lock_method") not in {"SessionLockedDataStoreWrapper", "UpdateAsync_lease"}:
            errors.append("session.lock_method must be SessionLockedDataStoreWrapper or UpdateAsync_lease.")
        for name in PROFILE_FLAG_FIELDS - {"locking_enabled"}:
            if session.get(name) is not True:
                errors.append(f"session.{name} must be true.")
        lease = session.get("lease_seconds")
        refresh = session.get("refresh_interval_seconds")
        if not is_int(lease, 30, 900):
            errors.append("session.lease_seconds must be an integer from 30 to 900.")
        if not is_int(refresh, 1, 450):
            errors.append("session.refresh_interval_seconds must be an integer from 1 to 450.")
        elif is_int(lease, 30, 900) and refresh * 2 > lease:
            errors.append("session.refresh_interval_seconds must not exceed half of lease_seconds.")

    saving = data.get("saving")
    if not isinstance(saving, dict):
        errors.append("saving must be an object.")
        saving = {}
    else:
        errors += check_fields(saving, SAVING_FIELDS, "saving")
        if saving.get("write_method") != "UpdateAsync":
            errors.append("saving.write_method must be UpdateAsync for shared player profile writes.")
        for name in SAVING_FLAG_FIELDS:
            if saving.get(name) is not True:
                errors.append(f"saving.{name} must be true.")
        if saving.get("unknown_write_outcome") != "reload_and_reconcile":
            errors.append("saving.unknown_write_outcome must be reload_and_reconcile.")
        if not is_int(saving.get("autosave_interval_seconds"), 30, 600):
            errors.append("saving.autosave_interval_seconds must be an integer from 30 to 600.")
        if not is_int(saving.get("shutdown_budget_seconds"), 1, 25):
            errors.append("saving.shutdown_budget_seconds must be an integer from 1 to 25.")
        if not is_int(saving.get("retry_attempts"), 1, 8):
            errors.append("saving.retry_attempts must be an integer from 1 to 8.")
        if not is_int(saving.get("initial_backoff_ms"), 100, 5000):
            errors.append("saving.initial_backoff_ms must be an integer from 100 to 5000.")
        if not is_int(saving.get("max_backoff_ms"), 100, 30000):
            errors.append("saving.max_backoff_ms must be an integer from 100 to 30000.")
        elif is_int(saving.get("initial_backoff_ms"), 100, 5000) and saving["max_backoff_ms"] < saving["initial_backoff_ms"]:
            errors.append("saving.max_backoff_ms cannot be smaller than initial_backoff_ms.")

    fields = data.get("fields")
    field_map: dict[str, dict] = {}
    declared_field_budget = 0
    if not isinstance(fields, list) or not 1 <= len(fields) <= 128:
        errors.append("fields must contain 1-128 profile field declarations.")
        fields = []
    for i, item in enumerate(fields):
        label = f"fields[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, FIELD_FIELDS, label)
        field_id = item.get("field_id")
        if not is_slug(field_id):
            errors.append(f"{label}.field_id must be a lowercase slug.")
        elif field_id in field_map:
            errors.append(f"Duplicate field_id: {field_id}.")
        else:
            field_map[field_id] = item
        if isinstance(field_id, str) and field_id.lower() in SENSITIVE_FIELD_NAMES:
            errors.append(f"{label}.field_id is not permitted for unnecessary personal or sensitive data.")
        data_type = item.get("data_type")
        if not isinstance(data_type, str) or data_type not in DATA_TYPES:
            errors.append(f"{label}.data_type must be one of {', '.join(sorted(DATA_TYPES))}.")
        elif "default_value" in item and not value_matches_type(item["default_value"], data_type):
            errors.append(f"{label}.default_value does not match data_type {data_type}.")
        category = item.get("category")
        if not isinstance(category, str) or category not in CATEGORIES:
            errors.append(f"{label}.category must be one of {', '.join(sorted(CATEGORIES))}.")
        if not is_int(item.get("max_encoded_bytes"), 1, MAX_DATASTORE_VALUE_BYTES):
            errors.append(f"{label}.max_encoded_bytes must be an integer from 1 to {MAX_DATASTORE_VALUE_BYTES}.")
        else:
            declared_field_budget += item["max_encoded_bytes"]
        client_mutable = item.get("client_mutable")
        server_validation = item.get("server_validation_required")
        if not is_bool(client_mutable):
            errors.append(f"{label}.client_mutable must be boolean.")
        if not is_bool(server_validation):
            errors.append(f"{label}.server_validation_required must be boolean.")
        if client_mutable is True and server_validation is not True:
            errors.append(f"{label} client-mutated settings require server_validation_required=true.")
        if isinstance(category, str) and category in AUTHORITATIVE_CATEGORIES and client_mutable is True:
            errors.append(f"{label} category {category} cannot be client_mutable.")

    if is_int(profile_budget, 65536, MAX_DATASTORE_VALUE_BYTES) and declared_field_budget > profile_budget:
        errors.append("Sum of declared field budgets exceeds profile_store.profile_size_budget_bytes.")

    migrations = data.get("migrations")
    if not isinstance(migrations, list) or len(migrations) > 99:
        errors.append("migrations must be a list of at most 99 migration steps.")
        migrations = []
    migration_by_from: dict[int, dict] = {}
    migration_ids = set()
    for i, item in enumerate(migrations):
        label = f"migrations[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, MIGRATION_FIELDS, label)
        migration_id = item.get("migration_id")
        if not is_slug(migration_id):
            errors.append(f"{label}.migration_id must be a lowercase slug.")
        elif migration_id in migration_ids:
            errors.append(f"Duplicate migration_id: {migration_id}.")
        else:
            migration_ids.add(migration_id)
        source_version = item.get("from_version")
        target_version = item.get("to_version")
        if not is_int(source_version, 1, 999) or not is_int(target_version, 2, 1000):
            errors.append(f"{label} from_version/to_version must be valid positive integer schema versions.")
        else:
            if target_version != source_version + 1:
                errors.append(f"{label} must migrate exactly one version step.")
            if source_version in migration_by_from:
                errors.append(f"Duplicate migration source version: {source_version}.")
            else:
                migration_by_from[source_version] = item
            if is_int(profile_version, 1, 1000) and target_version > profile_version:
                errors.append(f"{label}.to_version cannot exceed profile_store.schema_version.")
            if is_int(minimum_version, 1, 1000) and source_version < minimum_version:
                errors.append(f"{label}.from_version is below minimum_supported_version.")
        for name in ("idempotent", "backup_required", "dry_run_required", "preserve_unknown_fields"):
            if item.get(name) is not True:
                errors.append(f"{label}.{name} must be true.")
        if not isinstance(item.get("rollback_strategy"), str) or item.get("rollback_strategy") not in ROLLBACK_STRATEGIES:
            errors.append(f"{label}.rollback_strategy must be one of {', '.join(sorted(ROLLBACK_STRATEGIES))}.")
        case_ids = item.get("test_case_ids")
        if not isinstance(case_ids, list) or not 1 <= len(case_ids) <= 20 or not all(is_slug(x) for x in case_ids):
            errors.append(f"{label}.test_case_ids must contain 1-20 lowercase test-case slugs.")
        elif len(set(case_ids)) != len(case_ids):
            errors.append(f"{label}.test_case_ids must be unique.")

    if is_int(profile_version, 1, 1000) and is_int(minimum_version, 1, 1000) and minimum_version < profile_version:
        current = minimum_version
        while current < profile_version:
            if current not in migration_by_from:
                errors.append(f"Missing migration step from schema version {current} to {current + 1}.")
                break
            current += 1

    transactions = data.get("transactions")
    transaction_ids = set()
    if not isinstance(transactions, list) or len(transactions) > 32:
        errors.append("transactions must be a list of at most 32 transaction definitions.")
        transactions = []
    for i, item in enumerate(transactions):
        label = f"transactions[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, TRANSACTION_FIELDS, label)
        operation_id = item.get("operation_id")
        if not is_slug(operation_id):
            errors.append(f"{label}.operation_id must be a lowercase slug.")
        elif operation_id in transaction_ids:
            errors.append(f"Duplicate operation_id: {operation_id}.")
        else:
            transaction_ids.add(operation_id)
        kind = item.get("transaction_kind")
        if not isinstance(kind, str) or kind not in TRANSACTION_KINDS:
            errors.append(f"{label}.transaction_kind must be one of {', '.join(sorted(TRANSACTION_KINDS))}.")
        expected_key = "PurchaseId" if kind == "developer_product_receipt" else "server_operation_id"
        if item.get("idempotency_key_source") != expected_key:
            errors.append(f"{label}.idempotency_key_source must be {expected_key} for this transaction kind.")
        dedupe_field = item.get("dedupe_field_id")
        if not isinstance(dedupe_field, str) or dedupe_field not in field_map:
            errors.append(f"{label}.dedupe_field_id must reference a declared profile field.")
        else:
            field = field_map[dedupe_field]
            if field.get("category") != "transaction_ledger" or field.get("data_type") != "array":
                errors.append(f"{label}.dedupe_field_id must reference an array field with category transaction_ledger.")
        required_values = {
            "commit_strategy": "single_profile_key_UpdateAsync",
            "same_update_contains_effect_and_marker": True,
            "acknowledge_after_commit": True,
            "concurrent_delivery_policy": "serialized_UpdateAsync_per_key",
            "unknown_outcome_policy": "reload_reconcile_retry_same_key",
        }
        for name, expected in required_values.items():
            if item.get(name) != expected:
                errors.append(f"{label}.{name} must be {expected}.")
    return sorted(set(errors))

def audit_model(data: dict) -> dict:
    warnings = []
    profile = data["profile_store"]
    session = data["session"]
    saving = data["saving"]
    fields = data["fields"]
    migrations = data["migrations"]
    transactions = data["transactions"]
    declared = sum(x["max_encoded_bytes"] for x in fields)
    budget = profile["profile_size_budget_bytes"]
    if budget > int(MAX_DATASTORE_VALUE_BYTES * 0.90):
        warnings.append("Declared profile size budget is above 90% of the Roblox per-key maximum; lower it to leave serialization and metadata headroom.")
    if declared > int(budget * 0.75):
        warnings.append("Declared field budgets consume more than 75% of the profile size budget; measure actual JSON-encoded payloads.")
    if saving["autosave_interval_seconds"] >= session["lease_seconds"] // 2:
        warnings.append("Autosave interval is close to the session lease window; verify lease renewal and save scheduling independently.")
    if not transactions:
        warnings.append("No transaction definitions are declared; add them for any reward, exchange, or developer-product flow.")
    if any(item["transaction_kind"] == "developer_product_receipt" for item in transactions):
        warnings.append("Developer-product receipt markers can accumulate over time; never evict IDs that may still be redelivered, and review a durable capacity/reconciliation plan before the profile approaches its size budget.")
    if profile["minimum_supported_version"] == profile["schema_version"] and profile["schema_version"] == 1:
        warnings.append("No migration fixtures are declared because the profile schema has one supported version; add migration tests before the first schema change.")
    return {
        "schema_version": 1,
        "model_id": data["model_id"],
        "status": "review_required" if warnings else "no_design_warnings",
        "summary": {
            "store_name": profile["store_name"],
            "profile_schema_version": profile["schema_version"],
            "minimum_supported_version": profile["minimum_supported_version"],
            "field_count": len(fields),
            "declared_field_budget_bytes": declared,
            "profile_size_budget_bytes": budget,
            "migration_step_count": len(migrations),
            "transaction_definition_count": len(transactions),
        },
        "warnings": sorted(set(warnings)),
        "limitations": [
            "This report audits declared JSON metadata only; it does not inspect Luau source or connect to Roblox services.",
            "It does not verify that DataStore backups exist, migrations are correct, locks are race-free, or writes are durable.",
            "A green audit is not proof of production safety. Use Studio multi-server tests in a separate test experience and human-reviewed failure injection.",
        ],
    }

def duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"Duplicate JSON key: {key}")
        output[key] = value
    return output

def reject_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")

def resolve_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root

def safe_path(root: Path, raw: str, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw) > 1 and raw[1:2] == ":"):
        raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Empty, dot, and parent path segments are forbidden.")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Symlink traversal is not allowed.")
    resolved = probe.resolve(strict=must_exist)
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise ValueError("Path escapes the project root.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Input must be an existing regular file.")
    return resolved

def load_model(root: Path, raw: str) -> Any:
    path = safe_path(root, raw, True)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Persistence model JSON exceeds the 1 MiB input limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=duplicate_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid persistence model JSON: {exc}") from exc

def write_report(root: Path, raw: str, report: dict) -> None:
    path = safe_path(root, raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Output must be a regular file.")
    descriptor, temp = tempfile.mkstemp(prefix=".v40-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temp).replace(path)
    finally:
        try:
            Path(temp).unlink()
        except FileNotFoundError:
            pass

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("doctor")
    command.add_argument("--root", required=True)
    command = sub.add_parser("validate")
    command.add_argument("--root", required=True)
    command.add_argument("--model", required=True)
    command = sub.add_parser("audit")
    command.add_argument("--root", required=True)
    command.add_argument("--model", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "doctor":
            print(f"V{VERSION} ready | project={root}")
            return 0
        model = load_model(root, args.model)
        errors = validate_model(model)
        if errors:
            for error in errors:
                print("FAIL: " + error)
            return 1
        if args.command == "validate":
            print("PASS: persistence contract structure and safety constraints are valid.")
            return 0
        report = audit_model(model)
        write_report(root, args.output, report)
        print(f"PASS: persistence audit written; fields={report['summary']['field_count']}; migrations={report['summary']['migration_step_count']}; transactions={report['summary']['transaction_definition_count']}; warnings={len(report['warnings'])}.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
