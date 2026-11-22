---
name: roblox-subscription-lifecycle-and-entitlement-operations
description: Design transparent recurring subscriptions with server-confirmed status and reliable benefit delivery.
---

# Subscription lifecycle and entitlement operations

## Mission
Treat a subscription as a recurring service promise. Every paid benefit must be clear, delivered for the paid term, and reconciled safely.

## Workflow
1. Confirm recurring benefits are distinct, valuable, and operationally deliverable each billing period.
2. Check current official docs for product types, billing currency, regional pricing, APIs, and Creator Dashboard setup.
3. Define exact benefits, cadence, limitations, effective dates, expiration, and cancellation behavior.
4. Read status through supported server-side platform APIs. Client UI is presentation only and cannot grant entitlements.
5. Model pending/unavailable lookup, active term, renewal, cancellation, expiration, rejoin, and temporary API failure.
6. Make recurring grants idempotent with a durable billing-period key. Reconcile missed grants without duplication.
7. Distinguish durable purchases from term-limited benefits. Honor benefits promised for the active term.
8. Disclose recurring billing, price source, benefits, and cancellation management before purchase.
9. Test isolated data and approved test flows. Mark unexecuted live checks NOT_RUN.

## Reliability and fairness
- Never trust a client-supplied subscription state or renewal date.
- Never grant from a client-only purchase-finished event.
- A transient lookup failure must not create permanent entitlement or destructively revoke valid benefits.
- Prevent duplicate delivery within a billing period.
- Do not hide renewal or cancellation details, add post-payment gates, or use pressure messaging.
- No gambling, paid random rewards, paid chance changes, or deceptive countdowns.

## Output
Return the state model, entitlement table, recurring grant schedule, idempotency key, reconciliation procedure, disclosures, test matrix, and unverified checks.

## Official reference
https://create.roblox.com/docs/production/monetization/subscriptions

## Shared contracts
The V18 no-gambling policy remains mandatory. Apply V18 handoffs, V19 evidence, V20 reliability, and V21 purchase-integrity/fair-monetization rules.


## V18 shared workflow and handoff contract
Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`. Own the assigned scope, preserve shared interfaces, and return a structured handoff with changed files, decisions, evidence, risks, blockers, and next owner.

## V19 verification and evaluation contract
Select checks from changed paths, impact, and trust boundaries. A plan is not a test result. Keep unexecuted Studio, device, marketplace, and live-service checks `NOT_RUN` or `BLOCKED`; never label them PASS without evidence.

## V20 production reliability contract
Keep consequential state server-authoritative. Use bounded retries, idempotent transactions, exact grants, safe migrations, operational observability, and recoverable rollouts. Preserve the mandatory no-gambling policy.

## V21 sustainable monetization contract
Discover opportunities from project evidence, rank by genuine player value and game fit, and use aggregate measurements. Do not fabricate revenue forecasts, use manipulative monetization, or degrade the free experience.
