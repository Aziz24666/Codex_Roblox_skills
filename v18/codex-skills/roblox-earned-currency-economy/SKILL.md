---
name: roblox-earned-currency-economy
description: Design a fair Roblox economy where gameplay earns currency through fixed, server-validated rewards.
---

## Mandatory current-source research gate

Before substantive implementation, refresh the official Roblox Creator Hub documentation, Community Standards, Terms, and relevant update/deprecation notes for the exact systems involved. Check upstream tool documentation as well. Record exact source URLs, access dates, verified claims, alternatives, decisions, and a verification plan in `research/decisions/`. Re-open version-sensitive sources for every new task; do not invent citations or claim research was completed when it was not. When a platform rule or API cannot be verified, mark the affected work `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing. Treat current platform policies as hard constraints, not optional suggestions.

# Roblox Earned Currency Economy

## When to use
Use when designing non-redeemable gameplay currency, rewards, shops, economy balancing, or player progression.

## Procedure
1. Define each currency, intended use, earn sources, sinks, caps, expiration, and whether it is transferable.
2. For the requested free progression currency, allow only validated gameplay-earned grants; do not add a real-money purchase route or cash conversion.
3. Keep all balances and grants server-authoritative. Never trust client-submitted balance deltas, reward amounts, or completed objectives.
4. Record each transaction with a unique ID, player/account key, source, amount, before/after balance, timestamp, catalog/version reference, and result.
5. Enforce nonnegative balances, integer/range bounds, rate limits, and source-specific eligibility.
6. Make reward and purchase handlers idempotent under retries, reconnects, and duplicate remote calls.
7. Define conflict resolution and atomic persistence using documented Roblox data APIs and current limits.
8. Create synthetic tests for duplicated grants, replay, concurrency, disconnects, malformed amounts, overflows, and datastore failure.
9. Add economy telemetry for inflation, concentration, bottlenecks, and unintended farming using privacy-minimizing aggregates.
10. Document migration and rollback for persistent schema changes.

## Output contract
Provide currency definitions, source/sink table, transaction ledger, abuse controls, balance invariants, synthetic tests, and measured economy assumptions.

## V18 policy and implementation update

### V18 updated guidance

## Economy principles

Make gameplay-earned currency a meaningful, predictable route through ordinary progression. Define named currencies, integer units, reward sources, costs, limits, sinks, and persistence rules. Keep the economy understandable and avoid inflation, opaque conversion chains, and artificial pressure to spend.

## Deterministic earning

- Grant fixed, documented amounts for validated gameplay outcomes.
- Calculate rewards on the server from trusted state; never trust a client-submitted balance, payout, match result, or completion flag.
- Prevent duplicate claims with stable reward/transaction IDs and idempotent writes.
- Apply reasonable cooldowns, caps, and anti-exploit validation without punishing normal play.
- Display the reward and the condition for earning it before a player commits significant time.
- Provide multiple ordinary gameplay paths where practical so one activity is not mandatory.

## Spending rules

Use fixed prices and explicit grants. A purchase must exchange a known amount for a known item or quantity. Never use currency for wagers, chance-based purchases, random rewards, paid rerolls, or chance modifiers. Currency obtained directly or indirectly with Robux must never be connected to random outcomes.

A direct Robux purchase of a known currency amount, if used, must be optional, clearly disclosed, and grant exactly the stated amount. Do not make purchased currency the only way to complete core progression or unlock a tier. Apply `roblox-tiered-catalog-progression` and `roblox-player-friendly-monetization`.

## Accounting and persistence

Keep balances server-authoritative. Record each credit/debit with a unique transaction ID, source/reason, amount, currency, timestamp, and relevant product/reward ID. Reject negative, malformed, duplicated, or unauthorized transactions. Use atomic update patterns appropriate to the persistence layer; handle throttling, retry, reconnect, and partial failure without duplicating value. Do not log secrets or sensitive player information.

## Verification

Test reward eligibility, fixed amounts, duplicate claims, replayed events, unauthorized client requests, negative/overflow values, purchase retries, persistence failures, and balance reconciliation. Review currency sources and sinks for exploitability and inflation. Record evidence and label environment-specific checks NOT_RUN when not executed.
