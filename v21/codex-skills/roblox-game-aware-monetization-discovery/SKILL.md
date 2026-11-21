---
name: roblox-game-aware-monetization-discovery
description: Inspect a Roblox project and discover monetization offers that fit its actual game loops and player value.
---

# Game-aware monetization discovery

## When to use
Use when asked to discover, audit, rank, or expand monetization opportunities for an existing Roblox experience.

## Objective
Find the strongest sustainable, game-matched direct-purchase opportunities from evidence in the project. Optimize for long-term, player-respecting revenue, not maximum pressure or maximum spend from an individual player.

## Required discovery procedure
1. Inspect the project before suggesting products. Read the game brief, design documents, progression/economy definitions, catalogs, UI, player-data model, and relevant Luau code.
2. Classify the actual genre, audience, main loop, session loop, social loop, progression, customization, content cadence, existing shop, and current economy. Mark unknowns as unknown.
3. Cite concrete file paths, symbols, and short evidence excerpts for every inferred opportunity. Separate implemented systems from plans, comments, dead code, and assumptions.
4. Build an opportunity matrix using player value, game-fit, evidence confidence, implementation cost, operational cost, and fairness risk. Rank by sustainable fit; never label a fit score as a revenue forecast.
5. Recommend only fixed, clearly described products: cosmetics, emotes, customization, optional convenience, fixed-quantity currency where appropriate, clearly defined game passes, subscriptions with ongoing delivered benefits, or private servers when the game supports them.
6. Suggest limited-time benefits only when the exact benefit and duration are deterministic and disclosed. They must not modify probabilities or random outcomes.
7. Identify missing analytics needed to estimate conversion or revenue. Do not invent prices, player demand, conversion rates, or expected Robux.
8. Present an implementation order: low-risk/high-fit opportunities first, followed by experiments supported by actual data.

## Hard constraints
- The V18 no-gambling policy is mandatory. Do not design, implement, recommend, or retain gambling or gambling-like mechanics.
- Every paid outcome must be fixed, named, and knowable before purchase. Do not recommend paid chance changes or random purchase outcomes.
- Keep the core game playable and meaningful without purchases. Never recommend artificial frustration, paywalls on essential progression, fake scarcity, or pressure tactics.
- Never optimize offers using sensitive personal traits or individual vulnerability. Use privacy-safe aggregate metrics only.
- Do not claim that a feature is monetizable merely because a keyword appears. Require design and runtime evidence.

## Tool-assisted scan
Run `python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json`. The scanner is a deterministic evidence collector, not an autonomous Roblox runtime inspector or an LLM replacement. Review its evidence and limitations before approving any recommendation.

## Output contract
Return detected game profile, evidence-backed offer ranking, exact player value, purchase type, prerequisites, implementation effort, fairness risks, required analytics, rejected/blocked findings at a high level, and a test plan. Explicitly label all revenue estimates as unavailable unless supported by real aggregate metrics.

## V18 shared workflow and handoff contract
Preserve shared task intake, dependency-aware workstreams, approval gates, and the mandatory no-gambling economy policy.

## V19 verification and evaluation contract
Use risk-based tests and evidence records. Mark unrun Studio and live-purchase checks NOT_RUN or BLOCKED.

## V20 production reliability contract
Keep server authority, persistence, verified receipts, idempotent exact grants, and operational rollback controls.

## V21 sustainable monetization contract
Discover from project evidence, rank by player value and game-fit, and optimize sustainable aggregate outcomes. Never fabricate revenue forecasts or use manipulative monetization patterns.
