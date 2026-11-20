---
name: roblox-cross-system-contract-governance
description: Define and maintain stable interfaces, data schemas, ownership boundaries, lifecycle rules, and compatibility expectations across Roblox systems.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Cross-system contract governance

## Operating procedure
1. Before parallel work or implementation, create one feature contract covering player-visible outcomes, module responsibilities, public APIs, data schemas, remotes/events, ownership, execution context, error behavior, lifecycle, observability, and test seams.
2. For every interface identify producer, consumer, authority, validation boundary, version/compatibility policy, failure response, and owner. Server-owned state must not become client-authoritative through a UI or convenience adapter.
3. Use schema-first contracts for catalog/configuration/persistence where appropriate. Validate identifiers, uniqueness, references, version migration, and deterministic generation.
4. Keep one canonical definition. Generated code, UI descriptors, documentation tables, and test fixtures must derive from that source where practical; do not hand-maintain conflicting copies.
5. When a contract changes, update all consumers, migration behavior, examples, tests, skill handoffs, and documentation in the same integrated change. Use compatibility adapters only when they are intentional and tested.
6. Reject circular module dependencies, duplicate authority, ambiguous event ownership, silent partial failure, and placeholder interfaces that cannot support the final feature.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
