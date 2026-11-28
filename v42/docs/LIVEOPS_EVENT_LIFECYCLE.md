# LiveOps event lifecycle and scheduling

## Design model

Treat every scheduled event as a versioned manifest with a stable event ID, schedule group, timezone-aware start/end instants, config key dependencies, one boolean enable flag, test cases, and an explicit lifecycle state.

Recommended lifecycle:

planned → staged → scheduled → active → completed

A cancellation path can leave staged/scheduled states. A rollback path disables the event through a separately approved configuration change and then runs idempotent cleanup.

## Time and scheduling

- Use ISO 8601 timestamps with Z or an explicit UTC offset.
- Store the event's intended display timezone separately in product/UI configuration if necessary; never store a naive local timestamp as the authoritative boundary.
- Compare UTC instants on the server. Do not assume a server's local timezone.
- Keep overlapping event windows out of the same mutually exclusive schedule group.
- Do not assume publishing a config and updating every running server is instantaneous. ConfigSnapshot is a snapshot and requires refresh.
- For multiple servers, make activation and completion idempotent. A restarted server must reconcile the current event window and authoritative state before it enables content.

## Event state and rewards

Use a durable, server-authoritative event lifecycle record for events that need cross-server coordination or reward settlement. Store persistent player progress in DataStore, ephemeral locks/coordination in MemoryStore where suitable, and use idempotency keys for each reward grant. Never let a client claim that an event started, completed, or granted a reward.

## Failure planning

Define a tested fallback for missing configs, delayed publication, failed initial config loads, stale snapshots, overlapping schedules, cancellation, partial cleanup, and server restarts.

## Preflight checklist

1. Validate event IDs, timezone-aware start/end, and schedule-group conflicts.
2. Verify all referenced config keys and the boolean enabled key.
3. Run event start/end/restart/cancellation tests in an isolated test experience.
4. Review reward idempotency and any required DataStore migration.
5. Verify safe fallback and a human-approved disable/rollback path.
