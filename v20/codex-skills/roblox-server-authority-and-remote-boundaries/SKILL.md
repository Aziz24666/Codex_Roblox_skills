---
name: roblox-server-authority-and-remote-boundaries
description: Design server-authoritative Roblox gameplay and defensive RemoteEvent contracts with validation, ownership checks, and rate limits.
---

# Roblox Server Authority and Remote Boundaries

## Mission
Keep consequential gameplay state under server authority and make every client-to-server operation explicit, bounded, and reviewable.

## Required discovery
Inspect the existing remote inventory, producer/consumer scripts, state ownership, gameplay rules, player lifecycle, rate-limit utilities, tests, and V18 work-item contracts. Do not invent remote names or assume that a client-side check is security enforcement.

## Procedure
1. Classify each state value as server-owned, client presentation, or derived/replicated. Currency, inventory, rewards, purchase status, progression, damage, ownership, and permissions must be computed or confirmed by the server.
2. Inventory every RemoteEvent and RemoteFunction. Give each accepted operation a stable ID, payload schema, direction, owner, allowed context, and explicit side-effect classification.
3. Validate payload type, structure, bounds, string lengths, instance ancestry, ownership, distance/context, cooldown, and current server state. Reject unknown operations and malformed input.
4. Apply per-player and per-operation rate limits with bounded memory and cleanup on PlayerRemoving. Add concurrency protection for operations that must not overlap.
5. Derive prices, grants, rewards, damage, and unlock decisions from server-owned definitions. Never accept a client-supplied result as authoritative.
6. Make every state-changing request idempotent where duplicate delivery is possible. Use stable request/transaction identifiers and server-side records.
7. Keep validation, authorization, mutation, and response paths observable. Return safe error categories without disclosing internal secrets or stack traces.
8. Verify with unit/contract tests and a real multi-client Studio scenario when behavior depends on networking. Record environment and evidence under V19 rules.

## Review checklist
- Unknown or unauthorized operations fail closed.
- Server validates all values that affect shared state.
- Ownership and contextual eligibility are checked on the server.
- Payload size and computational cost are bounded.
- Rate limits and concurrency guards have cleanup paths.
- Duplicate requests cannot duplicate state changes.
- Rejected requests leave state unchanged.
- No client-controlled value bypasses server policy.

## Non-goals
Do not build client-side anti-cheat as the security boundary. Do not rely on obfuscation, hidden remotes, or UI restrictions. Do not add intrusive player surveillance or collect unnecessary personal data.

## Handoff
Return the remote inventory, state ownership map, operation contracts, changed files, tests actually executed, Studio scenarios not run, residual risks, and next owner.

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
