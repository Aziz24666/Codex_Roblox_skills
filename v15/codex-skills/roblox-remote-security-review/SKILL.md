---
name: roblox-remote-security-review
description: Review Roblox RemoteEvents, RemoteFunctions, prompts, and other client-originated actions for server authority, payload validation, permissions, rate limits, and negative tests.
---

# Roblox Remote Security Review

## When to use
Use when a feature accepts client-originated input, changes shared state, grants rewards, changes inventory/progression, controls interactions, or exposes a remote/API boundary.

## Procedure
1. Inventory every client-triggerable entry point and trace each handler to the consequential state change.
2. For each action, document caller, payload shape, maximum size, expected state, ownership rule, range/proximity rule, cooldown/rate limit, response, and failure behavior.
3. Treat client fields as untrusted. Validate structure, types, finite numeric values, ranges, allowlisted values, instance class/ancestry, caller state, permissions, ownership, and context on the server as appropriate.
4. Ensure the server derives consequential values (rewards, costs, inventory, progression, permissions, outcomes) from trusted server-side state and configuration.
5. Bound expensive work and payload sizes. Apply rate limits before costly processing and clean per-player limiter state on disconnect.
6. Check ordering and concurrency: duplicate requests, stale state, simultaneous requests, reconnects, and disconnects during an operation.
7. Add negative tests for malformed, missing, extra, oversized, non-finite, unauthorized, out-of-range, stale, repeated, and concurrent inputs as applicable.
8. Review logs for privacy and spam; log rejection categories without exposing secrets or unnecessary player data.
9. Use current official Roblox documentation for security-sensitive platform behavior and record source URLs in project research notes.
10. Report every unvalidated path as a blocker until the missing server-side control or test is addressed.

## Never rely on
- UI visibility, local cooldowns, client-side validation, or prompt enabled state as authorization.
- Client-supplied costs, rewards, ownership claims, arbitrary instance paths, or requested state outcomes.
- A happy-path test as proof that invalid requests are rejected.

## Output contract
Produce an action inventory with payload, server checks, authoritative mutation, rate limiting, negative tests, result, and unresolved risks. Do not claim a complete security audit from a partial endpoint scan.
