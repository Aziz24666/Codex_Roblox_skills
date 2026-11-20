---
name: roblox-performance-regression-testing
description: Establish Roblox client/server performance baselines, profile representative workloads, and detect regressions without inventing universal budgets.
---

## Mandatory current-source research gate

Before substantive implementation, perform fresh online research using the current official Roblox Creator Hub/API documentation and relevant Roblox platform updates, deprecations, security guidance, or release notes. Check upstream documentation for any external tool or framework involved. Compare viable approaches when an API, architecture, or platform behavior is version-sensitive. Record exact source URLs, access dates, verified claims, alternatives, decisions, and the verification plan in `research/decisions/`. Re-open sources for each new task; previous research is background, not a substitute for current verification. Never invent a citation or claim a source was checked when it was not. If a critical platform or tool claim cannot be verified, mark the affected implementation `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing.

# Roblox Performance Regression Testing

## When to use
Use for frame-time, memory, network, server-step, content-loading, replication, streaming, or scalability changes and before performance-related releases.

## Procedure
1. Define the player-facing performance problem and target device/server tiers.
2. Choose representative workloads: player count, world/content density, NPC count, effects, network activity, streaming state, and duration.
3. Record an unmodified baseline before optimizing. Capture device/Studio/build identity, server/client context, workload, sample duration, metric definitions, and raw output.
4. Select measurements relevant to the hypothesis: frame time, memory, CPU/script time, server simulation, network throughput/latency, load time, or instance counts.
5. Use current official Roblox profiling and performance references; verify exact tool/API behavior rather than assuming names or units.
6. Change one major variable at a time where practical and keep the workload comparable to baseline.
7. Repeat runs to distinguish real regressions from noise. Record median and spread or another justified summary.
8. Compare results to project-defined budgets and the original baseline. Do not invent one global threshold for every device.
9. Add a repeatable regression scenario or measurement script where feasible.
10. Report what was measured, what was not, trade-offs, and remaining bottlenecks.

## Pitfalls and fixes
- Source inspection called profiling: gather runtime measurements before quantitative performance claims.
- Different workloads compared: normalize players, device tier, scene, duration, and build.
- One noisy run: repeat samples and record variability.
- Desktop result generalized to phones: profile representative target tiers separately.

## Output contract
Provide baseline-versus-change measurements with context and methodology. Mark profiling NOT_RUN when the runtime environment was unavailable.
