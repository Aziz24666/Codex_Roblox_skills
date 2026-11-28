---
name: roblox-quest-graph-and-objective-architecture
description: Design maintainable Roblox quest and objective graphs with explicit states, prerequisites, branching completion paths, and testable progression contracts.
---

# Roblox quest graph and objective architecture

Define quest lifecycle states explicitly and keep authoritative progress on the server. The client renders objectives and submits intent; it never decides completion or awards rewards.

Give every quest and objective a stable authored ID. Never use display text, array position, Instance names, or UI order as persistent identity. Separate authored definitions from player progress so copy edits do not invalidate saved state.

Represent a quest as a directed graph with one start node and objective, branch, and completion nodes. An objective has one outgoing edge; a branch has two to four alternatives; a completion node has none. Every node must be reachable from start and have a path to completion. Reject missing references, duplicate IDs, and cycles. Model repeats as a new lifecycle activation, not a graph loop.

Validate quest prerequisites as a separate directed graph. Distinguish “prerequisite completed” from “currently active.” Reject missing prerequisites and cycles.

Treat progress as a server-authorized transition. Validate player context, objective type, target identity, interaction constraints, and current state on the server. Make duplicate events harmless and use V40 idempotent reward guidance. Never trust client-reported counts or completion flags. Prefer event-driven updates over per-frame polling.

Test initial availability, prerequisite locking, every branch, completion, duplicate progress events, reconnect/resume, and content-version changes. Confirm no objective becomes impossible because an actor, region, or event is unavailable.

The V45 CLI validates declared metadata only. It does not inspect Luau, prove server authority, verify live events, migrate profiles, balance rewards, or run Studio. Review the implementation and test in a private experience.
