---
name: roblox-teleport-reconnect-and-server-handoff
description: Implement server-side Roblox TeleportAsync routing, reserved match servers, safe teleport payloads, failure recovery, and reconnect reconciliation.
---

# Teleport, reconnect, and server handoff

## Goal
Move a fully validated party from lobby to match server without leaking secrets, losing the party on partial failure, retrying into a different match accidentally, or trusting client-supplied destination state.

## Server-side teleport contract
- Initiate cross-place teleports from server code with `TeleportService:TeleportAsync()` and a `TeleportOptions` object.
- For a new reserved-server workflow, create a destination ID using `HttpService:GenerateGUID(false)` and set `TeleportOptions.ReservedServerId`. Keep and reuse the same reserved server ID for retries and intended rejoin routing; do not generate a new destination on each retry.
- Respect the documented maximum of 50 players in one `TeleportAsync` group call. Validate the party/match size before calling the API.
- Do not use client-side teleporting as an authority or accept a client-selected place/server as a match assignment.
- Call teleports in `pcall` and handle both immediate errors and asynchronous `TeleportService.TeleportInitFailed` events.

## TeleportData and destination validation
Teleport data is visible to clients and is not encrypted. Include only an opaque, short-lived ticket/assignment reference and non-sensitive routing hints. Never include credentials, private keys, session tokens, private party invitations, durable profile data, hidden match answers, moderation records, or payment/receipt information.

At the destination:
1. Read the join information using the supported server-side API.
2. Treat TeleportData as an untrusted reference, not proof of entitlement.
3. Fetch the authoritative match/party assignment from MemoryStore or another server-owned source.
4. Check destination place ID, reserved server identity, assignment ID, expiry, membership version, expected players, and a one-use/claim state.
5. Claim the arrival idempotently. Reject stale, replayed, expired, or mismatched ticket references and route the player to a safe lobby/recovery path.

## Failure and partial-party handling
- Record assignment and reserved-server identity before teleport initiation.
- Handle a `pcall` failure and `TeleportInitFailed`; a call returning without a synchronous error does not guarantee every player arrived.
- Reconcile each player/member independently. Keep the party assignment intact while some members are still in transit or retrying.
- Retry only within a bounded policy and reuse the same assignment/destination so a partial party cannot be split across different matches accidentally.
- If retries are exhausted, return the affected party to a safe lobby and requeue using the same idempotent party ticket after server-side reconciliation.
- Maintain a short reconnect grace window. A rejoining player must be validated against the current assignment and membership version; do not let an old ticket rejoin a newer match.
- Clean up abandoned reserved-match records and tickets with a lease/version check, never by deleting state solely because one teleport callback failed.

## Observability and testing
Track aggregate counts and durations for initiation failures, per-player arrival, retries, requeue outcomes, expired tickets, and destination rejection. Avoid storing unnecessary player-level history. Log opaque assignment/ticket IDs and version numbers for correlation.

Test in an authorized test experience: successful party teleport, reserved destination reuse, one member failing while others arrive, server shutdown during handoff, destination validation rejecting an expired/replayed ticket, reconnect within/outside grace, and return-to-lobby behavior. Studio testing can help exercise teleport flows, but verify published-experience behavior and cross-server conditions separately.

## Required deliverables
- Server-side teleport API and reserved-server routing design.
- Assignment-to-destination state transition diagram.
- TeleportData allowlist and destination revalidation checklist.
- `TeleportInitFailed` and `pcall` failure handling.
- Partial-party retry/requeue state machine.
- Reconnect grace and orphan cleanup policy.
- Published test-experience evidence for cross-place and cross-server behavior.

## Non-negotiable safeguards
- Server-authoritative `TeleportAsync`; no client authority over destination or assignment.
- Never place sensitive data in TeleportData.
- Revalidate each arrival against authoritative, unexpired assignment state.
- Bounded retry, same destination, and party-aware recovery are mandatory.
- An offline audit cannot prove a real teleport succeeded.
