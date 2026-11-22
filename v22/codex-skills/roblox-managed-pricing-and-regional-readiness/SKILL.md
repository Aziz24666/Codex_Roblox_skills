---
name: roblox-managed-pricing-and-regional-readiness
description: Audit Managed Pricing, dynamic price displays, regional pricing, and server-side transfer safeguards.
---

# Managed Pricing and regional readiness

## Mission
Make custom shop prices accurate and compatible with Roblox Managed Pricing. Never hard-code a display value that can differ from the current platform price.

## Workflow
1. Inventory passes, developer products, subscriptions, shop labels, cached prices, gifts, and trade flows.
2. Classify each displayed amount as a platform-returned value, creator-owned fixed configuration, stale cache, or hard-coded literal.
3. For one pass or developer product, use MarketplaceService:GetProductInfoAsync; for all developer products, use MarketplaceService:GetDeveloperProductsAsync. Do not count deprecated GetProductInfo as a modern dynamic-pricing implementation.
4. Test loading, retries, unavailable product information, regional differences, and agreement with the purchase prompt. Never invent a fallback price.
5. For developer products, check current Managed Pricing prerequisites and dynamic scripting requirements.
6. If gifts or trades exist, inspect current price-level guidance and enforce transfer checks on the server. Test arbitrage, duplicate transfers, and concurrency.
7. Review passes, developer products, and subscriptions separately; do not generalize one product type's defaults to another.
8. Price optimization applies to passes and developer products, not subscriptions. Verify current eligibility, dynamic-price readiness, data sufficiency, and test status in Creator Dashboard; do not assume eligibility or hard-code old volume thresholds.
9. Compare aggregate conversion and revenue alongside retention, support, and fairness indicators. Distinguish correlation from causal lift.

## Mandatory checks
- No stale hard-coded display amount for regionally managed products.
- No client-authoritative price, entitlement, or transfer approval.
- Product-information failure must not display a fabricated price.
- Transfer rules must be server-owned and tested.
- Platform-managed price tests must be distinguished from creator-run experiments.
- Robux-priced subscriptions have Managed Pricing enabled by default; subscriptions priced in local currency do not use regional pricing.
- Do not recommend subscription price optimization; Roblox documents price optimization for passes and developer products.

## Output
Return a price-source inventory, code evidence, regional behavior matrix, transfer risk review, eligibility unknowns, and migration/test plan.

## Official references
https://create.roblox.com/docs/production/monetization/regional-pricing
https://create.roblox.com/docs/production/monetization/price-optimization

## Shared contracts
Preserve V18 no-gambling, V19 evidence, V20 server authority, and V21 fixed-known-outcome product rules.


## V18 shared workflow and handoff contract
Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`. Own the assigned scope, preserve shared interfaces, and return a structured handoff with changed files, decisions, evidence, risks, blockers, and next owner.

## V19 verification and evaluation contract
Select checks from changed paths, impact, and trust boundaries. A plan is not a test result. Keep unexecuted Studio, device, marketplace, and live-service checks `NOT_RUN` or `BLOCKED`; never label them PASS without evidence.

## V20 production reliability contract
Keep consequential state server-authoritative. Use bounded retries, idempotent transactions, exact grants, safe migrations, operational observability, and recoverable rollouts. Preserve the mandatory no-gambling policy.

## V21 sustainable monetization contract
Discover opportunities from project evidence, rank by genuine player value and game fit, and use aggregate measurements. Do not fabricate revenue forecasts, use manipulative monetization, or degrade the free experience.
