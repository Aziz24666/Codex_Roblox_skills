# V20 Server Authority, Remote Boundaries, and Player Data

## Remote contract design

For every client-to-server operation, define a stable operation ID, accepted payload schema, rate limit, ownership rule, context rule, side-effect classification, and idempotency requirement. Enforce these rules on the server even when the client UI already checks them.

Reject unknown operations and malformed, oversized, stale, or out-of-context requests. Avoid trusting client-provided prices, rewards, damage, distance, ownership, inventory contents, or authorization flags. Derive consequential values from server-owned state.

Use per-player and, where appropriate, per-operation throttles. Ensure a rejected request does not partially mutate state. Keep validation and authorization close to the server-owned operation rather than scattering checks across UI code.

## Persistence lifecycle

Model load, active session, save, release, migration, and recovery as explicit lifecycle states. Make save transforms safe under retry and concurrent invocation. Set bounded retry policies and observe request budgets rather than looping indefinitely.

A load failure must not silently create and save a fresh profile over existing data. Preserve the last known good state, enter a safe mode or fail closed, surface an actionable error, and route the case to a recovery owner.

## Migration engineering

- Store a schema version in each profile.
- Add migrations as adjacent, deterministic, idempotent steps.
- Validate old and new shapes, defaults, bounds, and unknown fields.
- Run each migration twice against an isolated fixture and compare the output.
- Keep a backup/restore rehearsal and a forward-recovery plan for irreversible changes.
- Never test migrations against production player keys.

## Transaction handling

Treat external delivery as at-least-once unless the provider documents stronger behavior. Persist the receipt/transaction identifier with the grant decision so a retry cannot duplicate value. Separate request acceptance from actual fulfillment, and record enough metadata to reconcile discrepancies without logging sensitive values.

See the V20 production contract schema and V19 evidence rules before declaring the implementation ready.
