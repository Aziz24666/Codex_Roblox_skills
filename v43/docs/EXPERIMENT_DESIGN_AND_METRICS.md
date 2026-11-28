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

Choose one primary goal metric. Useful engagement metrics include day-1 retention, day-7 retention, playtime per user, and average session time. Select a small number of learning metrics that explain why a result moved. Up to three custom metrics can be added to an in-game experiment.

Custom metrics must be based on AnalyticsService custom, economy, or funnel events that already exist and have data. Newly added events can take time to appear. Define the event and metric before the experiment starts; Roblox does not let you change the metric definition after start.

For each metric, document its population, denominator, unit, time window, and desired direction. A per-user metric and a per-participant metric answer different questions; do not compare them as if they used the same denominator.

## Sample feasibility and MDE

Review the minimum detectable effect displayed by Roblox for the proposed audience, rollout, duration, and variant split. A small targeted audience or multiple variants can make the detectable effect too large to be useful. The V43 CLI does not calculate or predict MDE.

Roblox in-game experiments have a planned duration between 14 and 60 days. Let the experiment run for its full duration unless critical early harm or a data-integrity issue requires operator review. Do not stop early because a favorable metric is temporarily significant.

## Guardrails and interactions

Select guardrails that represent meaningful unwanted outcomes, such as a significant decrease in playtime or task completion. Review any simultaneously running experiments for interactions. Avoid changing unrelated gameplay, config conditions, or analytics definitions while the experiment is running.
