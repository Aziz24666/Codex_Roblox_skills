---
name: roblox-resilient-data-saving-and-recovery
description: Design reliable Roblox DataStore saves, bounded retries, request-budget awareness, autosaves, and shutdown flushing.
---

# Roblox resilient data saving and recovery

## Design
- Prefer UpdateAsync for shared-key or read-modify-write mutations.
- Keep UpdateAsync callbacks pure, non-yielding, and deterministic.
- Protect network calls with pcall and classify retryable versus permanent errors.
- Use bounded exponential backoff with jitter; avoid synchronized retry storms.
- Serialize requests per key so an older retry cannot overwrite a newer state.
- Track request budgets. UpdateAsync consumes both read and write budgets.
- Coalesce redundant writes and stagger each profile's first autosave.
- Measure serialized payload length and remain comfortably below the 4 MiB per-key maximum.
- Treat unknown write outcomes as ambiguous: reload and reconcile before replaying a mutation.
- Save on player departure and use BindToClose for shutdown flushes, keeping within its 30-second platform wait.

## Recovery plan
Define the source of truth, last confirmed save, dirty revision, retry schedule, and what happens when save completion is unknown. Never discard dirty state merely because an API call timed out. Do not overwrite a newer version with delayed stale data.

## Tests
Cover transient and permanent failures, throttling, lost acknowledgements, concurrent writes, request-budget exhaustion, server shutdown, reconnects, and oversized profiles.

## Evidence
Separate local unit tests, Studio multi-server tests, live test-experience observations, and production metrics. A passing offline contract audit is not evidence of DataStore correctness.
