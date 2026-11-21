---
name: roblox-monetization-purchase-integrity
description: Implement reliable Roblox purchase catalogs, receipt handling, exact grants, and entitlement reconciliation.
---

# Monetization purchase integrity

## When to use
Use when implementing or auditing passes, developer products, subscriptions, fixed bundles, or paid entitlements.

## Required architecture
1. Maintain one server-owned catalog with immutable product IDs, exact contents, price source, currency, purchase class, repeatability, duration, prerequisites, entitlement semantics, and catalog version.
2. Treat the client as presentation and request input only. Never accept client-supplied authoritative prices, grants, balances, ownership, or receipt success.
3. Use current Roblox MarketplaceService APIs and official receipt-processing guidance. Re-check current documentation before coding; do not copy deprecated patterns.
4. Process developer-product receipts on the server with durable transaction IDs, exact fixed grants, idempotent retries, and safe behavior when persistence is unavailable.
5. Reconcile passes and subscription entitlements against current platform ownership/status. Remove temporary benefits at the correct expiry or cancellation boundary.
6. Ensure the product description matches the actual grant, duration, recurrence, and limitations.
7. Make concurrent requests, duplicate receipts, reconnects, data-store failures, refund/support cases, and catalogue migrations explicit.
8. Record a transaction ledger without storing secrets or unnecessary personal data.

## Required tests
Test unknown IDs, forged client prices, invalid grants, duplicate receipt delivery, concurrent purchase requests, persistence outages, reconnect recovery, entitlement expiry, subscription cancellation, and exact grant parity. Use a test environment and never claim live purchase verification from static CI.

## Hard constraints
All grants are deterministic and known before purchase. The mandatory V18 no-gambling policy applies to every product and currency path. Reject any paid flow whose result is uncertain or probability-based.

## Output contract
Provide catalog schema, server authority boundaries, receipt flow, idempotency design, entitlement lifecycle, UI disclosures, negative tests, and runtime evidence requirements.

## V18 shared workflow and handoff contract
Preserve shared transaction and no-gambling policies.

## V19 verification and evaluation contract
Use deterministic fixtures, risk-based testing, and honest evidence statuses.

## V20 production reliability contract
Use server-owned state, safe persistence, idempotent grants, and production observability.

## V21 sustainable monetization contract
Only exact, accurately described, optional purchase outcomes are allowed.
