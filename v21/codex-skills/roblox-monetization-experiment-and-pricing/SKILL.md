---
name: roblox-monetization-experiment-and-pricing
description: Design controlled, privacy-safe price and storefront experiments from measured Roblox game metrics.
---

# Monetization experiments and pricing

## When to use
Use when pricing, offer placement, storefront discovery, bundles, or conversion needs to be evaluated.

## Procedure
1. Establish a baseline window and verify event definitions, sample size, platform, region handling, and data quality.
2. Track aggregate funnel stages such as eligible shop impressions, shop views, product detail views, purchase prompts, completed purchases, unique payers, refunds/chargebacks where available, and post-purchase retention.
3. Change one major variable per experiment. Predefine the primary metric, guardrail metrics, duration, minimum sample, stop conditions, and decision rule.
4. Evaluate net outcomes alongside retention, satisfaction, support contacts, refunds, and gameplay balance. A conversion increase is not a win when it damages retention or player trust.
5. Prefer official managed/automated price optimization and regional pricing capabilities when they apply. Verify current availability, eligibility, and configuration in Creator Dashboard before claiming they are active.
6. Report confidence intervals or uncertainty when the data supports them. Label small samples inconclusive.
7. Keep tests consistent, avoid overlapping experiments that make attribution impossible, and record experiment versions and dates.

## Hard constraints
- Use aggregate, privacy-safe reporting. Do not target or rank individual players by vulnerability or sensitive traits.
- Do not use fake discounts, false scarcity, misleading timers, forced purchase interruptions, hidden costs, or high-pressure wording.
- Do not recommend gambling, chance-based purchases, or paid changes to random outcomes.
- Do not silently change an existing player's paid entitlement or the advertised benefit.

## Output contract
Return hypothesis, baseline, experiment design, metrics, guardrails, sample limitations, stop rules, result, and next decision. Do not call an experiment successful until the data supports that conclusion.

## V18 shared workflow and handoff contract
Preserve approval gates and no-gambling economy policy.

## V19 verification and evaluation contract
Use evidence-backed metric definitions and reproducible test plans.

## V20 production reliability contract
Protect telemetry privacy and production rollout safety.

## V21 sustainable monetization contract
Optimize for sustainable aggregate value and player trust, not short-term spend extraction.
