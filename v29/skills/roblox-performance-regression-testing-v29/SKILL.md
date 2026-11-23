---
name: roblox-performance-regression-testing-v29
description: Define repeatable Roblox performance budgets and compare externally captured baseline and candidate measurements across device classes.
---

# Performance Regression Testing

## Workflow

1. Define budgets per supported device tier and the gameplay scenarios they cover.
2. Capture a baseline and candidate from different builds under equivalent conditions.
3. Include device profile, build identifier, scene, player count, measurement source, and profiler interval in every capture.
4. Compare frame-time percentiles, memory, load time, script CPU, and replication only where the same metric is present in both captures.
5. Investigate candidate values above budgets or regressions beyond the agreed noise threshold.
6. Repeat noisy captures and examine variance before classifying a regression.
7. Run functional, multiplayer, server-authority, persistence, and device tests after optimization.
8. Keep evidence with source revision and mark blocked or unmeasured dimensions honestly.

## Reporting

Distinguish improvement, regression, budget violation, missing metric, and unavailable evidence. A capture file is developer-supplied and not independently authenticated by the comparison tool.

## Safety

Use isolated test places and synthetic data. Do not turn a performance task into a production publishing or player-data change. Keep all earlier no-gambling and fair-monetization requirements.
