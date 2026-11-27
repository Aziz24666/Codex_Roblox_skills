#!/usr/bin/env python3
"""Offline validator, auditor, and deterministic simulator for Roblox matchmaking contracts."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "41.0.0"
MAX_INPUT_BYTES = 1024 * 1024
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
QUEUE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,48}$")

TOP_FIELDS = {"schema_version", "model_id", "queue", "matching", "party", "coordination", "teleport", "recovery", "simulation_tickets"}
QUEUE_FIELDS = {"provider", "queue_name", "ordering", "item_ttl_seconds", "invisibility_timeout_seconds", "read_batch_size", "remove_after_assignment", "duplicate_ticket_key", "network_calls_protected", "stores_durable_player_data"}
MATCH_FIELDS = {"minimum_players", "preferred_players", "maximum_players", "initial_skill_window", "skill_window_step", "maximum_skill_window", "window_expansion_interval_seconds", "maximum_wait_seconds", "party_atomicity"}
PARTY_FIELDS = {"minimum_size", "maximum_size", "leader_policy", "leadership_transfer_policy", "invite_ttl_seconds", "invites_server_validated", "membership_server_validated", "party_ticket_atomic"}
COORD_FIELDS = {"shared_state_store", "active_record_ttl_seconds", "lease_seconds", "lease_refresh_seconds", "fencing_token_required", "versioned_state_required", "server_id_required", "messaging_service_role", "messaging_delivery_assumed", "messaging_as_authority"}
TELEPORT_FIELDS = {"method", "server_context_only", "route_mode", "reserved_server_id_source", "maximum_players_per_call", "teleport_data_classification", "secure_data_in_teleport_payload", "destination_ticket_revalidation", "access_control_reviewed", "teleport_init_failed_handler", "retry_attempts", "retry_same_destination"}
RECOVERY_FIELDS = {"ticket_idempotency_required", "queue_reentry_policy", "rejoin_grace_seconds", "orphan_ticket_cleanup_required", "reconcile_failed_members", "client_state_is_authoritative", "on_exhausted_retry", "retry_backoff_seconds"}
TICKET_FIELDS = {"ticket_id", "party_size", "skill_rating", "wait_seconds", "order_index"}


def is_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def is_slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value))


def check_fields(value: dict, expected: set[str], label: str) -> list[str]:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    errors: list[str] = []
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return errors


def validate_model(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Model must be a JSON object."]
    errors += check_fields(data, TOP_FIELDS, "model")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        errors.append("schema_version must be integer 1.")
    if not is_slug(data.get("model_id")):
        errors.append("model_id must be a lowercase slug (2-40 characters).")

    sections: dict[str, dict] = {}
    for name, expected in (("queue", QUEUE_FIELDS), ("matching", MATCH_FIELDS), ("party", PARTY_FIELDS),
                           ("coordination", COORD_FIELDS), ("teleport", TELEPORT_FIELDS), ("recovery", RECOVERY_FIELDS)):
        value = data.get(name)
        if not isinstance(value, dict):
            errors.append(f"{name} must be an object.")
            sections[name] = {}
        else:
            errors += check_fields(value, expected, name)
            sections[name] = value

    queue = sections["queue"]
    if queue:
        if queue.get("provider") != "MemoryStoreQueue":
            errors.append("queue.provider must be MemoryStoreQueue.")
        if not isinstance(queue.get("queue_name"), str) or not QUEUE_NAME.fullmatch(queue.get("queue_name", "")):
            errors.append("queue.queue_name must be 1-48 letters, digits, underscores, or hyphens.")
        if queue.get("ordering") not in ("FIFO", "priority"):
            errors.append("queue.ordering must be FIFO or priority.")
        if not is_int(queue.get("item_ttl_seconds"), 30, 3600):
            errors.append("queue.item_ttl_seconds must be an integer from 30 to 3600.")
        if not is_int(queue.get("invisibility_timeout_seconds"), 5, 120):
            errors.append("queue.invisibility_timeout_seconds must be an integer from 5 to 120.")
        if not is_int(queue.get("read_batch_size"), 1, 100):
            errors.append("queue.read_batch_size must be an integer from 1 to 100.")
        if queue.get("remove_after_assignment") is not True:
            errors.append("queue.remove_after_assignment must be true; remove entries only after assignment is durably recorded.")
        if queue.get("duplicate_ticket_key") != "ticket_id":
            errors.append("queue.duplicate_ticket_key must be ticket_id.")
        if queue.get("network_calls_protected") is not True:
            errors.append("queue.network_calls_protected must be true; handle MemoryStore failures with protected calls.")
        if queue.get("stores_durable_player_data") is not False:
            errors.append("queue.stores_durable_player_data must be false; MemoryStore is ephemeral, not durable player storage.")

    matching = sections["matching"]
    if matching:
        low = matching.get("minimum_players")
        target = matching.get("preferred_players")
        high = matching.get("maximum_players")
        if not is_int(low, 2, 50):
            errors.append("matching.minimum_players must be an integer from 2 to 50.")
        if not is_int(target, 2, 50):
            errors.append("matching.preferred_players must be an integer from 2 to 50.")
        if not is_int(high, 2, 50):
            errors.append("matching.maximum_players must be an integer from 2 to 50.")
        if all(is_int(x, 2, 50) for x in (low, target, high)) and not low <= target <= high:
            errors.append("matching player counts must satisfy minimum_players <= preferred_players <= maximum_players.")
        for name in ("initial_skill_window", "maximum_skill_window"):
            if not is_int(matching.get(name), 0, 5000):
                errors.append(f"matching.{name} must be an integer from 0 to 5000.")
        if is_int(matching.get("initial_skill_window"), 0, 5000) and is_int(matching.get("maximum_skill_window"), 0, 5000):
            if matching["maximum_skill_window"] < matching["initial_skill_window"]:
                errors.append("matching.maximum_skill_window cannot be smaller than initial_skill_window.")
        if not is_int(matching.get("skill_window_step"), 1, 1000):
            errors.append("matching.skill_window_step must be an integer from 1 to 1000.")
        if not is_int(matching.get("window_expansion_interval_seconds"), 5, 300):
            errors.append("matching.window_expansion_interval_seconds must be an integer from 5 to 300.")
        if not is_int(matching.get("maximum_wait_seconds"), 30, 1800):
            errors.append("matching.maximum_wait_seconds must be an integer from 30 to 1800.")
        if matching.get("party_atomicity") != "all_or_none":
            errors.append("matching.party_atomicity must be all_or_none; never split a party to fill a match.")

    party = sections["party"]
    if party:
        minimum = party.get("minimum_size")
        maximum = party.get("maximum_size")
        if not is_int(minimum, 1, 50):
            errors.append("party.minimum_size must be an integer from 1 to 50.")
        if not is_int(maximum, 1, 50):
            errors.append("party.maximum_size must be an integer from 1 to 50.")
        if is_int(minimum, 1, 50) and is_int(maximum, 1, 50) and minimum > maximum:
            errors.append("party.minimum_size cannot exceed party.maximum_size.")
        if is_int(maximum, 1, 50) and is_int(matching.get("maximum_players"), 2, 50) and maximum > matching["maximum_players"]:
            errors.append("party.maximum_size cannot exceed matching.maximum_players.")
        if party.get("leader_policy") != "server_authoritative":
            errors.append("party.leader_policy must be server_authoritative.")
        if party.get("leadership_transfer_policy") not in ("eligible_member_order", "manual_owner_approval"):
            errors.append("party.leadership_transfer_policy must be eligible_member_order or manual_owner_approval.")
        if not is_int(party.get("invite_ttl_seconds"), 15, 600):
            errors.append("party.invite_ttl_seconds must be an integer from 15 to 600.")
        for name in ("invites_server_validated", "membership_server_validated", "party_ticket_atomic"):
            if party.get(name) is not True:
                errors.append(f"party.{name} must be true.")

    coordination = sections["coordination"]
    if coordination:
        if coordination.get("shared_state_store") != "MemoryStoreHashMap":
            errors.append("coordination.shared_state_store must be MemoryStoreHashMap for ephemeral active-session records.")
        if not is_int(coordination.get("active_record_ttl_seconds"), 60, 86400):
            errors.append("coordination.active_record_ttl_seconds must be an integer from 60 to 86400.")
        lease = coordination.get("lease_seconds")
        refresh = coordination.get("lease_refresh_seconds")
        if not is_int(lease, 30, 300):
            errors.append("coordination.lease_seconds must be an integer from 30 to 300.")
        if not is_int(refresh, 5, 150):
            errors.append("coordination.lease_refresh_seconds must be an integer from 5 to 150.")
        elif is_int(lease, 30, 300) and refresh * 2 > lease:
            errors.append("coordination.lease_refresh_seconds must not exceed half of lease_seconds.")
        if is_int(coordination.get("active_record_ttl_seconds"), 60, 86400) and is_int(lease, 30, 300):
            if coordination["active_record_ttl_seconds"] < lease:
                errors.append("coordination.active_record_ttl_seconds must be at least lease_seconds.")
        for name in ("fencing_token_required", "versioned_state_required", "server_id_required"):
            if coordination.get(name) is not True:
                errors.append(f"coordination.{name} must be true.")
        if coordination.get("messaging_service_role") != "best_effort_notifications":
            errors.append("coordination.messaging_service_role must be best_effort_notifications.")
        if coordination.get("messaging_delivery_assumed") != "best_effort":
            errors.append("coordination.messaging_delivery_assumed must be best_effort.")
        if coordination.get("messaging_as_authority") is not False:
            errors.append("coordination.messaging_as_authority must be false; MessagingService delivery is not guaranteed.")

    teleport = sections["teleport"]
    if teleport:
        if teleport.get("method") != "TeleportAsync":
            errors.append("teleport.method must be TeleportAsync.")
        if teleport.get("server_context_only") is not True:
            errors.append("teleport.server_context_only must be true.")
        if teleport.get("route_mode") != "ReservedServerId":
            errors.append("teleport.route_mode must be ReservedServerId for reserved match servers.")
        if teleport.get("reserved_server_id_source") != "HttpService:GenerateGUID(false)":
            errors.append("teleport.reserved_server_id_source must be HttpService:GenerateGUID(false); do not use legacy access-code patterns for new systems.")
        maximum_call = teleport.get("maximum_players_per_call")
        if not is_int(maximum_call, 1, 50):
            errors.append("teleport.maximum_players_per_call must be an integer from 1 to 50.")
        elif is_int(matching.get("maximum_players"), 2, 50) and matching["maximum_players"] > maximum_call:
            errors.append("matching.maximum_players cannot exceed teleport.maximum_players_per_call (Roblox TeleportAsync group limit: 50).")
        if teleport.get("teleport_data_classification") != "opaque_ticket_reference_only":
            errors.append("teleport.teleport_data_classification must be opaque_ticket_reference_only.")
        if teleport.get("secure_data_in_teleport_payload") is not False:
            errors.append("teleport.secure_data_in_teleport_payload must be false; teleport data is visible to clients and unencrypted.")
        for name in ("destination_ticket_revalidation", "access_control_reviewed", "teleport_init_failed_handler", "retry_same_destination"):
            if teleport.get(name) is not True:
                errors.append(f"teleport.{name} must be true.")
        if not is_int(teleport.get("retry_attempts"), 1, 5):
            errors.append("teleport.retry_attempts must be an integer from 1 to 5.")

    recovery = sections["recovery"]
    if recovery:
        if recovery.get("ticket_idempotency_required") is not True:
            errors.append("recovery.ticket_idempotency_required must be true.")
        if recovery.get("queue_reentry_policy") != "preserve_party_ticket":
            errors.append("recovery.queue_reentry_policy must be preserve_party_ticket.")
        if not is_int(recovery.get("rejoin_grace_seconds"), 0, 600):
            errors.append("recovery.rejoin_grace_seconds must be an integer from 0 to 600.")
        for name in ("orphan_ticket_cleanup_required", "reconcile_failed_members"):
            if recovery.get(name) is not True:
                errors.append(f"recovery.{name} must be true.")
        if recovery.get("client_state_is_authoritative") is not False:
            errors.append("recovery.client_state_is_authoritative must be false.")
        if recovery.get("on_exhausted_retry") != "return_to_lobby_requeue":
            errors.append("recovery.on_exhausted_retry must be return_to_lobby_requeue.")
        if not is_int(recovery.get("retry_backoff_seconds"), 1, 30):
            errors.append("recovery.retry_backoff_seconds must be an integer from 1 to 30.")

    tickets = data.get("simulation_tickets")
    if not isinstance(tickets, list) or len(tickets) > 64:
        errors.append("simulation_tickets must be a list of at most 64 synthetic tickets.")
        tickets = []
    ticket_ids: set[str] = set()
    order_indexes: set[int] = set()
    for index, ticket in enumerate(tickets):
        label = f"simulation_tickets[{index}]"
        if not isinstance(ticket, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(ticket, TICKET_FIELDS, label)
        ticket_id = ticket.get("ticket_id")
        if not is_slug(ticket_id):
            errors.append(f"{label}.ticket_id must be a lowercase slug.")
        elif ticket_id in ticket_ids:
            errors.append(f"Duplicate simulation ticket_id: {ticket_id}.")
        else:
            ticket_ids.add(ticket_id)
        if not is_int(ticket.get("party_size"), 1, 50):
            errors.append(f"{label}.party_size must be an integer from 1 to 50.")
        elif is_int(party.get("maximum_size"), 1, 50) and ticket["party_size"] > party["maximum_size"]:
            errors.append(f"{label}.party_size exceeds party.maximum_size.")
        if not is_int(ticket.get("skill_rating"), 0, 5000):
            errors.append(f"{label}.skill_rating must be an integer from 0 to 5000.")
        if not is_int(ticket.get("wait_seconds"), 0, 86400):
            errors.append(f"{label}.wait_seconds must be an integer from 0 to 86400.")
        order_index = ticket.get("order_index")
        if not is_int(order_index, 0, 1000000):
            errors.append(f"{label}.order_index must be an integer from 0 to 1000000.")
        elif order_index in order_indexes:
            errors.append(f"Duplicate simulation order_index: {order_index}.")
        else:
            order_indexes.add(order_index)
    return sorted(set(errors))


def audit_model(data: dict) -> dict:
    warnings: list[str] = []
    queue = data["queue"]
    matching = data["matching"]
    party = data["party"]
    coordination = data["coordination"]
    if queue["item_ttl_seconds"] <= matching["maximum_wait_seconds"]:
        warnings.append("Queue item TTL does not exceed the maximum wait window; entries may expire before the intended wait budget is used.")
    if queue["invisibility_timeout_seconds"] < 30:
        warnings.append("Queue invisibility timeout is shorter than Roblox's documented 30-second default; verify that read, assignment, state commit, and removal complete inside the configured window.")
    if coordination["active_record_ttl_seconds"] < coordination["lease_seconds"] * 2:
        warnings.append("Active-session record TTL is less than twice the lease duration; review recovery headroom after a missed renewal.")
    if matching["maximum_skill_window"] == matching["initial_skill_window"]:
        warnings.append("Skill window never expands; long-wait players may experience avoidable queue starvation.")
    if party["maximum_size"] == matching["maximum_players"]:
        warnings.append("A maximum-size party can consume the entire match; review whether the experience supports party-only matches.")
    return {
        "schema_version": 1,
        "model_id": data["model_id"],
        "status": "review_required" if warnings else "no_design_warnings",
        "summary": {
            "queue_provider": queue["provider"],
            "queue_name": queue["queue_name"],
            "ordering": queue["ordering"],
            "minimum_players": matching["minimum_players"],
            "preferred_players": matching["preferred_players"],
            "maximum_players": matching["maximum_players"],
            "party_minimum_size": party["minimum_size"],
            "party_maximum_size": party["maximum_size"],
            "simulation_ticket_count": len(data["simulation_tickets"]),
        },
        "warnings": sorted(set(warnings)),
        "limitations": [
            "This report validates declared JSON metadata only; it does not call MemoryStoreService, MessagingService, TeleportService, or DataStoreService.",
            "It does not inspect Luau source, observe live queue fairness, create parties, reserve servers, teleport players, or prove reconnect behavior.",
            "Simulation inputs are synthetic and deterministic; results are not live queue measurements or predictions of player wait times.",
            "A green report is not proof of production readiness. Run multi-server tests and published-experience teleport tests with human review before rollout.",
        ],
    }


def simulate_match(data: dict) -> dict:
    """Greedy deterministic simulation that preserves ticket/party atomicity."""
    matching = data["matching"]
    tickets = sorted(data["simulation_tickets"], key=lambda item: item["order_index"])
    if not tickets:
        return {
            "schema_version": 1,
            "model_id": data["model_id"],
            "status": "insufficient_players",
            "synthetic_data": True,
            "selected_ticket_ids": [],
            "player_count": 0,
            "skill_window_used": matching["initial_skill_window"],
            "skipped": [],
            "limitations": ["No live queue was read. Add synthetic tickets to simulate_matchmaking only."],
        }
    anchor = tickets[0]
    steps = anchor["wait_seconds"] // matching["window_expansion_interval_seconds"]
    window = min(matching["maximum_skill_window"], matching["initial_skill_window"] + steps * matching["skill_window_step"])
    selected: list[str] = []
    skipped: list[dict[str, str]] = []
    player_count = 0
    for ticket in tickets:
        if abs(ticket["skill_rating"] - anchor["skill_rating"]) > window:
            skipped.append({"ticket_id": ticket["ticket_id"], "reason": "outside_anchor_skill_window"})
            continue
        if player_count + ticket["party_size"] > matching["maximum_players"]:
            skipped.append({"ticket_id": ticket["ticket_id"], "reason": "would_exceed_capacity_without_splitting_party"})
            continue
        if player_count >= matching["preferred_players"]:
            skipped.append({"ticket_id": ticket["ticket_id"], "reason": "preferred_match_size_already_reached"})
            continue
        selected.append(ticket["ticket_id"])
        player_count += ticket["party_size"]
        if player_count >= matching["preferred_players"]:
            break
    status = "matched" if player_count >= matching["minimum_players"] else "insufficient_players"
    return {
        "schema_version": 1,
        "model_id": data["model_id"],
        "status": status,
        "synthetic_data": True,
        "anchor_ticket_id": anchor["ticket_id"],
        "anchor_skill_rating": anchor["skill_rating"],
        "anchor_wait_seconds": anchor["wait_seconds"],
        "skill_window_used": window,
        "selected_ticket_ids": selected,
        "player_count": player_count,
        "skipped": skipped,
        "limitations": [
            "This is a deterministic, single-match planning simulation over supplied synthetic ticket metadata.",
            "It does not model real MemoryStore queue ordering, network timing, server concurrency, player retention, or Roblox matchmaking outcomes.",
            "Parties are indivisible tickets. Actual assignment must be atomically claimed and revalidated by server code before removal or teleport.",
        ],
    }


def duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    output: dict[str, Any] = {}
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
        raise ValueError("Matchmaking model JSON exceeds the 1 MiB input limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=duplicate_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid matchmaking model JSON: {exc}") from exc


def write_report(root: Path, raw: str, report: dict) -> None:
    path = safe_path(root, raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Re-check after creating the parent so pre-existing symlink components are rejected.
    safe_path(root, raw)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Output must be a regular file.")
    descriptor, temporary = tempfile.mkstemp(prefix=".v41-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).replace(path)
    finally:
        try:
            Path(temporary).unlink()
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
    command = sub.add_parser("simulate")
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
            print("PASS: matchmaking, party, coordination, teleport, and recovery contract is valid.")
            return 0
        if args.command == "audit":
            report = audit_model(model)
            write_report(root, args.output, report)
            print(f"PASS: matchmaking audit written; tickets={report['summary']['simulation_ticket_count']}; warnings={len(report['warnings'])}.")
            return 0
        report = simulate_match(model)
        write_report(root, args.output, report)
        print(f"PASS: deterministic simulation written; status={report['status']}; players={report['player_count']}; selected_tickets={len(report['selected_ticket_ids'])}.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
