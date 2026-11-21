---
name: roblox-impact-aware-skill-routing
description: Select a minimal, non-duplicative set of Roblox Codex skills based on task intent, affected systems, trust boundaries, and change impact.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Impact-aware skill routing

## Operating procedure
1. Use the V18 router (`python v18/tools/v18.py route --root . --task "..."`) as a recommendation, not as an unquestionable authority. Read the matching skill descriptions and current index before loading detailed specialists.
2. Always appoint one end-to-end owner for cross-system work. Add project intelligence for existing repositories, and add acceptance, security, persistence, performance, UI, asset, character, Studio, economy, or release specialists only when the task touches those concerns.
3. Route by affected boundary, not by keyword alone. A shop may touch catalog schema, server ownership, persistence, remote contracts, UI, analytics, and monetization; select each only when the implementation actually crosses that boundary.
4. Prefer the smallest useful set. Avoid duplicate reviewers, title-based selection, loading all 175 skills, and multiple specialists owning the same interface or files.
5. Record why each skill is selected, what it owns, what it does not own, inputs required, outputs expected, and downstream recipients. Re-route when scope or impact changes.
6. Identify missing capability honestly. Do not invent a specialist or claim that a skill grants a tool, Roblox permission, Studio connection, or external access.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
