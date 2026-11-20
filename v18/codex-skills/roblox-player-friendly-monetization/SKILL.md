---
name: roblox-player-friendly-monetization
description: Design transparent Roblox monetization with deterministic products, fair pricing, and a strict no-gambling policy.
---

# Player-friendly Roblox monetization

## Non-negotiable V18 policy: no gambling

Do not design, implement, recommend, or retain gambling-like mechanics. Every monetized outcome must be deterministic and clearly defined before the player confirms a purchase.

Never include:
- Paid random rewards or purchases whose result is selected by chance.
- Paid spins, prize draws, loot openings, mystery purchases, paid rerolls, or wagers.
- Paid currency, tickets, keys, or items that can be spent or converted into a random outcome.
- Purchases that change the chance of a random reward or upgrade.
- Paid random upgrades, paid chance boosts, or paid systems that risk losing a purchased item or currency.

This is an intentional toolkit rule, not a suggestion to implement a restricted mechanic with odds disclosures or eligibility checks. Do not add such systems even where platform APIs may support region-specific eligibility. Prefer deterministic rewards and fixed catalogs.

## Approved deterministic monetization models

Use only methods that clearly state what the player receives and what the purchase costs:
- **Cosmetics and customization:** fixed-price outfits, skins, accessories, emotes, animations, titles, visual effects, and other clearly specified cosmetic items.
- **Game passes:** one-time purchases for a defined permanent privilege or item. Check current ownership when applying benefits; do not treat a pass as a guaranteed forever entitlement if the platform says otherwise.
- **Developer products:** repeatable purchases that grant an exact item, a clearly stated quantity, or a known fixed amount of currency. Fulfill receipts on the server using the current Roblox receipt-processing API, with idempotent transaction handling.
- **Subscriptions:** recurring benefits described precisely, including renewal cadence, duration, eligibility, and how cancellation affects benefits. Never disguise recurring billing as a one-time purchase.
- **Paid access:** a clearly disclosed one-time fee to access the experience or a defined access tier.
- **Private servers:** optional server access at a clearly displayed fixed recurring price; preserve a useful free-play option when suitable.
- **Avatar and Creator Store products:** fixed-price avatar items, models, or plugins where relevant to the creator's business.

A paid currency top-up, when used, must grant an exact disclosed quantity. It must never fund random outcomes or chance modifiers. Gameplay-earned currency must remain a meaningful route through the core progression.

## Player-first requirements

1. Keep the core experience understandable and enjoyable without spending.
2. Display the exact price, currency, contents, quantity, duration, and important limitations before the purchase prompt.
3. Distinguish one-time purchases from subscriptions and state recurring terms clearly.
4. Avoid false scarcity, permanently repeating countdowns, fake discounts, misleading comparisons, pressure language, or purchase prompts that interrupt ordinary play.
5. Never imply that an item is exclusive, limited, or discounted unless that claim is true and verifiable.
6. Make purchase confirmation deliberate and initiated by the player. Provide a clear cancel/back path.
7. Offer gameplay-earned routes for core progression. Do not make spending Robux mandatory to complete the game's ordinary progression or to satisfy tier-unlock requirements.
8. Grant precisely the advertised product. Handle refunds, ownership changes, retries, duplicate receipts, and persistence failures safely.
9. Keep the authoritative catalog and prices on the server. Treat the client as presentation/input only.
10. Record the design decision and current official platform-policy sources in the task's research/decision record.

## Implementation review

Before approving a monetization feature, answer:
- Is the outcome fixed and known before purchase?
- Can the player identify the exact item, amount, duration, and price?
- Is any Robux-funded value involved in a random result, wager, or chance modifier? If yes, reject the feature.
- Can the essential progression still be completed without spending?
- Are purchase grants server-authoritative, idempotent, and auditable?
- Are recurring charges, cancellation, eligibility, refunds, and ownership transitions handled accurately?
- Does the UX avoid pressure and misleading claims?

If any answer is unknown, mark the feature BLOCKED pending research or implementation evidence; do not claim compliance.

## Required handoff

Return the exact products reviewed, allowed/rejected decisions, player-facing disclosures, server-side fulfillment design, official sources checked, tests actually run, risks, and unresolved blockers.
