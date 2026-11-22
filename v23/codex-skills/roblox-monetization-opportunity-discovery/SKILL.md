---
name: roblox-monetization-opportunity-discovery
description: Find and rank the widest evidence-supported set of deterministic Roblox monetization opportunities.
---

# Monetization opportunity discovery

## Mission
Search the entire experience for the broadest viable Robux and creator-revenue portfolio. Start from actual game systems and player value, not a generic shop checklist.

## Workflow
1. Inspect project structure, design documents, Luau scripts, UI, catalog, economy, progression, multiplayer, live operations, analytics, and existing monetization.
2. Run python v23/tools/v23.py discover-opportunities --root . and inspect every catalogue entry, including those with no detected signal.
3. For each candidate, verify the feature exists, identify the player benefit, product type, fixed contents, price source, entitlement owner, persistence, support cost, and implementation effort.
4. Search underused systems: character identity, emotes, cosmetics, vehicles, pets, housing, collections, story/map content, convenience, social play, subscriptions, private servers, platform programs, ads, avatar products, and creator tools.
5. Keep in-experience sales, Creator Rewards, ads, avatar/affiliate income, and Creator Store earnings as separate portfolio lines.
6. Rank ideas by player value, fit, effort, risk, and validated aggregate demand. Keep missing-evidence ideas in an exploration backlog.
7. Give a phased roadmap: quick deterministic cosmetics; supported durable passes; exact repeat purchases; authored content; subscriptions only when delivery is dependable; eligible platform/creator-business programs.
8. Re-check current Roblox requirements and Creator Dashboard settings before implementation.

## Strict exclusions
Never recommend paid random outcomes, gambling-like mechanics, wagers, spins, mystery purchases, random loot, paid rerolls, chance modifiers, or a purchase path that funds a random reward indirectly through tickets, gems, keys, or other currency.

## Output
Return the full opportunity inventory, evidence paths, best-fit ranked shortlist, no-evidence exploration list, player-value rationale, effort, eligibility unknowns, implementation dependencies, and a 30/60/90-day roadmap. Do not invent revenue forecasts or guaranteed Robux.

## Shared contracts
Preserve V18 no-gambling, V19 evidence, V20 server-authority, V21 fair monetization, and V22 platform-monetization rules.
