---
name: roblox-live-operations-and-safe-rollouts
description: Plan controlled Roblox releases with staged promotion, feature flags, compatibility windows, kill switches, and safe rollback.
---

# Roblox Live Operations and Safe Rollouts

## Mission
Make releases reversible where possible, observable during promotion, and safe for player data when code and stored schemas evolve.

## Procedure
1. Define the release identity, affected experience/places, owner, change risk, dependencies, and explicit non-goals.
2. Separate development, staging, canary, and production. Keep non-production data stores isolated from production.
3. Define promotion gates and an observation window for each stage. Use measurable error, latency, save, transaction, and remote-rejection signals.
4. Roll out risky behavior behind server-enforced feature flags with an owner, default, scope, and expiry/review date.
5. Provide a kill switch that stops the affected behavior without corrupting in-flight or already-persisted player data.
6. Preserve read/write compatibility through the rollout window. A source-code revert cannot undo a destructive player-data migration.
7. Define a rollback or forward-recovery plan before promotion. Never overwrite newer player writes.
8. Require owner approval for publishing, live configuration changes, and production data actions. Record exact approvals and execution evidence.
9. After promotion, verify actual service health and keep watch for delayed save, transaction, matchmaking, or client compatibility regressions.

## Stop conditions
Stop promotion on unexplained increases in server errors, player data save failures, duplicate/incorrect grants, remote abuse indicators, severe latency, or unexpected client failures. Set thresholds from the project's measured baseline rather than copying arbitrary universal numbers.

## Handoff
Return the stage map, promotion gates, feature-flag inventory, kill-switch owner/procedure, data compatibility window, rollback/forward-recovery plan, monitoring owner, approvals, and unrun production checks.

## V18 shared workflow and handoff contract

- Follow root AGENTS.md and v18/docs/SKILL_INTEROPERABILITY.md; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned. Do not silently redefine shared APIs, schemas, remotes, data ownership, or another specialist's files.
- Return a structured handoff: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence, risks, blockers, and next owner.
- Update task/evidence artifacts. Use PASS only for checks that actually ran; keep unavailable Studio/device/live-service checks NOT_RUN or BLOCKED.
- Re-route when scope changes. Skills do not grant tools, permissions, MCP connections, or runtime capabilities.

## V19 verification and evaluation contract

- Select verification from changed paths, impacted systems, trust boundaries, and failure impact; do not run or report unrelated checks as proof.
- Separate formatting, static analysis, unit, contract, integration, Studio, multi-client, device, performance, persistence, economy, and live-service checks.
- A plan is not an execution result. Preserve NOT_RUN and BLOCKED states for checks that did not run.
- A PASS requires the exact command or scenario, named environment, tool/runtime version, build identity, expected behavior, observed behavior, and a non-empty inspectable evidence artifact.
- Keep failures visible. Do not weaken acceptance criteria, delete negative benchmark cases, or convert a failed check into a pass.
- Deterministic routing benchmarks measure router behavior only; they do not prove model reasoning quality, skill compliance, or game correctness.

## V20 production reliability contract

- Treat the server as authority for consequential state and enforce an explicit remote allowlist, server validation, ownership/context checks, bounded payloads, and rate limits.
- Make persistence writes retry-safe, migrations deterministic/idempotent, and recovery decisions explicit; isolate tests from production data.
- Fulfill fixed-price products from server-verified receipts with idempotent exact grants; preserve the V18 no-gambling policy.
- Use staged rollouts, feature flags, a kill switch, schema compatibility, monitoring, and a data-safe rollback/forward-recovery plan.
- Track actionable service-health metrics and alerts; protect dashboards and redact personal data/secrets from logs.
- Static contracts and CI do not prove live Roblox services or production behavior; record environment-specific checks with V19 evidence rules.
