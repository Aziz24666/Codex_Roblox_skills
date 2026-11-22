# V22 — Managed Pricing and subscription operations

## Managed Pricing
Managed Pricing can change prices displayed to different players. Custom shop interfaces must not show stale hard-coded prices when the purchase prompt uses a different regional price.

Review each product type separately. Use currently supported MarketplaceService product-information APIs for custom UI. Handle loading and failures without inventing a price, then test that the UI matches the purchase prompt for multiple price contexts.

For gifts/trades, assess regional price differences and current price-level safeguards. Enforce transfer rules on the server and test concurrent and duplicate transfers.

## Price optimization
Price optimization is not an instruction to raise prices. Verify current dashboard eligibility, data sufficiency, dynamic-price readiness, test status, and reporting. Separate platform-managed tests from creator-run UI experiments. Review longer-term player value and retention alongside short-term sales.

## Subscription lifecycle
A subscription is a recurring promise. Define benefits and delivery schedule. Keep benefits available for the paid term, validate status through supported server-side APIs, and make periodic grants idempotent.

Model pending lookup, active status, renewal, cancellation, expiration, and reconciliation after missed delivery. Never treat a client event as entitlement proof. A temporary service error must not create permanent entitlement or destructively revoke valid benefits. Disclose renewal and cancellation before purchase.

## Official references
- https://create.roblox.com/docs/production/monetization/regional-pricing
- https://create.roblox.com/docs/production/monetization/price-optimization
- https://create.roblox.com/docs/production/monetization/subscriptions
