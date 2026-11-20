---
name: roblox-autonomous-implementation-loop
description: Execute bounded Roblox implementation slices with automatic inspect-plan-edit-check-repair cycles while preserving scope, safety, and user approval boundaries.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Autonomous implementation loop

## Operating procedure
1. Use the approved work item and project profile as the execution contract. Work on one complete vertical slice at a time; do not expand scope silently.
2. For each slice: inspect target files and callers, confirm current official API/tool behavior, state the intended diff, implement the smallest coherent change, run focused checks, inspect the diff, and update task evidence.
3. Repair failures in bounded iterations. Reproduce the failure, isolate its cause, change one coherent area, rerun the failing test and relevant regression tests, and stop when blocked or when the agreed iteration budget is reached.
4. Use available Codex tools, terminal, MCP, and subagents only when actually connected and authorized. Do not claim automation happened merely because a workflow or MCP template exists.
5. Never install dependencies, modify global configuration, access secrets, run destructive commands, change permissions, publish, deploy, upload public assets, alter production data, or spend currency without the required user approval.
6. At each checkpoint record commit/build identity when available, changed files, commands actually executed, pass/fail output, limitations, and the next step. Keep generated files deterministic and regenerate them from their source.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
