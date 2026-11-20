---
name: roblox-agent-delegation-and-coordination
description: Use Codex subagents for independent Roblox research, audits, and isolated implementation work with explicit ownership and integration contracts.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Agent delegation and coordination

## Operating procedure
1. Use subagents only when the runtime exposes them and when work can be decomposed into bounded, independent assignments. If unavailable, perform the same workflow sequentially and report that delegation was unavailable.
2. Give each agent a single question or deliverable, exact input files, permitted output paths, expected format, acceptance criteria, and a prohibition on editing shared integration files unless assigned.
3. Prefer parallel read-only research, separate subsystem reviews, and isolated test writing. Do not parallelize coupled edits, shared schemas, migrations, overlapping file ownership, or dependent steps.
4. Require each agent to return evidence and changed-file ownership, not an unverified summary. The coordinator reviews every output, resolves contradictions, integrates changes, and runs the combined test suite.
5. Limit concurrency to a small measured number; more agents increase cost and coordination overhead. Begin with a small number of agents and expand only when parallelism improves end-to-end quality.
6. Never grant a subagent more permissions than the parent task requires. Approval boundaries and data-handling rules apply equally to delegated work.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
