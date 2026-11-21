---
name: roblox-evidence-first-completion
description: Produce truthful, traceable completion reports that connect requirements, code changes, verification evidence, unresolved risks, and release readiness.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Evidence-first completion

## Operating procedure
1. Map each acceptance criterion to an implementation owner and a verification method before work begins. Keep criterion IDs stable across scope changes.
2. For every check record status, exact command or scenario, environment, tool/Studio version, commit/build identity, expected result, actual result, logs/artifacts, timestamp, and limitations.
3. Use PASS only when the check ran and its assertion succeeded. Use FAIL for observed failure, BLOCKED for an unavailable prerequisite or approval, NOT_RUN for work not executed, and NOT_APPLICABLE with a reason.
4. Distinguish skill invocation, static inspection, type/lint checks, build success, automated tests, Studio playtests, multi-client behavior, device testing, staging, and production evidence.
5. Before completion, compare the final diff against the task scope, inspect generated files and secrets, confirm all cross-system contracts, review unresolved TODOs, and verify release manifests if packaging.
6. Write a concise report with completed outcomes, changed paths, tests and evidence, remaining risks, checks not run, user decisions required, and the exact next step. Never claim bug-free, secure, production-ready, or runtime-verified without evidence.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
