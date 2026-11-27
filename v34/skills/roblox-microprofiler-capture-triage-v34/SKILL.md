---
name: roblox-microprofiler-capture-triage-v34
description: Interpret Roblox MicroProfiler, Script Profiler, Developer Console, and performance dashboard evidence while preserving client/server boundaries and capture provenance.
---

# Roblox Profiler Capture Triage

## Objective

Turn measured evidence into a narrow, testable bottleneck hypothesis. Do not optimize from a static scan or from an unexplained dashboard average.

## Select the correct diagnostic surface

- MicroProfiler: inspect frame timelines, spikes, engine task groups, and saved frame dumps on the affected client or server.
- Script Profiler: compare CPU cost by script/function and record whether the capture was client-side or server-side. Recording frequency and duration affect profiling overhead.
- Developer Console: inspect runtime errors, server heartbeat, LuaHeap, InstanceCount, PlaceScriptMemory, memory tags, and network statistics.
- Performance Stats: collect the relevant client frame, memory, CPU/GPU, network, and ping context.
- Performance Dashboard: use aggregate client/server trends before and after a release. It requires sufficient experience activity for its charts; don't invent unavailable metrics.

## Evidence workflow

1. Reproduce a defined scenario on the same build and environment.
2. Capture the affected side (client, server, or both); never assume a client profiler represents server work.
3. Note time window, profiling mode, profiler sampling frequency, target device, player count, network profile, and build revision.
4. Use saved MicroProfiler frame dumps and Script Profiler summaries to locate the actual costly work.
5. Correlate profiler evidence with time-series captures; avoid joining unrelated windows.
6. Form one hypothesis, change one subsystem, and repeat the same capture.
7. Use V34 repeated-run comparisons to account for run-to-run variation.

## Capture interpretation cautions

- Script Profiler only records CPU-consuming function calls; sleeping/waiting work is not represented as CPU cost.
- High-frequency profiler sampling can add overhead; keep baseline and candidate settings identical.
- A single frame spike is not automatically a persistent performance issue.
- A memory chart moving upward is not automatically a leak; inspect its category, server age, player count, and instance lifecycle.
- Performance Dashboard compute efficiency is an aggregate metric, not a direct measure of player experience.

## Required output

State the measured symptom, capture source, side, environment, time window, affected frame/script/subsystem, confidence, reproduction steps, and follow-up capture required. Mark unsupported or missing evidence explicitly. Do not claim V34 tools import proprietary profiler dump formats; the CLI validates structured numeric summaries and opaque evidence references only.
