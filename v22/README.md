# V22 Overlay

V22 adds five specialists for Creator Rewards, Managed Pricing, subscription operations, creator-revenue portfolios, and monetization release readiness.

## Commands
```bash
python v22/tools/v22.py audit-pricing --root . --output reports/v22-pricing-readiness.json
python v22/tools/v22.py validate-subscription-contract --root . --file v22/examples/subscription-contract.example.json
python v22/tools/v22.py evaluate-routing --root .
python v22/tools/v22.py verify --root .
```

The pricing auditor scans Luau source for likely hard-coded price assignments and evidence of platform APIs. Findings require human review; the scanner cannot inspect Creator Dashboard eligibility or prove live behavior. Subscription validation is a static contract check; test purchases, renewal, expiration, cancellation, and reconciliation in an authorized Roblox environment.
