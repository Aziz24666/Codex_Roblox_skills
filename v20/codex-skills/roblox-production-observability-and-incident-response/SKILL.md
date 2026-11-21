---
name: roblox-production-observability-and-incident-response
description: Define privacy-safe Roblox service metrics, actionable alerts, production dashboards, incident triage, and recovery evidence.
---

# Roblox Production Observability and Incident Response

## Mission
Make failures visible early, diagnosable by the responsible owner, and recoverable without exposing player secrets or unnecessary personal data.

## Procedure
1. Identify critical player journeys and failure modes: join/session startup, remote operations, saves, purchases, matchmaking/teleports, and high-impact gameplay loops.
2. Define a small metric set with numerator, denominator, aggregation window, owner, and actionable alert threshold. Prefer rates and distributions to unbounded raw event logs.
3. Track at least server errors, remote rejections, data-save failures, transaction failures, and request/operation latency where applicable.
4. Use structured logs with stable correlation IDs and safe error categories. Never log secrets, authentication material, raw purchase receipts, or unnecessary personal data.
5. Restrict dashboards and diagnostic access to the appropriate team. Apply retention and access policies that match the data collected.
6. Build alerts with an owner, severity, runbook, deduplication, and clear action. Avoid alerting on a single noisy event without context.
7. Prepare incident runbooks for authority bypass, save degradation, incorrect grants, elevated server errors, and rollout regressions.
8. Preserve release identity, environment, timestamps, observed impact, mitigation, and recovery evidence. Keep speculation separate from confirmed facts.
9. Rehearse alert delivery and recovery in a safe environment. Do not claim production alerting works because a schema or package check passes.

## Review checklist
- Metrics represent actionable player/service health.
- Alert thresholds are grounded in a named baseline.
- Logs redact sensitive values and include useful correlation context.
- Dashboard access is restricted.
- Each alert has an owner and runbook.
- Incident containment and recovery steps are clear.
- Evidence distinguishes simulated incidents from real production events.

## Handoff
Return metric definitions, dashboard/alert ownership, redaction/access controls, incident playbooks, recovery evidence, and limitations or production checks not run.

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
