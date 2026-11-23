# V29.0.0 — Performance Engineering and Optimization

V29 extends the cumulative V1-V28 Roblox Codex Game Studio Kit with profiling-first performance workflows, local Luau performance review hints, device-specific budgets, and comparison of externally captured measurements.

## New capabilities

- Four native Codex skills:
  - roblox-performance-profiling-v29
  - roblox-luau-performance-optimization-v29
  - roblox-memory-and-asset-optimization-v29
  - roblox-performance-regression-testing-v29
- v29/tools/v29.py:
  - doctor: inventory local source and optional developer tools.
  - audit: bounded, read-only heuristic scan for possible performance-sensitive code patterns.
  - budget: validate low-end mobile, high-end mobile, and desktop performance budgets.
  - compare: compare supplied baseline/candidate JSON captures and identify deltas, budget violations, and missing metrics.
  - report: combine existing static audit and capture-comparison reports.
- Add schemas, example budgets, regression tests, package patcher/auditor, and documentation.

## Important limitations and safeguards

- Static findings are heuristic review leads, not proven defects or measured bottlenecks.
- No FPS, memory, CPU, frame-time, replication, or load-time data is inferred from Luau source.
- Captures must be collected independently with Roblox Studio profiling tools or a documented test harness.
- The toolkit does not execute game code, launch Studio, connect to Roblox, alter scripts, optimize projects automatically, or perform production operations.
- Preserve V1-V28 functionality, server authority, DataStore safety, fair monetization, and all no-gambling requirements.

## Validation

- V29 tests cover bounded static findings, source inventory, measurement and budget schema rules, profile/build matching, regression thresholds, budget violations, path containment, symlink handling, report generation, and idempotent cumulative package integration.
- The V29 workflow reconstructs the pinned V17 baseline, applies all cumulative overlays V18-V29, runs inherited regression suites, checks the 220-skill package, validates archive equivalence, and verifies SHA-256 checksums.
- Studio profiling on physical devices remains a manual evidence-gathering task; GitHub Actions does not claim to run it.
