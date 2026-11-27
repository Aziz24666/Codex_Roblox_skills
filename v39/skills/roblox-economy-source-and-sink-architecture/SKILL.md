---
name: roblox-economy-source-and-sink-architecture
description: Design understandable, server-authoritative gameplay currency sources and sinks for Roblox experiences.
---

# Roblox economy source and sink architecture

## Goal
Create a transparent gameplay economy that is understandable, sustainable, and resistant to duplication or inflation exploits.

## Workflow
1. List the gameplay currencies and what each one is for. Prefer fewer currencies with distinct purposes.
2. Map every source and sink, including amount, eligibility, cooldown, repeatability, and authoritative server owner.
3. Make rewards idempotent where retries can occur. A reward must not be granted twice because a client repeats a request.
4. Validate purchases/upgrades server-side and check balances atomically with the state change.
5. Model legitimate casual and frequent gameplay separately using synthetic activity assumptions, not individual player profiles.
6. Define affordability, balance ceiling, and inflation review thresholds that fit the actual game.
7. Add sinks that create optional value without coercing players or blocking essential free progression.
8. Ensure every economy path remains fair, explainable, and testable.

## Roblox implementation reminders
Clients may display prices and request actions but must not be authoritative for balances, reward amounts, ownership, or transaction completion. Validate remote arguments, rate-limit sensitive actions, and use idempotent server-side transaction identifiers where appropriate.

## Output
A source/sink map, ownership diagram, transaction invariants, failure/retry rules, and synthetic scenario model.

## Guardrails
Do not design gambling, wagers, paid random outcomes, or manipulative spending pressure. Do not profile individual players by spend. Keep paid items disclosed and optional, and preserve worthwhile free progression.
