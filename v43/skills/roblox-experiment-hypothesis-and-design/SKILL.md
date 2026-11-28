---
name: roblox-experiment-hypothesis-and-design
description: Design useful Roblox in-game experiments with a causal hypothesis, one primary metric, feasible audience and duration, and predeclared decision rules.
---

# Roblox experiment hypothesis and design

## Start with one causal question
Write a hypothesis before changing the game:
- What single config value or feature behavior changes?
- What player behavior should change?
- Why should the change cause that behavior?
- Which outcome would support the hypothesis, and which result would reject it?

Prefer one config key per in-game experiment. Keep the control and treatment values explicit and easy to explain. Avoid bundling unrelated features into one treatment; if the change is complex, split it into separate experiments with independent hypotheses.

## Select metrics before the experiment
- Choose one primary goal metric that directly tests the hypothesis.
- Choose learning metrics that explain the result, not a long list of metrics to search for a favorable result after the fact.
- Add up to three custom metrics only when existing server-side custom, economy, or funnel events answer an important question.
- Define a metric's unit, population, denominator, and desired direction.
- Treat guardrails as protection against unintended harm, not as extra opportunities to declare a win.

## Check feasibility
- Use Roblox's displayed minimum detectable effect (MDE) for the planned audience, rollout, duration, and variant split.
- Confirm that the eligible player population and expected sample per variant are adequate for the chosen goal metric.
- Narrow targeting only when it is important to the hypothesis; smaller audiences make the detectable effect larger.
- Roblox in-experience experiments support one baseline and up to two treatment variants, with a duration between 14 and 60 days.
- Prefer a simple control/treatment split when it answers the question. More variants divide the available sample.

## Pre-register the decision
Before scheduling, document:
- Primary metric and desired direction.
- At least one guardrail, declared before scheduling, with a stable metric ID, platform/custom metric reference, and harmful direction (increase or decrease).
- Planned duration and rollout percentage.
- Sample feasibility and MDE review.
- Audience targeting and possible interactions with other running experiments.
- Conditions that justify stopping for critical harm or invalid assignment data.
- Who reviews results and approves any final config change.

## Non-negotiable safeguards
- Do not stop early because a variant looks successful.
- Do not change unrelated content, config rules, or event instrumentation during the experiment.
- Do not treat non-significant results as proof of equivalence.
- Do not turn a single positive metric into a launch decision while a guardrail has significantly worsened.
- Do not run paid-random-outcome, gambling, or pressure-based spending experiments.
