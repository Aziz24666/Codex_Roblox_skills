---
name: roblox-skill-based-matchmaking-queue-design
description: Design server-authoritative Roblox matchmaking queues that preserve party atomicity, expand skill windows safely, and handle ephemeral MemoryStore failures.
---

# Skill-based matchmaking queue design

## Goal
Build a predictable matchmaking service that groups compatible players without splitting parties, losing tickets on transient failures, trusting client claims, or treating temporary queue data as durable player state.

## Architecture boundaries
- Use `MemoryStoreService` for cross-server, short-lived queue coordination. `MemoryStoreQueue` is appropriate for FIFO or priority-oriented ticket intake; `MemoryStoreHashMap` can hold short-lived assignment/session records.
- Use `DataStoreService` for durable player progress and long-lived records. A MemoryStore item expiring is normal; it must never be the only copy of durable inventory, currency, progression, or entitlements.
- Keep queue writes and match decisions on the server. Clients may request queue entry or cancellation, but the server computes eligibility, party size, skill inputs, queue ticket IDs, and authoritative state.
- Treat all MemoryStore calls as fallible: wrap calls in `pcall`, apply bounded retry/backoff with jitter, and surface a recoverable service-degraded state instead of silently dropping tickets.

## Ticket contract
Every queue ticket should use a stable opaque `ticket_id` and include only the minimal matching fields required by the experience: party member references, party size, server-derived skill/rating bucket, enqueue time, region/latency bucket if actually measured, queue type, ticket version, and an idempotency token. Do not include passwords, authentication secrets, personal contact data, raw chat, or unnecessary player profiles. Keep payload size bounded.

A party is one queue ticket. Never split its members to fill a match. Validate the complete membership and size on the server before enqueue, after dequeue, before reservation, and at the destination. Reject duplicate member assignment across tickets.

## Queue lifecycle
1. Validate the requesting player and current party membership on the server.
2. Create or reuse an idempotent queue ticket. A repeated request with the same logical operation must not create another active ticket.
3. Add the ticket with a bounded expiration. Choose TTL based on the maximum intended wait and cleanup/rejoin policy; do not assume the queue entry is permanent.
4. Read a bounded batch. If using `MemoryStoreQueue:ReadAsync`, account for the invisibility timeout: unacknowledged items can become visible again after timeout, including when a worker crashes.
5. Build a candidate match using a deterministic tie-breaker and the same queue snapshot/version. Validate the whole party and skill window.
6. Claim the match/assignment in shared state using an atomic update or compare-and-set style version check and a unique fencing token. Only one coordinator may win the assignment.
7. Remove queue entries only after the assignment claim is recorded and the claim is revalidated. If the claim is uncertain, reconcile by ticket ID and version rather than blindly removing or enqueueing duplicates.
8. Expire abandoned tickets and reconcile orphaned assignment records. Preserve a party ticket as one unit when a retry returns it to the queue.

## Skill expansion and fairness
- Start with a narrow rating window and expand it as the oldest ticket waits, using a documented step and maximum. Derive expansion from server time and enqueue timestamp, not client time.
- Keep a hard maximum wait and define what happens at the limit: widen to an explicit ceiling, offer a broader mode, or return the party to a lobby. Do not promise a match where the pool cannot satisfy minimum player count.
- Decide how latency/region, input mode, team balance, and party composition affect eligibility. Do not use opaque or protected personal attributes as skill inputs.
- FIFO fairness and rating quality conflict. Document the ranking order, avoid starvation of parties near the edge of the skill window, and instrument aggregate wait bands without logging unnecessary personal data.
- Use a stable ordering for ties (enqueue timestamp then ticket ID) so test runs are repeatable.

## Failure handling
- Distinguish transient throttling/timeouts from invalid ticket data and permanent configuration errors.
- On timeout with an unknown write outcome, read the authoritative ticket/assignment record before retrying.
- If MemoryStore is unavailable, stop new assignments safely; keep players in a recoverable lobby state and avoid creating unbounded local queues that cannot coordinate across servers.
- Handle duplicate queue reads, expired tickets, server shutdown, stale assignment leases, and two coordinators selecting the same ticket.
- Never acknowledge/delete an item before the associated assignment is safely claimed.

## Required deliverables
- Queue/ticket state diagram and authoritative state owner.
- Ticket schema, idempotency rules, TTL and invisibility-timeout policy.
- Party atomicity rules, match sizing, rating-window expansion, tie-breakers, and starvation policy.
- Cross-server assignment claim and fencing-token design.
- Failure matrix for throttling, timeouts, worker crashes, duplicate reads, expired leases, and ambiguous outcomes.
- Server-side implementation plan and a multi-server Studio/published-test checklist.

## Non-negotiable safeguards
- Matchmaking tickets are ephemeral coordination data, not durable player saves.
- A party is never split without an explicit game design that changes party membership before enqueue.
- Clients cannot set their rating, queue priority, team, ticket ownership, match assignment, or destination.
- Queue removal follows confirmed assignment, not the other way around.
- A local simulator or passing metadata audit is not proof of live queue fairness or concurrency safety.
