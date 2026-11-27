---
name: roblox-cross-server-matchmaking-coordination
description: Coordinate matchmaking ownership and active match state across Roblox servers using expiring MemoryStore records, fencing tokens, and best-effort messaging.
---

# Cross-server matchmaking coordination

## Goal
Coordinate queue workers, match assignment, lobby handoff, and match server ownership without assuming that one Roblox server can see another server's memory or that message delivery is guaranteed.

## Select the right service
- Use `MemoryStoreService` data structures for temporary state shared across live servers, such as queue entries, active match assignments, short-lived party reservations, and lease records.
- Use `DataStoreService` for durable player progression and records that must survive MemoryStore expiration or server shutdown.
- Use `MessagingService` for best-effort notifications, cache invalidation hints, or wake-up signals. A message is not an authoritative state transition and must not be the only record that an assignment happened.
- Use `TeleportService` for player movement, driven by a server-owned assignment that the destination revalidates.

## Lease and fencing contract
A shared assignment/worker record should carry an opaque assignment ID, queue ticket IDs, match ID, owning `game.JobId`, creation/update timestamps, an expiry, a monotonically increasing version, and a fencing token or generation. Do not store secrets or full player profiles in a broadly shared coordination payload.

1. Create or claim the record with an atomic update that checks the expected prior version/state.
2. Renew only if both owner server ID and fencing token still match.
3. Advance the generation/version when ownership changes. Stale workers must be unable to mutate a newer assignment.
4. Set a TTL longer than the lease and include a recovery margin. Expiration is expected; design cleanup/reconciliation for records that disappear.
5. Treat unknown write outcomes as unknown. Read back by stable key and reconcile before retrying.
6. Make every transition idempotent using match/ticket IDs and expected version.

## Messaging rules
- Subscribe/publish with `MessagingService` only as a signal to re-read authoritative MemoryStore state.
- Expect best-effort delivery, duplicates, delayed delivery, or missing notifications. Do not use a publish success as proof the target server acted.
- Keep messages small and privacy-minimal. Include a versioned event type and opaque reference, not credentials or personal data.
- Implement periodic reconciliation/polling so a dropped notification does not strand a party or match.

## Concurrency and cleanup
- Ensure a ticket cannot be claimed by two matchmakers, a player cannot be in two active matches, and one party cannot be assigned to two destinations.
- Claim assignment first, then mark/remove the queue ticket according to the queue acknowledgment protocol.
- Use fencing/version checks on renewals, completion, cancellation, and cleanup so an old worker cannot delete a newer record.
- Use bounded retries and exponential backoff with jitter around transient MemoryStore/MessagingService errors. Avoid hot retry loops.
- Keep TTLs bounded and observable. Periodically reconcile orphan assignments, expired leases, partially teleported parties, and tickets whose owner server no longer exists.
- Define shutdown behavior: stop intake, finish or release in-flight work safely, and let leases expire if ownership cannot be proven.

## Required deliverables
- Data ownership diagram listing MemoryStore, DataStore, MessagingService, and TeleportService responsibilities.
- Active assignment record schema, version/fencing rules, and TTL/lease policy.
- Idempotent transition table for queued, claimed, assigned, teleporting, in-match, completed, and recovery states.
- Reconciliation strategy that does not rely on MessagingService delivery.
- Failure tests for worker crash, lease expiry, duplicate notification, missing notification, concurrent claim, stale cleanup, and unknown MemoryStore write outcome.

## Non-negotiable safeguards
- MessagingService is not a database, lock, or guaranteed-delivery queue.
- MemoryStore data is ephemeral and must not contain the only copy of durable progression.
- Server ownership is checked through server-issued IDs and fencing/version tokens, never a client claim.
- Expired records are handled deliberately; do not treat expiry as evidence that a player has no durable entitlement.
