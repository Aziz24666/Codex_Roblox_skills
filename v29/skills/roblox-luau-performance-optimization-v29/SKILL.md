---
name: roblox-luau-performance-optimization-v29
description: Review Luau hot paths and propose focused, correctness-preserving Roblox performance improvements using measured profiling evidence.
---

# Luau Performance Optimization

## Workflow

1. Require a reproducible symptom and profiler evidence before calling a code path a bottleneck.
2. Inspect the full call path, execution frequency, data size, client/server boundary, and lifetime of created objects.
3. Review tight polling, redundant work, repeated hierarchy traversal, expensive per-frame callbacks, repeated allocation/cloning, and unnecessary remote or replicated updates.
4. Estimate the complexity and correctness risks of possible changes before implementation.
5. Prefer the smallest targeted change; preserve authoritative server decisions, deterministic behavior where required, and clear ownership of state.
6. Define a before/after test with equivalent scene, device, build settings, and player count.
7. Re-profile and run relevant functional, multiplayer, and persistence regressions.
8. Reject an optimization that improves a microbenchmark but harms responsiveness, correctness, maintainability, or real player experience.

## Output

For every recommendation state: measured evidence, suspected cause, proposed change, risks, expected metric, validation method, and rollback approach. Clearly separate measured facts from hypotheses.

## Do not

Do not blindly replace event-driven logic with polling, introduce pooling without lifecycle cleanup, cache mutable state without invalidation, reduce replication at the cost of correctness, or weaken server validation to save CPU. Do not mass-rewrite unrelated files.
