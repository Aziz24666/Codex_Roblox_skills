# V18 No-Gambling and Fair Monetization Policy

**Status:** Mandatory design constraint for V18 and projects using its economy specialists.  
**Last reviewed against official Roblox documentation:** 2026-11-21.

## 1. Absolute no-gambling rule

V18 must not design, implement, recommend, or retain gambling-like systems. Monetized offers must have a deterministic, fully disclosed result. Do not build any purchase or Robux-funded path whose outcome, reward, or success depends on chance. This includes indirect paths where Robux buys currency, tickets, keys, items, or modifiers that then feed a random outcome.

Do not add paid random rewards, wagering, paid spins/draws, mystery purchases, paid rerolls, chance-based paid upgrades, paid luck modifiers, or systems that risk losing purchased value. Do not treat an odds disclosure, regional eligibility check, or policy API as permission to relax this toolkit's stricter no-gambling rule.

## 2. Supported deterministic monetization methods

The following are possible models, subject to current Roblox rules and a player-first design review:

| Method | Appropriate deterministic use | Required disclosure |
|---|---|---|
| Cosmetics and customization | Fixed skins, outfits, accessories, emotes, animations, titles, visual effects | Exact item(s), price, and whether ownership is permanent |
| Game passes | A defined one-time privilege, access right, or permanent item | Exact benefit, price, conditions, and any platform ownership limitations |
| Developer products | Repeatable purchase of a specific item or exact quantity of currency | Exact contents, quantity, price, and fulfillment behavior |
| Subscriptions | Recurring access or benefits that are actually delivered each billing period | Price, renewal cadence, benefits, cancellation/expiry behavior |
| Paid experience access | One-time access fee for the experience | Fee and what access it unlocks |
| Private servers | Optional private server access | Recurring price, who can join, and access terms |
| Avatar items / Creator Store | Fixed-price avatar items, models, or plugins where applicable | Exact asset/product and price |

A developer product or currency top-up must never be a disguised route into a randomized result. Do not add any pay-to-randomize mechanic.

**Mutual-exclusion constraint:** Roblox does not allow paid experience access (whether priced in Robux or local currency) and private servers to be enabled for the same experience at the same time. Treat these as mutually exclusive experience-level access configurations, not as two simultaneously available options. Re-check the platform settings and current Creator Hub guidance before changing an experience's access model.

## 3. Earned currency and progression

- Make earned currency a meaningful route through the core game. Grant fixed values for server-validated gameplay outcomes.
- If direct currency sales are present, they must be optional, grant an exact stated amount, and never be the only route through core progression.
- Every shop purchase must have a fixed product ID, fixed contents, and a fixed price owned by the server.
- For tiered catalogs, the next tier unlocks only after the player owns every required item in every earlier tier.
- Required tier items must have a clear achievable non-Robux acquisition route. Do not make Robux purchases mandatory to satisfy a tier gate.
- Keep currency, inventory, and tier state authoritative on the server. Make transactions idempotent and auditable.

## 4. Honest and accessible shop UX

Show the exact item, contents, quantity, price, currency, duration, recurrence, and important restrictions before a player confirms. Clearly distinguish one-time payments from recurring subscriptions. The purchase action must be deliberate and player-initiated, with an obvious cancel path.

Do not use fake scarcity, misleading discounts, perpetually restarting countdowns, hidden costs, confusing currency conversions, pressure copy, or repeated purchase interruptions. A discount or limited-time claim must be genuine and verifiable. Keep ordinary gameplay enjoyable without spending.

## 5. Purchase and entitlement integrity

Use current Roblox APIs and server-side receipt processing for platform purchases. Verify product identifiers and grants against a server-owned catalog. Process receipts idempotently, safely handle retries and persistence failures, reconcile entitlements on join, and grant exactly what the product description promises. Never trust a client event as proof that payment succeeded.

For subscriptions and passes, verify current ownership/entitlement semantics before applying benefits. Do not permanently persist benefits that should expire when a subscription or temporary entitlement ends.

## 6. Required V18 specialists

- `roblox-player-friendly-monetization` — product strategy, strict no-gambling review, and truthful disclosures.
- `roblox-deterministic-progression-shop` — catalog, fixed prices, shop UX, and purchase fulfillment.
- `roblox-tiered-catalog-progression` — all-earlier-tier ownership requirements and migration rules.
- `roblox-earned-currency-economy` — predictable gameplay earnings, economy accounting, and currency integrity.

Load `roblox-shop-ux-and-accessibility`, persistence, transaction, and security specialists when the task affects those areas.

## 7. Official platform references

Re-check these sources before release because platform APIs and requirements can change:

- Roblox Creator Hub — Monetization: https://create.roblox.com/docs/production/monetization
- Roblox Creator Hub — Passes: https://create.roblox.com/docs/production/monetization/passes
- Roblox Creator Hub — Developer Products: https://create.roblox.com/docs/production/monetization/developer-products
- Roblox Creator Hub — Subscriptions: https://create.roblox.com/docs/production/monetization/subscriptions
- Roblox Creator Hub — Private Servers: https://create.roblox.com/docs/production/monetization/private-servers
- Roblox Creator Hub — Paid Access in Robux: https://create.roblox.com/docs/production/monetization/paid-access-robux
- Roblox Creator Hub — Paid Random Items Policy: https://create.roblox.com/docs/production/monetization/paid-random-items

These references describe Roblox platform capabilities and requirements; V18 intentionally excludes paid random items even if a platform page documents eligibility controls or disclosures for them.
