---
name: roblox-continuous-validation-and-repair
description: Choose and run impact-appropriate Roblox static, schema, unit, integration, Studio, multiplayer, device, and release checks with bounded repair loops.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Continuous validation and repair

## Operating procedure
1. Build a verification profile from changed paths, dependency graph, affected contracts, risk level, and project source of truth. Run cheap deterministic checks first, then focused tests, then broader regression and environment-specific tests.
2. Use existing project commands only after inspecting their definitions and trust implications. Never execute arbitrary scripts from an untrusted repository simply because a package file declares them.
3. Validate formatting, lint, strict Luau analysis, configuration/schema contracts, generated artifacts, module boundaries, remote contracts, persistence behavior, builds, unit tests, integration tests, and release artifacts where applicable.
4. Use Roblox Studio MCP or Studio TestService only when an actual compatible Studio session/plugin is connected and its current documented permissions permit the action. Keep test-only automation out of production game scripts.
5. When a check fails, preserve the first failure, classify it, reproduce it, repair the root cause, and rerun the failed check plus impact-selected regressions. Bound retries; do not mask flakes or weaken assertions to force green.
6. Record every check as PASS, FAIL, BLOCKED, NOT_RUN, or NOT_APPLICABLE with environment, tool version, build identity, scenario, output/artifact, and limitations. A static audit is not a playtest.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
