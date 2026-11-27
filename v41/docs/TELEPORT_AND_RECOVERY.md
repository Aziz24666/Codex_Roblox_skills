# Teleport, reconnect, and recovery

## Server-initiated routing

Use `TeleportService:TeleportAsync()` from server code with `TeleportOptions`. For new reserved match servers, set `TeleportOptions.ReservedServerId` to an opaque ID generated with `HttpService:GenerateGUID(false)`. Persist that destination identity in the short-lived authoritative assignment and reuse it for retries intended to reach the same match. Validate the intended player count before the call; the documented `TeleportAsync` player-list limit is 50.

Wrap API initiation in `pcall`, but do not treat a successful return as proof that every player arrived. Handle `TeleportService.TeleportInitFailed`, which covers initiation failures where the player remains in the current server. Keep retry counts bounded and make retry decisions per member while preserving a single party assignment and destination.

## TeleportData is not a secure channel

TeleportData is visible to clients and is not encrypted. Pass only an opaque short-lived ticket/assignment reference and non-sensitive routing hints. Never send passwords, tokens, private invitations, durable profile contents, hidden game state, payment records, or moderation data.

The destination reads join information and then revalidates the ticket against authoritative state stored server-side. Check expected place/server, assignment ID, expiry, membership version, allowed roster, and one-time arrival/claim state. Treat TeleportData as an untrusted reference, not as authentication or proof of entitlement.

## Partial-party recovery

Maintain an arrival ledger per assignment with a bounded grace period. If only some party members arrive:

1. Keep the original assignment and reserved destination stable.
2. Reconcile each expected member against authoritative state.
3. Retry only failed/still-eligible members, using the same destination and assignment.
4. If retry budget expires, route the affected party to a safe lobby/recovery state and requeue the entire party under an idempotent ticket policy.
5. Clean up the previous assignment only after all members are accounted for or its lease/expiry and recovery rules allow cleanup.

Never assume that teleport callbacks are a complete source of truth. Reconcile using join data and the destination's server-side assignment record. Do not let a failed callback remove a newer assignment.

## Reconnect policy

Define a grace period and expected state for each stage: lobby, queued, claimed, teleporting, and in-match. Rejoining players must be matched to the correct current party membership version and assignment. Reject expired, replayed, or stale references and provide a safe fallback. Keep reconnect references opaque and short lived.

## Test cases

- Normal group teleport to the reserved destination.
- Reuse the same reserved destination on retry.
- A synchronous `pcall` error.
- A per-player `TeleportInitFailed` event.
- Some party members arrive while others do not.
- A server shuts down during handoff.
- Destination rejects an expired or replayed ticket.
- Rejoin within the grace period and after expiry.
- Exhausted retry returns party to the lobby without duplicating queue tickets.

Studio testing is useful for development, but perform cross-place and multi-server verification in a published test experience before production.
