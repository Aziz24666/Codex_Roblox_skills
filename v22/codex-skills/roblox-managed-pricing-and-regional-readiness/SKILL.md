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
3. Inspect the current MarketplaceService APIs and use supported product-information methods for custom price UI.
4. Test loading, retries, unavailable product information, regional differences, and agreement with the purchase prompt. Never invent a fallback price.
5. For developer products, check current Managed Pricing prerequisites and dynamic scripting requirements.
6. If gifts or trades exist, inspect current price-level guidance and enforce transfer checks on the server. Test arbitrage, duplicate transfers, and concurrency.
7. Review passes, developer products, and subscriptions separately; do not generalize one product type's defaults to another.
8. Verify current price-optimization eligibility and test status in Creator Dashboard. Do not assume eligibility or hard-code old volume thresholds.
9. Compare aggregate conversion and revenue alongside retention, support, and fairness indicators. Distinguish correlation from causal lift.

## Mandatory checks
- No stale hard-coded display amount for regionally managed products.
- No client-authoritative price, entitlement, or transfer approval.
- Product-information failure must not display a fabricated price.
- Transfer rules must be server-owned and tested.
- Platform-managed price tests must be distinguished from creator-run experiments.

## Output
Return a price-source inventory, code evidence, regional behavior matrix, transfer risk review, eligibility unknowns, and migration/test plan.

## Official references
https://create.roblox.com/docs/production/monetization/regional-pricing
https://create.roblox.com/docs/production/monetization/price-optimization

## Shared contracts
Preserve V18 no-gambling, V19 evidence, V20 server authority, and V21 fixed-known-outcome product rules.
