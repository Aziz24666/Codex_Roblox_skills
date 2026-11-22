---
name: roblox-monetization-launch-and-policy-readiness
description: Gate Roblox monetization releases on verified eligibility, clear disclosures, purchase integrity, and evidence.
---

# Monetization launch and policy readiness

## Mission
Prevent monetization from shipping with unknown eligibility, misleading prices, incomplete delivery, weak recovery, or outdated policy assumptions.

## Pre-launch gate
1. Inventory each paid surface, product type, price source, exact benefit, delivery owner, entitlement source, and rollback behavior.
2. Re-check current Roblox Terms, Community Standards, Creator Hub documentation, and program-specific rules. Record URL, date, owner, and evidence.
3. Verify account and experience eligibility/configuration in Creator Dashboard. A public feature page does not prove eligibility.
4. Ensure price, quantity, recurrence, duration, limitations, and benefits are visible before purchase.
5. Ensure custom price UI uses the applicable platform-returned value.
6. Verify server-owned catalogs, receipt/status validation, idempotent grants, persistence, and recovery.
7. Test subscription renewal, active-term benefits, expiration, cancellation, and per-period delivery.
8. Review analytics definitions, denominators, aggregate-only data, sample size, and retention guardrails.
9. Confirm support ownership, incident response, kill switch, rollback/forward recovery, and reconciliation visibility.
10. Mark each gate PASS, FAIL, NOT_RUN, or BLOCKED. PASS requires inspectable evidence and a named environment.

## Hard release gates
- Block gambling, paid random outcomes, and paid odds/chance modifiers.
- Block hidden costs, fake scarcity, deceptive discounts, misleading renewal disclosures, or undeliverable benefits.
- Block production rollout while server authority, transaction fulfillment, or subscription status remains unverified.
- Never bypass account, age, identity, region, or experience eligibility requirements.
- Never label dashboard, Studio, live purchase, or subscription checks PASS based on static inspection.

## Output
Produce a risk-ranked launch gate, requirement-to-evidence traceability, blockers, rollback owner, support readiness, and GO/NO-GO result. GO requires evidence for every critical gate.

## Official references
https://create.roblox.com/docs/production/monetization
https://create.roblox.com/docs/creator-rewards
https://create.roblox.com/docs/production/monetization/subscriptions

## Shared contracts
Preserve V18 no-gambling, V19 evidence, V20 production reliability, and V21 deterministic player-first product standards.


## V18 shared workflow and handoff contract
Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`. Own the assigned scope, preserve shared interfaces, and return a structured handoff with changed files, decisions, evidence, risks, blockers, and next owner.

## V19 verification and evaluation contract
Select checks from changed paths, impact, and trust boundaries. A plan is not a test result. Keep unexecuted Studio, device, marketplace, and live-service checks `NOT_RUN` or `BLOCKED`; never label them PASS without evidence.

## V20 production reliability contract
Keep consequential state server-authoritative. Use bounded retries, idempotent transactions, exact grants, safe migrations, operational observability, and recoverable rollouts. Preserve the mandatory no-gambling policy.

## V21 sustainable monetization contract
Discover opportunities from project evidence, rank by genuine player value and game fit, and use aggregate measurements. Do not fabricate revenue forecasts, use manipulative monetization, or degrade the free experience.
