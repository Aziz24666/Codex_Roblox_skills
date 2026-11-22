# V22 Overlay

V22 adds five specialists for Creator Rewards, Managed Pricing, subscription operations, creator-revenue portfolios, and monetization release readiness.

## Commands
```bash
python v22/tools/v22.py audit-pricing --root . --output reports/v22-pricing-readiness.json
python v22/tools/v22.py validate-subscription-contract --root . --file v22/examples/subscription-contract.example.json
python v22/tools/v22.py evaluate-routing --root .
python v22/tools/v22.py verify --root .
```

The pricing auditor is a heuristic Luau source scan. It flags likely hard-coded prices, supported dynamic-price API usage, deprecated GetProductInfo calls, price-level APIs, and subscription APIs. It rejects a missing project root and reports file-count truncation, oversized files, and unreadable files rather than silently presenting an incomplete scan as complete.

Findings require human review. The scanner does not parse all Luau syntax, inspect Creator Dashboard eligibility, inspect active price tests, or prove live behavior. Subscription-contract validation is static; test purchases, renewal, expiration, cancellation, and reconciliation in an authorized Roblox environment.

Roblox documents price optimization for passes and developer products, not subscriptions. Robux-priced subscriptions have Managed Pricing enabled by default, while local-currency subscriptions do not use regional pricing; verify the current official documentation before implementing these flows.
