# V21 — Offer selection, pricing, and measurement

## Build a coherent portfolio

Start from a player's real goals in the game: customization, expression, social play, creativity, convenience, or access to ongoing content. A good portfolio is small, comprehensible, and easy to maintain. Avoid duplicative products that confuse the shop or provide unclear incremental value.

For every offer record:
1. The game system and code/design evidence it depends on.
2. The player's problem or optional desire it serves.
3. The exact contents or benefit, including the complete duration for temporary benefits.
4. Purchase class, price owner, prerequisites, and entitlement semantics.
5. Earnable/free alternatives for meaningful progression.
6. Server grant path, receipt idempotency, reconciliation, and failure recovery.
7. Accessibility, policy, retention, balance, and support risks.
8. Metrics needed to judge whether the offer helps both players and the experience.

## Pricing process

Use controlled tests with a written hypothesis and a baseline. Change one major variable at a time. Verify that analytics use the same population and time window. Prefer official managed/automated price testing and regional pricing where eligible and configured. Re-check current documentation and Creator Dashboard because product availability and platform rules can change.

A higher purchase conversion rate is not automatically a better result. Review net revenue, refunds, payer retention, overall retention, support issues, and sentiment. Stop experiments that materially harm the experience or misrepresent value.

## Metrics

Use consistent definitions for shop open rate, purchase conversion, payer conversion, ARPPU, and ARPDAU. Separate gross, net, pending, and refunded Robux; state the exact reporting window and data source. Never treat unique active users as daily active users or divide by an unrelated denominator.

The V21 CLI computes only the aggregate metrics for which input fields are supplied. Missing or zero denominators produce null values. It does not produce forecasts or claims of causal lift.

## Release gate

Before release, verify every advertised benefit, price, duration, and recurrence against server-owned product data and real runtime behavior. Run accessibility checks, duplicate receipt tests, entitlement expiry/cancellation tests, and actual authorized Studio purchase-flow tests. Static CI is not evidence that a live Robux purchase has succeeded.
