# V23 — Player engagement and store optimization

## Engagement that earns the right to offer something
The strongest sustainable monetization starts with a game players choose to revisit. Improve first-session clarity, responsive controls, core-loop depth, mastery, authored challenges with fixed rewards, collections, co-op/social play, seasonal content, stability, accessibility, and reliable saves.

Measure whether players enjoy the experience. Do not artificially stretch a session to reach a platform reward threshold, force attendance, punish players for missing a day, or use AFK loops. Never use player spending history to decide who deserves pressure, discounts, or prompts.

## Store discovery
Roblox documents product-intelligence APIs for product discovery:
- RankProductsAsync can rank a supplied set of eligible product IDs for a player. It has a strict rate limit; load results once at join rather than repeatedly.
- RecommendTopProductsAsync can return top product recommendations, but may return an empty list when the experience has no item sales in the previous 28 days. Build a useful fallback catalogue instead of an empty storefront.
- Run recommendation work non-blockingly where appropriate and handle empty, unavailable, or slow results gracefully.
- Do not call ranking APIs on every frame, every UI redraw, or every shop open.

Use recommendations to improve relevance and discovery. Keep the offer, price, benefits, and purchase choice transparent. Do not implement spending-based player profiling or pressure tactics.

## Store UX and funnel
Players should be able to browse without interruptions. Show the exact item and preview, exact quantity/benefit, price, duration, recurrence, and limitations. Let the player deliberately open the Roblox purchase prompt. Respect cancellation. Verify delivery on the server and reconcile ownership after reconnecting.

Track aggregate store visits, product detail views, purchase prompts, completed purchases, successful grants, support/refund issues, and later returns. A higher prompt count is not necessarily better if satisfaction or retention gets worse.

## Testing and optimization
Use platform-managed price optimization for passes and developer products only when eligible and dynamically scripted; do not apply it to subscriptions. Compare aggregate cohorts with sufficient samples. Guardrail metrics include retention, game completion, crash/error rate, purchase failures, cancellation/support volume, and fairness complaints. Stop changes that improve short-term revenue while harming enjoyment, reliability, or free progression.

## No-pressure checklist
- No paid random rewards, paid spins, paid rerolls, loot boxes, wagers, or chance modifiers.
- No fake timers, fake discounts, false stock limits, or deceptive urgency.
- No purchase prompt after every failure, death, level, or low-currency event.
- No artificial wait, forced ad, AFK reward loop, or session-length manipulation.
- No client-authoritative price, receipt, entitlement, or inventory grant.
- No paywall on basic onboarding, core controls, or a reasonable free route through the experience.
