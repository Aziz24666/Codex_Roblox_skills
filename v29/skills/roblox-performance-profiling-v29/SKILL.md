---
name: roblox-performance-profiling-v29
description: Plan and execute evidence-based Roblox performance profiling with MicroProfiler, Script Profiler, Developer Console, and representative hardware.
---

# Roblox Performance Profiling

## Objective

Find the measured bottleneck before recommending an optimization. Establish a reproducible baseline for the actual player experience and target devices.

## Workflow

1. Define the gameplay scenario, scene, build revision, player count, device tier, and symptom.
2. Capture repeated baseline runs with Roblox Studio MicroProfiler and Script Profiler; inspect the Developer Console for memory, network, and runtime signals.
3. Separate frame-time, script CPU, memory, loading, and replication hypotheses. Do not infer one metric from another.
4. Identify the most expensive relevant frames, scripts, functions, or subsystem before changing code.
5. Record exact evidence, capture interval, test conditions, and measurement variance.
6. Prioritize issues by player impact, frequency, severity, confidence, and implementation risk.
7. Re-run the same scenario after each focused change and preserve comparison evidence.
8. Validate on low-end mobile, high-end mobile, and desktop hardware where those devices are supported.

## Required output

Produce a prioritized profiling plan or evidence-backed findings table. Mark unknown, planned, blocked, and measured items distinctly. Static V29 audit hints must remain labelled as unverified candidates until profiler evidence confirms them.

## Boundaries

Never invent FPS, frame time, memory, CPU, load-time, or replication numbers. A CI run does not imply a Studio profiler capture. Do not optimize production code without a clear baseline and review.
