# V22 — Monetization launch gate and evidence

Each critical check must be PASS, FAIL, NOT_RUN, or BLOCKED. PASS requires the exact check, environment, tool/runtime version, build identity, expected and observed behavior, and inspectable evidence.

## Critical gates
- Product eligibility and configuration are confirmed in Creator Dashboard.
- Product type and current platform rules have been checked against official documentation.
- Custom price UI uses the appropriate platform-returned price.
- Server-owned catalog, receipt/status validation, and idempotent grants are tested.
- Subscription renewal, paid-term benefits, expiry, cancellation, and recurring grants are verified where applicable.
- Price, quantity, recurrence, duration, limits, and benefits are disclosed before purchase.
- No gambling, paid random outcomes, paid chance modifiers, hidden costs, false scarcity, or manipulative pressure tactics exist.
- Analytics have defined events, denominators, observation windows, and sample-size caveats.
- Support owner, incident response, kill switch, and recovery process are documented.

## Do not infer
A local scan cannot inspect Creator Dashboard, account standing, Managed Pricing configuration, active price tests, live marketplace behavior, receipts, subscription status, or earnings. Mark these checks NOT_RUN until an authorized owner verifies them.

## Rollback
Separate reversible UI/catalog changes from irreversible grants and data migrations. Consider active subscriptions and delivery promises before removing an offer. Do not silently revoke paid benefits. Keep reconciliation and support procedures.

The V18 no-gambling rule remains mandatory. Do not implement paid random rewards, paid odds changes, betting/wagering, or disguised equivalents.
