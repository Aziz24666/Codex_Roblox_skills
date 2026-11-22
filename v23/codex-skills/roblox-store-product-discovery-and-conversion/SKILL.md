---
name: roblox-store-product-discovery-and-conversion
description: Improve product discovery and transparent purchase completion using Roblox-supported store APIs.
---

# Store product discovery and conversion

## Mission
Help players find offers they genuinely value and understand exactly what they are buying. Improve purchase completion through clarity and reliable delivery, never coercion.

## Workflow
1. Inventory passes, developer products, subscriptions, avatar products, and eligible platform catalog items.
2. Map each product to its actual player benefit, permanent/temporary nature, quantity, duration, restrictions, price source, and server-owned grant.
3. Review RankProductsAsync and RecommendTopProductsAsync in current official docs. Load rank recommendations once at join due to rate limits; handle empty recommendations and provide a useful fallback shop.
4. Show a clear thumbnail, item preview, fixed contents, quantity, dynamic platform price where applicable, ownership status, duration, and renewal details before the purchase prompt.
5. Offer a deliberate purchase action and a clear cancel path. Do not reopen a cancelled prompt or interrupt ordinary gameplay with repeated offers.
6. Keep client UI informational; server-side receipt processing and entitlement checks own consequential grants.
7. Test slow/unavailable product intelligence, unknown products, owned items, prompt cancellation, receipt retries, duplicate delivery, and reconnect reconciliation.
8. Track aggregate funnel and support issues; optimize product clarity and relevance rather than player vulnerability.

## Requirements
- No stale hard-coded regional price display for managed products.
- No false discounts or fake scarcity.
- No personalized pressure based on spending history or inferred financial capacity.
- No paid random rewards or chance modifiers.
- Product recommendations are not proof of demand and do not replace playtesting.

## Output
Return a catalogue map, recommendation API plan, store UX audit, dynamic pricing review, server purchase-flow map, aggregate funnel definition, and regression tests.

## Shared contracts
Preserve V18 no-gambling, V19 evidence, V20 server-authority, V21 fair monetization, and V22 platform-monetization rules.
