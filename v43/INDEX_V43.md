# Roblox Codex Game Studio Kit — V43

V43.0.0 is the cumulative V1–V43 package with **276 native Codex skills**. Download only the current release.

## V43 — Experimentation and Decision Intelligence

Four new native Codex skills:

1. **Experiment hypothesis and design** — one causal question, primary metric, MDE/sample feasibility, variants, guardrails, and predeclared decision rules.
2. **Native Roblox experiments and Open Cloud lifecycle** — Creator Hub in-game experiments, least-privilege scopes, asynchronous operation polling, immutable running plans, and human-approved completion.
3. **Experiment analytics instrumentation** — server-side AnalyticsService custom events and funnels, privacy/cardinality review, and pre-existing event checks.
4. **Statistical results and decision review** — confidence intervals, sample-ratio mismatch, novelty/early-harm handling, guardrails, and documented human decisions.

## V43 CLI

v43/tools/v43.py provides doctor, validate, audit, compare, and analyze. It validates local experiment plans and reviews an exported/transcribed result summary. It does not make Roblox API calls or compute statistical significance.

## Roblox platform alignment

The design uses native Roblox in-game config experiments and supported AnalyticsService instrumentation. Current platform constraints include 14–60 day experiment durations, one baseline plus up to two treatment variants, up to three custom metrics per in-game experiment, up to 100 custom event names per experience, and asynchronous Open Cloud experiment operations.

## Important boundaries

V43 is an offline planning/review tool. It does not assign players, create or start experiments, retrieve results, calculate MDE or confidence intervals, determine a winning variant, publish a config, or change a live experience. Production experiment operations require authorized credentials, staged review, human approval, and independent readback.

V1–V42 capabilities remain included.
