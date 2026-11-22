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
