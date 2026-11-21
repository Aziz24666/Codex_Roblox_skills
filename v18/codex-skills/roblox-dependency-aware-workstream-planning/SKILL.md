---
name: roblox-dependency-aware-workstream-planning
description: Convert a Roblox feature into an acyclic implementation graph with clear dependencies, exclusive ownership, integration points, and parallel-safe workstreams.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Dependency-aware workstream planning

## Operating procedure
1. Create workstreams from deliverables and dependency boundaries, not from arbitrary file or role counts. The graph must be directed and acyclic, with explicit prerequisite IDs and a topological execution order.
2. Assign one owner and a bounded file/path scope to each workstream. Do not permit concurrent edits to shared files unless a named integration owner coordinates sequential merges.
3. Identify shared contracts before delegation. A consumer cannot begin against an invented interface; use a reviewed contract stub with defined semantics and owner.
4. Parallelize independent research, audits, content inventories, and isolated components. Keep tightly coupled edits, sequential migrations, integration, and final verification under one coordinating agent.
5. For each workstream define inputs, outputs, acceptance criteria, dependencies, expected evidence, risk level, and handoff recipient. Re-plan when a dependency fails or new impact is discovered.
6. Validate the graph using `v18/tools/v18.py validate-task`. Reject duplicate IDs, missing dependencies, dependency cycles, and overlapping exclusive path ownership.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
