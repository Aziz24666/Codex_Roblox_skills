# V22.0.1 — Platform monetization readiness and creator economics

V22.0.1 is a hardening update to the cumulative V1–V22 toolkit. It preserves all 196 skills and adds scanner completeness checks, explicit deprecated-API findings, stronger subscription grant-key validation, portable release checksums, and clearer Roblox pricing guidance.

## V22.0.0 features retained
- Creator Rewards eligibility review and healthy engagement improvements.
- Managed Pricing, regional-price readiness, dynamic display, and transfer safeguards.
- Subscription lifecycle, recurring benefit delivery, server-confirmed entitlements, and idempotent period grants.
- Platform revenue portfolio planning with distinct player-purchase, creator-reward, advertising, and marketplace accounting.
- Monetization release gate for policy, evidence, support, and rollback.

## V22.0.1 hardening
- Reject missing or invalid project roots in the pricing auditor.
- Report oversized/unreadable files and file-count truncation so incomplete scans are visible.
- Separate supported GetProductInfoAsync/GetDeveloperProductsAsync use from deprecated GetProductInfo calls.
- Require subscription grant keys to include product_id and billing_period_id.
- Generate relative checksum paths and verify the checksum file during CI.
- Clarify that price optimization is for passes/developer products, not subscriptions, and distinguish Robux/local-currency subscription pricing.

## Constraints and evidence boundaries
V18's no-gambling and fair-monetization rules remain mandatory. V22 adds no gambling, paid random outcomes, paid chance modifiers, artificial activity, manipulative session-length optimization, or individual-spender targeting. Static tools cannot verify dashboard eligibility, live subscriptions, or actual earnings.
