# V43.0.0 — Experimentation and Decision Intelligence

## Added
- Four native Codex skills for experiment hypothesis/design, Roblox native Experiments/Open Cloud lifecycle, AnalyticsService instrumentation, and statistical result/decision review.
- Offline experiment plan validator and audit tool.
- Baseline/candidate experiment plan comparison.
- Offline results reviewer for confidence intervals, SRM, critical-harm flags, planned-duration completion, primary-metric direction, and harmful guardrails.
- Experiment plan and result-review JSON Schemas, examples, documentation, regression tests, cumulative patcher/auditor, and Windows/Linux CI.

## Cumulative package
V1–V43, 276 native Codex skills. Download only the V43 package.

## Limitations
The CLI validates local metadata and reviews supplied result summaries only. It does not calculate MDE, sample-size power, confidence intervals, statistical significance, or SRM. It does not call Roblox Open Cloud, poll operations, assign players, start or complete experiments, select winners, or publish configs. All live experiment writes and final decisions require authorized human review.
