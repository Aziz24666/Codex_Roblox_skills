# V41 matchmaking architecture

## Responsibility map

| Roblox service / component | Responsibility | Must not be used for |
|---|---|---|
| Lobby/game servers | Validate requests, party membership, rating inputs, and state transitions | Trusting client-supplied rating, leader, or destination |
| `MemoryStoreQueue` | Short-lived, cross-server queue tickets and dequeue/invisibility workflow | Durable player progress or permanent history |
| `MemoryStoreHashMap` | Temporary party/match assignment records, owner leases, versions, and fencing tokens | A permanent source of truth for currency, inventory, or entitlements |
| `DataStoreService` | Durable player data and durable records that must survive ephemeral store expiry | Fast transient queue coordination |
| `MessagingService` | Best-effort cross-server wake-up and notification hints | Guaranteed delivery, locks, or authoritative assignment commits |
| `TeleportService` | Server-initiated routing to the assigned place/server | Proving that a player arrived or authorizing an unverified ticket |

## Matchmaking state machine

Recommended lifecycle:

`forming -> queued -> claimed -> assigned -> teleporting -> in_match -> completed`

Recovery states can include `cancelled`, `expired`, `recovery_pending`, and `requeued`. Define allowed transitions and expected record version for every operation. Each mutation is idempotent using the ticket or match ID plus version. A stale worker cannot advance or delete a newer record.

## Queue ticket

Use one ticket per indivisible party. Keep ticket data bounded and privacy-minimal. A practical contract includes:

- Stable opaque `ticket_id` and ticket schema version.
- Party/roster reference and server-validated party size.
- Server-derived skill rating or rating bucket.
- Server enqueue timestamp and stable tie-breaker.
- Queue/mode/region constraints that are actually needed.
- Expected party membership version and operation idempotency key.

Avoid secrets, credentials, raw chat, contact details, profile dumps, and any payload field that the destination can look up from authoritative state. A player identifier may be required for the server workflow, but do not expose it in public messages or client-visible data unless necessary.

## Queue processing protocol

1. Validate party membership, eligibility, capacity, and rating on a server.
2. Create or reuse the party's idempotent ticket.
3. Add it to a MemoryStore queue with a bounded TTL. TTL should be longer than the intended maximum wait plus the defined recovery margin.
4. Read a bounded batch. If a queue item is temporarily invisible to another worker, assume it can reappear after its invisibility timeout.
5. Build a candidate match using deterministic ranking and an explicit skill-window expansion rule.
6. Validate that selected tickets still exist, have the same membership/ticket versions, meet constraints, and do not share members.
7. Atomically claim the complete match assignment with a unique assignment ID, server owner, lease, version, and fencing token.
8. Read back/revalidate the claim if the write outcome is ambiguous.
9. Remove/acknowledge the queue entries only after the assignment is successfully claimed and reconciled.
10. Initiate teleport. Do not consider the match complete until destination servers confirm the expected arrivals against the authoritative assignment.

## Match quality and fairness

For a skill-based game, choose a starting rating window and a controlled widening schedule based on server-side wait time. Set a maximum window and a maximum wait. Decide how to handle the hard limit explicitly. The policy should balance rating quality with queue time and party sizes; party tickets remain indivisible. Stable tie-breaking makes behavior testable. Avoid using protected or sensitive attributes as rating inputs.

## Cross-server ownership

Store short-lived assignment state in MemoryStore, not a server's local table alone. Records should identify the owner server (`game.JobId`), assignment ID, lease expiry, monotonic record version, and fencing generation. Only the current owner with the current fencing generation may renew or transition the record. A replacement worker must claim a newer version/generation.

Use `MessagingService` to notify a server that something may have changed; always re-read the authoritative record. Delivery can be missing, duplicated, or delayed. Add periodic reconciliation so a missed notification does not strand a player.

## Capacity and quotas

The example configuration sets the maximum group size to 50, matching the documented `TeleportAsync` player-list maximum. Tune smaller values based on experience design and performance. Validate MemoryStore quotas, request budgets, item size, queue TTL, and throttling with real test runs; the local validator cannot infer a safe throughput limit for your experience.

## Failure matrix

| Failure | Required response |
|---|---|
| MemoryStore request throws or times out | Protected call, bounded retry with jitter, then reconcile by stable ID |
| Unknown write outcome | Read authoritative state; do not blindly duplicate or delete |
| Worker crashes while queue item invisible | Allow item to reappear; idempotent ticket ID prevents duplicate assignment |
| Two workers claim same candidate | Conditional claim/version/fencing check lets only one transition win |
| Queue item expires | Reconcile party/assignment state, return a recoverable outcome; do not erase durable progress |
| Messaging event is missed | Destination/owner periodically reconciles authoritative state |
| Party member leaves before assignment | Cancel or rebuild the entire party ticket under a new version |
| Teleport partly succeeds | Maintain one assignment/destination, track each member's arrival, retry or requeue as a party |
| Owner lease expires | New worker claims higher generation; old owner is fenced out |

## Verification boundary
V41's CLI validates declared JSON contracts and simulates supplied synthetic ticket metadata. It does not call Roblox APIs, access real MemoryStore queues, measure live network latency, launch match servers, or prove fairness/concurrency. Multi-server Studio testing and published-experience validation remain required.
