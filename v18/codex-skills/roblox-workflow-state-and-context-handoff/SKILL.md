---
name: roblox-workflow-state-and-context-handoff
description: Persist concise project and task state across Codex sessions using validated artifacts, phase transitions, and explicit specialist handoffs.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Workflow state and context handoff

## Operating procedure
1. Use versioned files under `.codex/workflows/` for durable project/task artifacts; do not rely on hidden memory or a long conversation as the sole source of truth.
2. Keep project profile, task contract, design/interface contracts, workstream graph, decision records, verification evidence, and completion report separate so each can be updated and reviewed independently.
3. Advance state only through valid transitions: DRAFT → DISCOVERED → SPECIFIED → DESIGNED → IMPLEMENTING → INTEGRATING → VERIFYING → REVIEWED → DONE. Use BLOCKED when a required dependency or approval is unavailable.
4. At each handoff summarize current phase, verified facts, assumptions, decisions, files changed, active blockers, pending approvals, checks run, and next owner. Include paths to artifacts rather than copying entire documents into context.
5. Keep artifacts concise, deterministic, and free of credentials or unnecessary personal data. Preserve history through explicit dated decision/evidence records rather than silently overwriting important decisions.
6. On resume, verify artifact versions and repository state before trusting saved state. A task marked DONE must have all required acceptance criteria and evidence validated.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
