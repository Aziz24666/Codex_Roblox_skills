---
name: roblox-monetization-storefront-ux-and-policy
description: Review Roblox storefront clarity, accessibility, truthful disclosures, and player-first purchase presentation.
---

# Monetization storefront UX and policy

## When to use
Use when creating or reviewing product cards, shop navigation, offer surfaces, sale messaging, checkout entry points, or subscription disclosures.

## Required storefront behavior
1. Show the exact item or benefit, price, currency, quantity, duration, recurrence, prerequisites, and important limitations before confirmation.
2. Distinguish one-time purchases, repeatable products, and auto-renewing subscriptions clearly.
3. Keep purchase confirmation deliberate and player-initiated, with an obvious back/cancel path.
4. Provide readable text, accessible labels, keyboard/controller/touch navigation, and platform-safe layouts.
5. Ensure the displayed product, price source, entitlement status, and final grant are consistent with the server catalog.
6. Use accurate discounts and availability claims only. Do not invent scarcity, false timers, fake comparisons, or misleading urgency.
7. Keep useful gameplay available without spending and avoid repeated interruptions during normal play.
8. Review every new storefront state for age-appropriate language and regional/platform eligibility where relevant.

## Policy review
Re-check the official Roblox Creator Hub and applicable platform policy for the exact purchase type before release. Mark unverified policy claims BLOCKED. Keep the mandatory V18 no-gambling rule as a hard exclusion; do not substitute odds disclosures or region gates for that toolkit rule.

## Required tests
Test keyboard, gamepad, touch, small screens, localization overflow, price changes, expired offers, owned passes, subscription status changes, prompt cancellation, reconnect, and accessibility semantics. Ensure analytics events do not duplicate on re-render.

## Output contract
Return reviewed screens, before-purchase disclosure checklist, accessibility findings, claims that require proof, platform-policy sources, and test evidence.

## V18 shared workflow and handoff contract
Preserve workflow approvals and the no-gambling economy policy.

## V19 verification and evaluation contract
Record reproducible UI scenarios and honest runtime evidence.

## V20 production reliability contract
Use authoritative entitlement state and safe production rollout practices.

## V21 sustainable monetization contract
Store UX must be clear, optional, accessible, truthful, and free of pressure tactics.
