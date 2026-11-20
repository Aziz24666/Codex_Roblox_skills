---
name: roblox-tiered-catalog-progression
description: Implement clear catalog tiers where all items in every earlier tier must be owned before the next tier unlocks.
---

# Tiered catalog progression

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
