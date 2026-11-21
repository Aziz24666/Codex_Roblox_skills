---
name: roblox-risk-and-approval-gating
description: Classify Roblox development actions by risk and reversibility, enforcing approval before external, destructive, costly, or production-impacting operations.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Risk and approval gating

## Operating procedure
1. Classify actions before execution: read-only inspection; reversible workspace edits; local builds/tests; external network/authenticated actions; destructive changes; production or public side effects.
2. Proceed with ordinary reversible source edits and disposable local tests inside the authorized workspace. Use least privilege and keep a reviewable diff.
3. Require explicit user approval before publishing/unpublishing, deployment, uploading/replacing public assets, modifying live experience settings or permissions, changing production data, migrating/resetting player data, creating/deleting places, spending Robux or other money, or pushing externally when not already specifically requested.
4. Never ask for, print, commit, or store credentials, cookies, API keys, passwords, tokens, or `.ROBLOSECURITY`. Use configured secret stores without exposing values; do not infer permission from the presence of credentials.
5. For automation and CI, use read-only pull-request permissions by default. Never execute untrusted pull-request code in privileged workflows. Keep package build, test, publish, and deployment gates separate.
6. When approval is required, stop before the side effect and state the exact action, target, consequence, rollback options, and evidence available. Do not imply that a blocked action was completed.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
