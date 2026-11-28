---
name: roblox-experiment-results-and-decision-review
description: Review Roblox experiment confidence intervals, MDE, sample-ratio mismatch, novelty effects, guardrails, and human-approved rollout decisions.
---

# Roblox experiment results and decision review

## Verify the experiment is decision-ready
- Confirm the experiment completed its planned duration; Roblox recommends running experiments for their full planned duration.
- Review the achieved enrolled sample and MDE, not just the percentage lift.
- Check Roblox's Sample Ratio Mismatch (SRM) signal. SRM means enrollment did not follow expected proportions and can invalidate results. Do not make a launch decision from an SRM-affected experiment.
- Treat critical early-harm alerts as an operational reason to review and potentially stop. Early-harm observations are not evidence for a winning launch decision.

## Read statistical evidence correctly
- Require each treatment result to report exactly the guardrails predeclared in the experiment plan; missing, duplicate, or unexpected guardrails invalidate the review.
- Derive harmful direction from the predeclared plan, never from a result export.
- Verify every reported point estimate is inside its confidence interval; inconsistent summaries must be rejected.
- Review the confidence interval for each goal and learning metric. Roblox describes a change as statistically significant when the interval for percent change does not overlap zero.
- A large-looking point estimate with an interval crossing zero is not a statistically significant win.
- A non-significant result is inconclusive; it does not prove the two variants are identical.
- Do not repeatedly inspect and stop at the first favorable result. Novelty effects and random variation can make early results unstable.
- Treat a statistically significant guardrail decline as a real trade-off requiring review, even when the primary metric improves.

## Make a documented decision
Choose one:
- Keep control.
- Roll out a treatment after statistical and product review.
- Run a new experiment with a new hypothesis.
- Gather more evidence where the platform and experiment lifecycle allow it.

Record the selected outcome, confidence interval, MDE/sample context, SRM status, guardrail movements, reviewer, evidence, and date. Review player feedback and product context alongside the quantitative result.

## Non-negotiable safeguards
- Never select a winner from an incomplete run or SRM-affected data.
- Never treat early-harm monitoring as a way to declare success.
- Never claim statistical significance when the interval includes zero.
- Never roll out solely because one metric rose while a guardrail fell significantly.
- Human approval is required for a winning-variant completion and permanent config change.
