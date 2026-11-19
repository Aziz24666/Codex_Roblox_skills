---
name: roblox-remote-security-review
description: Review Roblox client-originated actions for server authority, payload validation, permissions, rate limits, and negative tests.
---

## Mandatory current-source research gate

Before substantive implementation, perform fresh online research using the current official Roblox Creator Hub/API documentation and relevant Roblox platform updates, deprecations, security guidance, or release notes. Check upstream documentation for any external tool or framework involved. Compare viable approaches when an API, architecture, or platform behavior is version-sensitive. Record exact source URLs, access dates, verified claims, alternatives, decisions, and the verification plan in `research/decisions/`. Re-open sources for each new task; previous research is background, not a substitute for current verification. Never invent a citation or claim a source was checked when it was not. If a critical platform or tool claim cannot be verified, mark the affected implementation `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing.

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
