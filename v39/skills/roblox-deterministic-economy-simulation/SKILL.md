---
name: roblox-deterministic-economy-simulation
description: Build and interpret reproducible synthetic economy simulations for Roblox gameplay currencies.
---

# Roblox deterministic economy simulation

## Workflow
1. Gather explicit integer assumptions for each gameplay currency's initial balance, sources, sinks, and review ceiling.
2. Define a bounded time horizon and synthetic activity archetypes.
3. Model source generation before sink spending each active day.
4. Simulate progression XP and deterministic milestone rewards.
5. Review currency shortfalls, accumulated balances, and archetype progression gaps.
6. Change one parameter at a time and keep each report linked to its model version.
7. Compare results with actual human-reviewed playtests and privacy-safe aggregate observations before changing live values.

## Interpretation
A sink shortfall indicates that the modeled cohort cannot afford all modeled sink demand. A high closing balance may signal a weak sink or generous source assumptions. A progression gap is a review prompt, not necessarily a defect. Check alternate routes and whether casual players can still access worthwhile content.

## Limits
V39 runs a deterministic model based only on supplied assumptions. It does not query Roblox, inspect player records, estimate retention or revenue, or establish live economy health. Never feed player-level records into the simulator.
