# V29 Performance Engineering

## Profile first, change second

Performance work begins by defining the player experience and target hardware. Capture a repeatable baseline before changing code. Use Roblox Studio MicroProfiler to locate frame-time costs, Script Profiler to identify script CPU hotspots, and the Developer Console to inspect runtime and network behavior. Repeat scenarios on representative low-end mobile, high-end mobile, and desktop devices.

Prioritize user-visible symptoms: frame-time spikes, long loading, memory pressure, script work, network replication, and stalls during spawn or scene transitions. Use the profiler to identify the actual expensive subsystem before editing it.

## Optimization workflow

1. Describe the target experience, scene, player count, device profile, and success criteria.
2. Capture a baseline using an unchanged build and stable test scenario.
3. Inspect frame time and script CPU; isolate a specific hotspot instead of rewriting unrelated code.
4. Change one category at a time and preserve gameplay correctness, server authority, and readability.
5. Repeat the same scenario and compare measurements against the baseline and device budgets.
6. Test sustained sessions, reconnects, streaming, respawns, and realistic peak activity.
7. Record source revision, device, scene, player count, profiler evidence, and known limitations.

## Luau and systems review

Review polling loops, per-frame callbacks, repeated hierarchy traversal, repeated allocations/clones, connection lifetimes, redundant calculations, unbounded caches, and unnecessary replication. Event-driven updates, bounded work, caching, pooling, and throttling are possible techniques—not blanket rules. Each can introduce stale state, retained instances, complexity, or latency if applied without a measured need.

Do not optimize from a static scan alone. A pattern is a lead to investigate, not proof of a bottleneck.
