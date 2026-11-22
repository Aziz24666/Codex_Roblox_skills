# V22 — Managed Pricing and subscription operations

## Managed Pricing and dynamic custom UI

Managed Pricing can vary the price a player sees. A custom shop must not show a stale hard-coded number when Roblox's purchase prompt presents a different regional price.

Use the current MarketplaceService methods:
- `GetProductInfoAsync` for the regional price of one pass or developer product.
- `GetDeveloperProductsAsync` to retrieve all developer products and their relevant product information.

`GetProductInfo` is deprecated. Do not count a call to that legacy method as evidence that a project uses the current dynamic-price path.

Handle loading, retries, unavailable product information, and purchase prompt return without inventing a fallback price. Test the displayed price against the actual prompt in an authorized Roblox test experience.

For gifts and trades, assess regional price differences and current price-level safeguards. Roblox documents `GetUsersPriceLevelsAsync` for this purpose; retrieve current levels at session start and again as appropriate for transfers rather than relying on stale cross-session cached values. Enforce transfer rules on the server and test concurrent and duplicate transfers.

## Price optimization

Price optimization is part of Managed Pricing, but it is not an instruction to raise prices. Verify current dashboard eligibility, data sufficiency, dynamic-price readiness, test status, and reporting. The current Roblox documentation describes price optimization for **passes and developer products only**; it is not available for subscriptions. Separate platform-managed tests from creator-run UI experiments. Review long-term player value and retention alongside short-term sales.

## Subscription pricing and lifecycle

Roblox subscriptions renew monthly and can be priced in Robux or local currency. Regional/Managed Pricing is enabled by default for subscriptions priced in Robux and cannot be turned off; subscriptions priced in local currency do not use regional pricing. Check current official documentation and the actual product configuration before showing a price or offering a subscription to players.

A subscription is a recurring promise. Define the benefits and delivery schedule. Keep benefits available for the paid term, validate status through supported server-side APIs, and make period grants idempotent with a key that includes both the product/subscription ID and the billing-period ID.

Model pending lookup, active status, renewal, cancellation, expiration, and reconciliation after missed delivery. Never treat a client event as entitlement proof. A temporary service error must not create permanent entitlement or destructively revoke valid benefits. Disclose renewal and cancellation before purchase.

## Official references
- https://create.roblox.com/docs/production/monetization/regional-pricing
- https://create.roblox.com/docs/production/monetization/price-optimization
- https://create.roblox.com/docs/production/monetization/subscriptions
- https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
