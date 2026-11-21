---
name: roblox-tiered-catalog-progression
description: Implement clear catalog tiers where all items in every earlier tier must be owned before the next tier unlocks.
---

## Mandatory current-source research gate

Before substantive implementation, refresh the official Roblox Creator Hub documentation, Community Standards, Terms, and relevant update/deprecation notes for the exact systems involved. Check upstream tool documentation as well. Record exact source URLs, access dates, verified claims, alternatives, decisions, and a verification plan in `research/decisions/`. Re-open version-sensitive sources for every new task; do not invent citations or claim research was completed when it was not. When a platform rule or API cannot be verified, mark the affected work `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing. Treat current platform policies as hard constraints, not optional suggestions.

# Roblox Tiered Catalog Progression

## When to use
Use for deterministic unlock tracks, collection completion, catalog tiers, and transparent sequential storefronts.

## Required behavior
- Every item in a tier is listed before the player starts that tier.
- Each item has a fixed, visible price and a guaranteed grant.
- Tier N+1 remains locked until the player owns every required item in Tier N.
- A locked tier explains the exact missing prerequisites.
- No chance, spin, wager, or random reward is used.

## Procedure
1. Create a versioned catalog with stable item IDs and strictly ordered tier IDs.
2. Validate unique IDs, nonnegative integer prices, known prerequisites, no cycles, and no gaps in tier order.
3. Compute completion from server-persisted ownership, not client UI or client-supplied flags.
4. On purchase, re-check the previous tier's completion in the same authoritative transaction as the debit/grant.
5. Make purchase operations idempotent and safe under duplicate/concurrent requests.
6. Add catalog migration rules for renamed, removed, or retired items. Never silently reset existing ownership.
7. Add tests for partial completion, exact completion, duplicate purchase, concurrent final item purchases, and catalog updates.
8. Display owned, available, locked, and insufficient-currency states accessibly.

## Output contract
Provide tier graph, catalog, per-tier completion rules, persistence model, migration policy, UI states, and tests.

## V18 policy and implementation update

### V18 updated guidance

## Required V18 unlock rule

For a catalog with ordered tiers T1, T2, ... Tn, a player may unlock tier Tn only when the player owns every required item in every preceding tier T1 through T(n-1). Do not reduce this to owning only one item, reaching a level threshold, or buying a single tier pass.

Use a canonical tier definition and evaluate ownership on the server. Define how retired items, limited-time items, bundles, replacements, and migrated inventories count before launch; never silently make a previously completed tier impossible to finish.

## Player-first acquisition

Every item that is required to unlock a later tier must have a clear, achievable non-Robux route, such as gameplay-earned currency, a stated quest, or a deterministic free unlock. Direct fixed-price purchases may be optional alternatives, but do not require Robux spending to satisfy a tier gate. Never put chance-based rewards, paid random items, paid rerolls, or gambling-like steps in the progression path.

Show players:
- The current tier and the next tier.
- Every required earlier-tier item.
- Which items are owned and which remain.
- The exact deterministic acquisition route and price for each remaining item.
- The precise condition that unlocks the next tier.

Do not hide requirements, change them retroactively without migration and disclosure, or use misleading progress indicators.

## Data and authority

Use stable item IDs rather than display names. Persist ownership as server-validated records. The server computes the tier-unlock predicate from canonical catalog data and the player's authoritative inventory. The client only renders the result. Make acquisition and ownership writes idempotent and safe against duplicate grants, retries, and reconnects.

Represent requirements explicitly, for example as a list of required item IDs per tier. Validate at build/test time that every required ID exists, tier IDs are unique and ordered, and no item is accidentally omitted from the requirement set.

## Verification

Cover empty inventory, partial prior-tier ownership, all prior-tier items owned, current-tier ownership, missing/retired item migration, duplicate grants, reconnects, and catalog changes. Confirm that no Robux-only purchase is required to unlock a tier. Report actual tests and unresolved migration questions.
