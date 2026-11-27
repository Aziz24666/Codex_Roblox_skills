---
name: roblox-profile-lifecycle-and-session-ownership
description: Design server-authoritative player profile loading, exclusive session ownership, lease renewal, and safe release.
---

# Roblox profile lifecycle and session ownership

## Goal
Prevent simultaneous writable profile sessions, stale-server overwrites, and unsafe loading after an ambiguous lock result.

## Lifecycle
1. Review Roblox's current `DataStoreWrapper` and `SessionLockedDataStoreWrapper` reference implementation first. It demonstrates per-key request ordering/retries and session locks. The Creator Hub warns that its sample has not been proven at scale; do not copy it unchanged. Adapt and test it thoroughly, or implement the same ownership invariants in a reviewed custom wrapper.
2. Define one profile owner service and one well-defined profile state machine: unloaded, loading, active, saving, releasing, failed.
3. Acquire the session lease through an UpdateAsync transform using a unique owner token and bounded expiry.
4. Never make a profile writable unless both its data and session ownership are confirmed.
5. On contention, wait with a bounded policy or fail closed. Do not load a second copy and continue saving.
6. Refresh the lease with a non-yielding transform that verifies the current owner token.
7. Before save/release, verify the owner token still matches. A stale server must never clear or overwrite a newer session.
8. On PlayerRemoving, save and release only that session's lock.
9. On BindToClose, flush active profiles concurrently within a bounded shutdown budget and stop accepting new mutations.

## Failure cases
Specify behavior for timeouts, ambiguous reads, expired leases, server crashes, duplicate joins, teleports, and lock-renewal failures. If ownership becomes uncertain, freeze mutations and use a safe recovery flow instead of guessing.

## Required deliverables
Profile state machine, lock record contract, ownership invariants, stale lease policy, retry policy, reconnect behavior, and race-condition test matrix.

## Non-negotiable safeguards
- Server owns all persistent mutations.
- Use a unique server-session token, not a client-provided identifier.
- Release only a lock owned by the current session.
- Keep per-key writes serialized.
- Test with multiple servers in a separate test experience.
