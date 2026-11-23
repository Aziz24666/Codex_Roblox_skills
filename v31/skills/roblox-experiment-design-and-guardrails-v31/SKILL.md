---
name: roblox-experiment-design-and-guardrails-v31
description: Design ethical Roblox gameplay experiments with predeclared hypotheses, aggregate metrics, fair controls, and technical/player-experience stop conditions.
---

# Experiment Design and Guardrails

## Design

1. Write one falsifiable hypothesis about a gameplay or usability change.
2. Describe the control and candidate experiences precisely; keep outcomes, prices, and eligibility clear.
3. Choose one primary aggregate metric and a small set of secondary metrics before starting.
4. Predeclare a sample-size floor, observation window, and minimum data-quality requirements.
5. Add guardrails for server errors, performance, persistence failures, purchase issues, accessibility, and player support.
6. Define stop conditions before rollout. Do not change the primary metric after looking at results.
7. Keep the test reversible and limited to an approved staged environment.

## Interpret

Compare like-for-like periods and cohorts, note missing or delayed data, and do not claim causation from a simple before/after comparison. Document uncertainty, negative outcomes, and effects on different play styles. Avoid a single engagement or revenue number as a proxy for overall quality.

## Safety

Do not experiment with paid random outcomes, hidden odds, individual-spender targeting, artificial scarcity, coercive notifications, or intentionally exhausting session loops. Do not compromise free progression or make purchases necessary to understand the game. All production experiments need human approval and a rollback path.
