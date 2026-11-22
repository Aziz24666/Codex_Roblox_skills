# V23 — Roblox revenue opportunity playbook

## Goal
Find the broadest viable monetization portfolio for the actual experience, without turning every game mechanic into a paywall. V23 searches beyond game passes and developer products: subscriptions, access models, private servers, platform-funded Creator Rewards, ads, avatar products, and creator-facing Creator Store products.

The catalogue has 48 candidate routes. The CLI always reports the full catalogue, ranks entries supported by project evidence, and shows the evidence behind each match. A missing match means the scanner did not find evidence; it does not prove the game cannot support the idea.

## Revenue families

### In-experience Robux purchases
- Permanent passes with clear, durable benefits.
- Repeatable developer products with exact contents and quantities.
- Cosmetic collections, outfits, emotes, animations, auras, titles, vehicle/pet/housing appearance, and saved customization presets.
- Optional content expansions such as authored missions, maps, challenges, or extra game modes.
- Convenience options such as saved loadout slots, save slots, inventory capacity, and travel only to places already unlocked.
- Deterministic currency, crafting-material, and consumable packages with exact grants.
- Season passes with a published, guaranteed reward list and a worthwhile free track.
- Subscriptions only when recurring benefits are actually delivered every billing period.

### Social and access options
- Private servers when playing with friends or communities is meaningful.
- Group, guild, clan, party, and team identity cosmetics.
- Robux paid access only when a genuine closed-beta access model makes sense.
- Paid access and private servers are mutually exclusive experience-level configurations in Roblox's documented model. Verify current settings before choosing one; do not plan to enable both simultaneously.

### Platform-funded and creator-business routes
- Creator Rewards for genuine, satisfying engagement. Current Daily Engagement Rewards pay 5 Robux when an Active Spender plays the experience for at least 10 minutes and it is one of the first three experiences they play that day. Active Spender status requires at least $9.99 of platform spend in the previous 60 days.
- Audience Expansion Rewards can provide a 35% revenue share on a referred New or Reactivated User's first $100 of qualifying purchases during their first 60 days, subject to attribution, experience engagement/DAU conditions, ID-verification, good-standing, and other current program requirements. Verify eligibility and current rules in Creator Dashboard.
- Immersive ads only when the experience and owner satisfy current eligibility.
- Avatar catalog or affiliate products only when current marketplace features and permissions support them.
- Creator Store models, plugins, and assets as a separate creator-business revenue line.

These streams have different eligibility, reporting, payout, and accounting rules. Creator Rewards depend on genuine qualifying users, not just raw playtime. Never encourage artificial activity, bots, teleport manipulation, or alternate accounts to generate rewards. Never combine the streams into one unexplained Robux number.

## Prioritization model
Evaluate each opportunity on evidence that the underlying feature exists, player value and game fit, a fair free alternative, build/support cost, platform eligibility, technical reliability, and aggregate demand evidence from playtests and analytics.

A high fit score means the project contains more relevant signals. It does not mean the product will sell, or that any Robux amount will be earned.

## Store portfolio design
- Offer meaningful variety rather than duplicating near-identical products.
- Use one-time products for permanent benefits, developer products for clearly described repeat purchases, and subscriptions only for recurring benefits.
- Show product images, exact item lists, price, quantity, duration, recurrence, restrictions, and ownership behavior.
- Keep a free route to core gameplay, meaningful progression, and basic identity features.
- Use platform-returned prices in custom UI when Managed Pricing applies. The Roblox purchase prompt is the authoritative confirmation.

Do not sell a random reward, random duration, random upgrade, random chance modifier, or currency bundle that feeds a chance-based purchase. V18's no-gambling policy is stricter than any platform rule that might permit a disclosed chance mechanic.

## Required evidence before building an offer
For each selected opportunity, record the exact feature, player benefit, product type, fixed grant, purchase surface, price source, entitlement owner, persistence behavior, rollback path, support owner, and relevant platform documentation. Confirm live eligibility and configuration in Creator Dashboard. Static analysis cannot do this.

## Official Roblox references
- https://create.roblox.com/docs/production/monetization
- https://create.roblox.com/docs/production/game-design/monetization-foundations
- https://create.roblox.com/docs/production/monetization/passes
- https://create.roblox.com/docs/production/monetization/developer-products
- https://create.roblox.com/docs/production/monetization/subscriptions
- https://create.roblox.com/docs/production/monetization/price-optimization
- https://create.roblox.com/docs/creator-rewards
- https://create.roblox.com/docs/production/monetization/immersive-ads
- https://create.roblox.com/docs/production/analytics/monetization
