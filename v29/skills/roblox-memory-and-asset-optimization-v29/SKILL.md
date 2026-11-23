---
name: roblox-memory-and-asset-optimization-v29
description: Review Roblox memory growth, instance lifetimes, asset loading, streaming, and content budgets without relying on guesses.
---

# Roblox Memory and Asset Optimization

## Workflow

1. Capture a memory baseline and record device, scene, player count, session duration, and asset/loading conditions.
2. Inspect long-lived tables, retained Instances, event connections, closures, caches, cloned models, temporary effects, and cleanup paths.
3. Confirm ownership and release conditions for connections, Instances, tasks, and cached references. Look for growth over repeated spawn/respawn, teleport, streaming, and UI open/close cycles.
4. Audit asset dimensions, texture/audio/mesh payload, redundant variants, loading priorities, and streaming configuration in the context of actual use.
5. Distinguish legitimate memory residency from a leak; compare repeated equivalent captures over time.
6. Propose focused fixes and verify that cleanup does not break replication, re-entry, animations, or gameplay state.
7. Re-run sustained-session tests and compare memory and load behavior on target devices.

## Output

Provide a resource-lifetime map, evidence, likely root cause, proposed action, expected trade-offs, and a repeatable validation scenario.

## Boundaries

Do not delete assets or instances based only on static guesses. Do not claim memory use or asset impact without measurements. Treat content optimization as a balance between fidelity, memory, download size, and loading behavior.
