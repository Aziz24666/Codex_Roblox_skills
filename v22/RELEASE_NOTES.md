# V22.0.1 — Platform monetization readiness and creator economics

V22.0.1 hardens the cumulative V1–V22 Roblox Codex toolkit. It keeps all 196 skills and improves verification accuracy:

- Rejects missing project roots and reports oversized, unreadable, or truncated pricing scans.
- Distinguishes supported GetProductInfoAsync/GetDeveloperProductsAsync calls from deprecated GetProductInfo usage.
- Requires subscription period grant keys to include product_id and billing_period_id.
- Uses portable relative paths in SHA256SUMS-RELEASE.txt and validates the file during CI.
- Clarifies the current separation between pass/developer-product price optimization and subscription pricing.

V22.0.0 introduced Creator Rewards, Managed Pricing, regional pricing, subscription lifecycle operations, creator revenue portfolio planning, and monetization launch readiness.

The V18 no-gambling rule remains mandatory. CI does not execute Roblox Studio, access Creator Dashboard eligibility, or prove live purchases or subscription fulfillment.
