---
name: roblox-server-authority-review-v28
description: Review Roblox Luau RemoteEvents and RemoteFunctions for server-authority boundaries, input validation, ownership, rate limiting, and duplicate-request safety.
---

# Roblox Server Authority Review

## Goal

Review client/server boundaries defensively and improve server-side correctness. Never generate exploit payloads, scripts for unauthorized access, or instructions to abuse live games.

## Workflow

1. Inventory every client-to-server RemoteEvent and RemoteFunction and locate its server handler.
2. Write a contract for each remote: caller, arguments, types, bounds, allowed values, state preconditions, response, and expected rejection.
3. Treat all client arguments and all client-reported outcomes as untrusted. Derive the player from the server callback parameter.
4. Confirm the server validates type, finite numeric values, range, collection size, enum values, Instance class/ancestry, ownership, permissions, distance, cooldown, and match state as applicable.
5. Ensure critical currency, damage, rewards, inventory, purchases, progression, and persistent-data changes are computed and authorized on the server.
6. Add server-side rate limiting before expensive work. Do not rely on a LocalScript debounce as a security control.
7. Define retry and duplicate semantics. Use server-controlled request/receipt tracking and atomic updates where needed; never treat a client-provided ID as proof of authorization.
8. Test valid, malformed, unauthorized, rapid, concurrent, and repeated requests in a private Studio test place with synthetic state.
9. Report each finding with the exact source location, evidence, impact, uncertainty, and a safe remediation. Do not claim a vulnerability solely from a static pattern.

## Review output

Return a remote inventory, contract table, server-side validation checklist, rate-limit and idempotency analysis, test cases, and residual risks. Distinguish verified code behavior from heuristic suspicion and missing context.

## Non-negotiable safeguards

- Never move authority for currency, damage, rewards, inventory, purchase entitlement, or DataStore mutation to the client.
- Never suggest trusting a client-supplied amount, ownership flag, target identity, or result.
- Never run untrusted code or send test requests to a production experience.
- Keep changes narrow, reviewed, and covered by Studio tests.
