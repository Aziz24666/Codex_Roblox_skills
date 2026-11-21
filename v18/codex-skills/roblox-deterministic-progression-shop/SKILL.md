---
name: roblox-deterministic-progression-shop
description: Build server-authoritative Roblox shops with fixed catalogs, explicit prices, and exact purchase grants.
---

## Mandatory current-source research gate

Before substantive implementation, refresh the official Roblox Creator Hub documentation, Community Standards, Terms, and relevant update/deprecation notes for the exact systems involved. Check upstream tool documentation as well. Record exact source URLs, access dates, verified claims, alternatives, decisions, and a verification plan in `research/decisions/`. Re-open version-sensitive sources for every new task; do not invent citations or claim research was completed when it was not. When a platform rule or API cannot be verified, mark the affected work `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing. Treat current platform policies as hard constraints, not optional suggestions.

# Roblox Deterministic Progression Shop

## When to use
Use for catalog shops, direct purchases, progression storefronts, cosmetics, emotes, titles, convenience features, and guaranteed upgrades.

## Non-negotiable design
- The player sees the exact item, benefit, currency, and price before confirming.
- Each purchase grants the named item deterministically.
- No gambling or simulated-gambling activity, wagering, staking, random purchase outcome, or chance-based paid reward is designed.
- Do not add a random reward button under a different name.
- Use a gameplay-earned, non-redeemable soft currency when the user asks for a free progression currency. Keep it separate from any platform purchase flow.

## Procedure
1. Define allowed catalog categories and exclude unsupported or prohibited categories.
2. Model immutable item IDs, tier IDs, display names, descriptions, fixed prices, prerequisites, grant type, and catalog version.
3. Make the server own the catalog and price. The client sends only an item ID and request/idempotency token.
4. Validate player state, catalog version, eligibility, ownership, tier completion, balance, and request replay on the server.
5. Atomically debit currency and grant the exact item. Use a durable transaction record and idempotency key.
6. If any step fails, prevent partial grants or double debits; define a recoverable transaction state.
7. Provide a clear preview, exact benefit summary, total price, confirmation, and receipt/ownership display.
8. Keep an earnable route and avoid pressure prompts or misleading scarcity.
9. Test insufficient balance, unknown IDs, duplicate requests, simultaneous purchases, stale catalog, incomplete prior tier, persistence failure, and reconnect recovery.
10. Research current Roblox monetization rules before exposing any platform purchase integration.

## Output contract
Provide catalog schema, currency rules, server purchase flow, idempotency design, tier gates, UI states, negative tests, and transaction evidence.

## V18 policy and implementation update

### V18 updated guidance

## Core rule

Every shop offer must have a stable product identifier, fixed contents, explicit price, currency type, availability rule, and exact grant. Do not implement random purchase outcomes, paid rerolls, wagers, or purchase-funded chance mechanics. Apply the V18 no-gambling and player-first rules in `v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md`.

## Catalog contract

Define one canonical catalog. Each product should specify:
- Stable, unique product ID.
- Display name, description, category, and icon/asset reference.
- Exact item or quantity granted.
- Exact price and currency.
- Whether it is one-time or repeatable.
- Eligibility, prerequisites, and tier.
- Whether the benefit is permanent, temporary, or subscription-dependent.
- A version or migration strategy when saved ownership changes.

The server owns the real catalog, prices, eligibility checks, balances, and grants. The client may display catalog data and request a purchase, but must never choose the authoritative price or grant contents.

## Purchase lifecycle

1. Validate the product ID against the server catalog.
2. Validate the player's eligibility, current ownership, tier state, and balance.
3. Make the purchase and grant one atomic, auditable transaction.
4. Deduct the exact listed price and grant exactly the listed contents.
5. Persist the transaction safely; make retries idempotent so reconnects or duplicate requests cannot double-charge or duplicate grants.
6. Return a clear success or failure result and refresh the visible balance/inventory from server state.
7. For Roblox developer products, verify the current official receipt-processing requirements and fulfill successful receipts through the server receipt callback. Do not treat a client prompt-finished event as proof of payment.

Reject duplicate one-time purchases unless the product explicitly supports gifting or another reviewed flow. For repeatable products, apply a server-side rate limit and preserve a transaction identifier.

## Shop UX

Show the exact final price and what is granted before opening a platform purchase prompt. State whether an item is permanent, temporary, consumable, or recurring. Provide a clear cancel path, readable category/filter navigation, controller and touch support, and accessible labels. Do not use misleading discounts, fake timers, false scarcity, pressure copy, or hidden costs.

## Progression integration

Use gameplay-earned currency as a real progression route. A purchase should not silently bypass stated prerequisites. If tier progression is used, defer to `roblox-tiered-catalog-progression`: every item in all earlier tiers must be owned before the next tier unlocks, while ensuring required items are earnable without Robux.

## Verification

Test exact price authority, insufficient balance, invalid IDs, duplicate requests, duplicate receipts, persistence retries, reconnects, ownership refresh, and exact grant contents. Record only checks actually run. Review the economy and monetization policy before approving any new offer.
