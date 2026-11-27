---
name: roblox-live-performance-rollout-monitoring-v34
description: Plan privacy-safe pre/post-release performance monitoring and staged rollout decisions using aggregate client/server health evidence.
---

# Roblox Live Performance and Rollout Monitoring

## Purpose

Detect performance regressions after a release while distinguishing client experience from server health. A good Studio benchmark does not guarantee that every live device, place, or server cohort behaves identically.

## Pre-release baseline

Record the build identifier, place scope, device distribution, scenario, player-count conditions, client metrics, server metrics, and known limitations. Use V34 repeated-run captures for controlled benchmarks and V29 device budgets for explicit project limits.

## Post-release monitoring

Use Roblox's supported aggregate Performance Dashboard and authorized operational telemetry:
- Client frame rate/frame time, memory, join/crash patterns, and device cohorts.
- Server CPU time, heartbeat/frame rate, memory by age, crash/out-of-memory signals, and process groups.
- Compare equivalent time windows and places, and annotate rollout timing.
- Account for changes in player count, geography, device mix, and seasonality before attributing a shift to a code change.

The Performance Dashboard charts are activity-dependent. Current Creator Hub documentation notes that client/server charts require at least 100 daily active users; when the data is unavailable, record it as unavailable rather than estimating it.

## Rollout decision process

1. Establish a pre-release reference window and documented thresholds.
2. Release to a controlled cohort when the platform's release controls support it.
3. Compare client and server symptoms separately against the reference window.
4. Investigate changes that exceed a pre-agreed threshold or affect a critical device/place cohort.
5. Pause or roll back only through the team's approved release procedure and human authorization.
6. Record the decision, evidence references, mitigations, and follow-up owner in the approved project system.

## Privacy and authority

Use aggregate health signals. Do not create individual-player performance profiles, infer player identity from network data, or collect chat/voice content. V34 is an offline evidence validator; it does not access Creator Dashboard, read live player data, change rollout settings, or execute rollback operations.
