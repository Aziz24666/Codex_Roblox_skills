---
name: roblox-end-to-end-development-orchestrator
description: Coordinate the complete Roblox task lifecycle from intake and project discovery through implementation, integration, validation, and evidence-backed delivery.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.


## Mandatory economy and monetization policy

For any task involving a shop, catalog, currency, purchase, paid access, pass, developer product, subscription, tier unlock, or monetization UX:
1. Read `v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md` before planning or editing.
2. Treat the no-gambling rule as mandatory: do not design or implement paid random rewards, wagers, paid rerolls, chance-based paid upgrades, or any Robux-funded random outcome.
3. Route to all four V18 economy specialists: `roblox-player-friendly-monetization`, `roblox-deterministic-progression-shop`, `roblox-tiered-catalog-progression`, and `roblox-earned-currency-economy`. Add UX, transaction, persistence, and security specialists when affected.
4. Preserve deterministic prices and grants. If tiered catalog progression is requested, every required item in every earlier tier must be owned before the next tier unlocks, and each required item must have a non-Robux route.
5. Re-check current official Roblox documentation and record the URLs/date and the exact claims used. Never claim platform compliance from a static prompt or unrun test alone.

# End-to-end development orchestrator

## Operating procedure
1. Own the complete task lifecycle and keep one authoritative work item. Convert the request into a player-visible or developer-visible outcome, preserve constraints, and select the smallest set of relevant specialists.
2. Run discovery before proposing edits. Read the root AGENTS.md, existing task state, project profile, relevant architecture records, and current source evidence. Use the V18 CLI to inspect and route tasks when available.
3. Create an explicit workstream graph. Keep one integration owner, assign exclusive file ownership, and parallelize only independent work. Do not create subagents merely to appear autonomous; use them when their work can be bounded and independently reviewed.
4. Execute in dependency order: requirements, contracts, implementation slices, integration, validation, review, and handoff. Recompute impact and skill routing when discoveries change scope.
5. Keep normal reversible workspace work moving without needless approval pauses. Stop for external side effects, production data, publishing, public assets, credentials, permissions, costs, destructive changes, or any other approval boundary in AGENTS.md.
6. Require each specialist to return the V18 handoff fields: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence locations, risks, and next owner. Resolve conflicting contracts centrally.
7. Finish only when the work item acceptance criteria are satisfied or explicitly BLOCKED. Summarize changed files, actual test results, remaining risks, runtime checks not run, and any approval needed. Never equate skill selection, plan completion, or a successful build with verified gameplay.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
