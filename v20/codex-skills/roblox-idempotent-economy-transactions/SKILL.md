---
name: roblox-idempotent-economy-transactions
description: Build deterministic Roblox purchase fulfillment with verified receipts, exact grants, duplicate protection, and auditable transaction records.
---

# Roblox Idempotent Economy Transactions

## Mission
Ensure every paid product maps to a fixed, server-owned grant and duplicate receipt delivery cannot duplicate value.

## Procedure
1. Inspect the existing MarketplaceService integration, product catalogue, currency ownership, receipt handler, save path, and V18 monetization policy before editing.
2. Treat client purchase prompts as presentation only. The server owns product IDs, prices, entitlements, receipt decisions, and grant definitions.
3. Process only server-provided, verified receipt data through the supported ProcessReceipt flow. Do not accept a client message as proof of payment.
4. Persist a stable receipt/transaction identifier with the grant decision. A repeated receipt must resolve to the same completed outcome without granting again.
5. Use an atomic or otherwise concurrency-safe grant/receipt operation. Reconcile grant records with player balances and handle retries or server interruption without partial duplication.
6. Grant the exact configured fixed amount/item. Validate product configuration and reject unknown product IDs safely.
7. Keep monetization deterministic and player-friendly. Never introduce paid random rewards, wagers, paid rerolls, or Robux-funded chance outcomes.
8. Test duplicate receipt delivery, interruption before/after persistence, retry, unknown products, player departure, and conflicting concurrent requests using isolated test configurations.

## Review checklist
- Product ID resolves to exactly one fixed grant definition.
- The grant is server-side and cannot be edited by client input.
- Receipt identifiers are durable and deduplicated.
- A repeated receipt cannot grant twice.
- Unknown/invalid products are not silently fulfilled.
- No paid chance mechanics exist.
- Reconciliation and support evidence do not expose private player data.

## Handoff
Return the product/grant matrix, transaction state model, idempotency key design, persistence contract, failure/replay scenarios, test results, and any live receipt checks not run.

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
