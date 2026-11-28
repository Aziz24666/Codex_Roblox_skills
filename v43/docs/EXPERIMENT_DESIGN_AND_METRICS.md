# Experiment design and metrics

## Why experiments exist

Roblox Creator Hub Experiments can compare in-game config values across assigned player groups and help measure the causal impact of a change. Use them to answer one clear product question, not to search many metrics until a favorable result appears.

This V43 toolkit models in-game config experiments. It does not model matchmaking experiments or build a custom assignment platform.

## Hypothesis template

Write the hypothesis before editing any live config:
- Change: the one setting or behavior being tested.
- Expected outcome: the player behavior expected to change.
- Rationale: why the change should cause that behavior.
- Success criteria: the primary metric and guardrails that define a useful result.

Prefer one config key and one treatment. Roblox supports one baseline and up to two treatment variants. Each additional variant divides the available sample, so more variants require a larger population or a larger detectable effect.

## Metrics

Choose one primary goal metric. Roblox default metrics include D1 retention, D7 retention, Playtime, ARPU, ARPPU, payer conversion rate, and session time. Custom metrics may also be the goal. Select a small number of learning metrics that explain why a result moved. Up to three custom metrics can be added to an in-game experiment.

Custom metrics must be based on AnalyticsService custom, economy, or funnel events that already exist and have data. For custom events, choose average custom value, average custom value over all users, or participation percentage. For economy metrics, choose average net/source/sink currency delta. For funnels, choose per-user or per-instance funnel conversion and preselect the completion step. Newly added events can take time to appear. Define the metric before scheduling; Roblox does not let you change the metric definition after start.

For each metric, document its population, denominator, unit, time window, and desired direction. A per-user metric and a per-participant metric answer different questions; do not compare them as if they used the same denominator.

## Sample feasibility and MDE

Review the minimum detectable effect (MDE) displayed by Roblox, or returned by its Open Cloud calculateMde operation, for the proposed audience, rollout, duration, and variant split. The V43 CLI does not call that API. A small targeted audience or multiple variants can make the detectable effect too large to be useful. The V43 CLI does not calculate or predict MDE.

Roblox in-game experiments have a planned duration between 14 and 60 days. Let the experiment run for its full duration unless critical early harm or a data-integrity issue requires operator review. In the first 24 hours (or until first daily results), Roblox checks Playtime, ARPU, and payer conversion every five minutes; critically harmful thresholds are -10% for Playtime and -20% for ARPU and payer conversion. The platform waits for at least 10,000 players across treatment and control and requires the full one-sided confidence interval to be beyond the threshold before flagging critical harm. Treat these as early-stop signals only, not success metrics. Do not stop early because a favorable metric is temporarily significant.

## Guardrails and interactions

Declare at least one guardrail in the experiment plan before scheduling. Each guardrail has a stable metric ID, a platform/custom metric reference, and the direction that represents harm (increase or decrease). Every treatment result must include exactly the declared guardrails; missing, duplicate, or unexpected guardrails invalidate the review. The direction comes from the predeclared plan, never from the result export. Review any simultaneously running experiments for interactions. Avoid changing unrelated gameplay, config conditions, or analytics definitions while the experiment is running.
