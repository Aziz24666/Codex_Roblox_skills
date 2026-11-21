---
name: roblox-player-data-resilience-and-migrations
description: Engineer resilient Roblox player profiles, safe DataStore retries, schema migrations, and recovery without overwriting valid data.
---

# Roblox Player Data Resilience and Migrations

## Mission
Protect player progress across transient failures, concurrent sessions, schema changes, server shutdowns, and recovery operations.

## Procedure
1. Map profile ownership and the full load/active/save/release lifecycle. Inspect existing session-locking and persistence libraries before proposing new infrastructure.
2. Use UpdateAsync-style transforms that are deterministic and safe to re-enter. Keep external side effects outside retryable transform callbacks.
3. Bound retry attempts, use exponential backoff with jitter, respect request budgets, and distinguish transient service failures from invalid data.
4. Treat a failed load as an explicit state. Do not replace unreadable existing data with defaults and then save those defaults over the profile. Use a documented safe-mode or fail-closed policy.
5. Version every stored profile. Implement adjacent migrations that are deterministic, idempotent, shape-validated, and safe to run again after interruption.
6. Test migrations against isolated fixtures, including repeated runs, partial failures, old profile shapes, unknown fields, and restore/forward-recovery scenarios.
7. Define shutdown/reconnect handling and release session ownership predictably. Do not hold a session lock forever or allow two servers to mutate the same profile concurrently.
8. Record backup identity, schema version, observed outcome, and owner approval for any recovery affecting real player data.

## Review checklist
- No infinite retry loops or hidden save failures.
- No silent default-profile overwrite after load failure.
- All migrations have explicit source/target versions and repeat-run behavior.
- Test stores and production stores are separate.
- Recovery preserves newer valid writes and has an owner.
- Save/load failure rates are observable and actionable.

## Handoff
Return the profile lifecycle diagram, schema-version map, retry/failure policy, migration list, fixture results, backup/recovery plan, tests actually run, and production-only checks still NOT_RUN.

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
