---
name: roblox-performance-soak-and-memory-trend-v34
description: Design long-duration Roblox server/client soak tests and distinguish sustained memory or CPU growth signals from load changes and noisy samples.
---

# Roblox Performance Soak and Memory Trend Testing

## Purpose

Find performance degradation that only appears after a server has been running for a while. V29 establishes profiling and device budgets; V34 adds structured time-series evidence and repeatable long-session trend review.

## Test design

1. Define the scenario, build, target (server/client), device profile, network profile, player-count target, warm-up period, measured duration, and sample interval.
2. Choose a representative workload and keep it stable. Record connected-client counts at every sample.
3. Collect at least five time-ordered samples over a meaningful duration. Prefer long enough runs to include several round/respawn/asset-streaming cycles.
4. Capture relevant metrics from the appropriate source: server/client Developer Console, MicroProfiler, Script Profiler, Performance Dashboard, or an explicitly documented harness.
5. Track server memory, Lua heap, instance count, script/server CPU, heartbeat, client frame time, client memory, join time, and replication only when actually measured.
6. Compare trends against the server's age and workload. A rising value under a changing player count is not evidence of a leak.
7. Repeat the same run after a focused fix and retain the same environment and measurement method.

## Interpreting trends

Use the V34 validate-capture and analyze-soak commands. The analyzer calculates a simple least-squares trend, per-hour slope, start-to-end change, and R-squared for supported resource metrics. It suppresses a growth signal when the connected-client count varies beyond the configured tolerance or the trend fit is too weak.

A positive memory trend is a growth signal requiring investigation, not proof of a memory leak. Inspect LuaHeap, InstanceCount, PlaceScriptMemory, and event-connection/object lifetimes. Review server-age cohorts and repeat the run before concluding.

## Guardrails

- Never fabricate samples or interpolate missing captures to manufacture complete coverage.
- Do not compare a busy server to an idle server as if workload were controlled.
- Do not put player IDs, usernames, raw chat, voice data, credentials, private server identifiers, or arbitrary logs into captures.
- Keep detailed profiler exports in an authorized project location; reports include only opaque evidence references.
- Do not run soak tests against production player data or production DataStores without an approved isolated plan.
