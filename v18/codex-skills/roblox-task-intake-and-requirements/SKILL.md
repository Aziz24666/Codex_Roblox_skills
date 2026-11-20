---
name: roblox-task-intake-and-requirements
description: Turn Roblox feature requests and bugs into scoped, testable work items with explicit goals, non-goals, assumptions, and acceptance criteria.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Task intake and requirements

## Operating procedure
1. Capture the requested outcome, target audience, player journey, constraints, existing behavior, non-goals, and known dependencies. Separate facts supplied by the user from assumptions that need validation.
2. Ask only for information that blocks safe, correct execution. For non-blocking unknowns, record a reversible assumption and mark it for confirmation at the appropriate gate.
3. Write acceptance criteria as observable behaviors with clear setup, action, expected result, and failure conditions. Include server/client, persistence, UI, accessibility, performance, and platform coverage only where relevant.
4. Identify affected systems and data ownership. Distinguish a feature requirement from an implementation preference; preserve the requested outcome while proposing simpler architecture when appropriate.
5. Create or update the V18 work item using the task schema. Give every criterion a stable ID, verification method, owning workstream, and status. Keep scope changes in the same task record.
6. Before handoff, list unresolved decisions, confidence, risks, dependencies, and which specialist must own each open item. Do not mark criteria PASS before evidence exists.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
