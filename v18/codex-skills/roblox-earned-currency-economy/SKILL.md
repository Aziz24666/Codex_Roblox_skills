---
name: roblox-earned-currency-economy
description: Design a fair Roblox economy where gameplay earns currency through fixed, server-validated rewards.
---

# Earned-currency economy

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
