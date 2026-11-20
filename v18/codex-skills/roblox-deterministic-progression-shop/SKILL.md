---
name: roblox-deterministic-progression-shop
description: Build server-authoritative Roblox shops with fixed catalogs, explicit prices, and exact purchase grants.
---

# Deterministic progression shop

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
