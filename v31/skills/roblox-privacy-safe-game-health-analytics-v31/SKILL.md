---
name: roblox-privacy-safe-game-health-analytics-v31
description: Review aggregate Roblox experience health indicators using minimum sample sizes, freshness checks, and predeclared quality guardrails.
---

# Privacy-Safe Game Health Analytics

## Workflow

1. Select a small set of aggregate indicators that reflect technical quality and player experience.
2. Define maximum/minimum thresholds before examining the next snapshot.
3. Require a project-appropriate minimum sample size and maximum snapshot age.
4. Export aggregate metrics only; do not export player-level rows, account identifiers, chat, private support text, or individual purchase histories.
5. Evaluate snapshots with the V31 CLI.
6. Treat `hold` as insufficient evidence, not as a passing result.
7. Investigate warning/alert signals with additional aggregate evidence and qualitative player feedback.
8. Record known limits, sample definition, source, and observation window.

## Interpretation

A clear result means the supplied values fall within the declared guardrails. It is not a universal quality score, proof of player wellbeing, or assurance of platform compliance. Missing values are not zero and low sample sizes must not be overinterpreted.

## Safety

Do not infer sensitive player traits, create individual-spender segments, or optimize engagement at the expense of player choice. Keep free progression worthwhile and paid outcomes fixed and transparent.
