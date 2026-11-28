# Statistical review and decisions

## Decision-readiness gates

Before a launch decision, confirm:
- The experiment completed its full planned duration.
- The eligible audience and sample size are adequate for the MDE.
- Roblox has not flagged Sample Ratio Mismatch (SRM).
- The goal metric and learning metrics have usable confidence intervals.
- Guardrail metrics have been reviewed.
- The content and instrumentation were stable during the experiment.

## Confidence intervals

Roblox describes a metric change as statistically significant when the confidence interval for percent change does not overlap zero. A point estimate alone is not enough. If the interval crosses zero, the result is inconclusive—not proof that the variants are equivalent.

A significant result in the direction opposite the hypothesis is not a win. A positive goal metric alongside a significant harmful guardrail is a trade-off that requires review, not an automatic rollout.

## Sample Ratio Mismatch

SRM means players were not enrolled in variants at the expected proportions. Roblox checks for SRM, more frequently during the first 24 hours and then daily. SRM can invalidate results. Do not choose a winner from an SRM-affected experiment; investigate the assignment/enrollment issue and follow the platform's stop/restart guidance.

## Early harm and novelty

Critical early-harm alerts can justify an operational review and stopping an experiment. They are not evidence for a successful launch decision. Do not stop early because results look favorable: novelty and random variation can make early metrics unstable.

## Human decision record

For each decision, preserve:
- Experiment ID, goal, planned duration, actual duration, exposure, and variants.
- Sample counts and MDE context.
- SRM and critical-harm status.
- Goal and guardrail movements with confidence intervals.
- Decision: keep control, roll out a reviewed treatment, or run a new experiment.
- Reviewer, approval, evidence link, and decision date.

A statistically significant result is not certainty. Combine quantitative evidence with player feedback and the game's intended design.
