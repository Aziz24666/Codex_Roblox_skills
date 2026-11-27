# Repeated Benchmarks and Live Rollout Review

## Repeated benchmark cohorts

Do not treat one baseline and one candidate capture as conclusive. The V34 suite requires at least three runs per build and checks that the same scenario, target, device profile, measurement source, network profile, player-count target, duration, and sample interval were used.

V34 aggregates each metric within each capture, then uses the median across captures. It reports missing metrics rather than inventing values. The manifest contains only project-relative capture paths and fixed metadata.

## Regression direction

- Higher is generally adverse: frame time, memory, LuaHeap, instance count, CPU time, and join time.
- Lower is adverse: server heartbeat.
- Replication throughput is contextual and does not receive a universal regression direction.

A configured percentage threshold reduces noise but does not prove statistical significance. Review individual captures and rerun if the cohort is noisy.

## Live monitoring

Use authorized aggregate Creator Dashboard metrics before and after a release. Separate client and server metrics, compare equivalent windows/places/device cohorts, and annotate deployment timing. Do not infer causality from a single chart movement.

Current Creator Hub Performance Dashboard charts have activity requirements; its client/server charts are documented as requiring at least 100 daily active users. Record unavailable data as unavailable.

## Release actions

Only a human release owner should approve a pause, staged rollout, or rollback under the team's release process. V34 can compare supplied evidence; it cannot change release settings, access live Roblox telemetry, or trigger rollback.
