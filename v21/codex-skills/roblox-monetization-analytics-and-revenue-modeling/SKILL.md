---
name: roblox-monetization-analytics-and-revenue-modeling
description: Measure aggregate Roblox store performance and compare offers using observed, privacy-safe metrics.
---

# Monetization analytics and revenue modeling

Use only aggregate, privacy-safe event data. Never require player names, account IDs, chat logs, or sensitive personal traits.

## Metrics
- Shop open rate = unique shop viewers / eligible shop impressions.
- Purchase conversion = unique purchasers / unique shop viewers.
- Payer conversion = unique payers / unique active users in the same period.
- ARPPU = recognized Robux revenue / unique payers.
- ARPDAU = recognized Robux revenue / daily active users.
- Offer yield = gross Robux / eligible offer impressions.
- Repeat purchase rate = payers with more than one completed transaction / unique payers, only for repeatable products.

Validate event completeness, deduplication, time window, currency, refunds, and denominators. Missing or zero-denominator values must be reported as unavailable, never guessed.

## Offer comparison
Compare offers using matching event definitions and windows. Rank observed historical Robux per eligible impression descriptively, flag small samples, and never infer causality from a simple ranking. Include retention, refunds, support contacts, and sentiment as guardrails. A scenario is not a forecast.

## Privacy and fairness
Never target or rank individual players by vulnerability, age, location, device, or sensitive traits. Optimize player value and sustainable aggregate outcomes, not pressure on individual spenders.

## Output
Provide metric definitions, dataset window, formulas, source fields, observed values, sample-size warnings, uncertainty, limitations, and next instrumentation changes. Never fabricate revenue, conversion, or lift.

## V18 shared workflow and handoff contract
Preserve shared workflow and the mandatory no-gambling economy policy.

## V19 verification and evaluation contract
Record metric lineage, test evidence, and data-quality gaps.

## V20 production reliability contract
Keep telemetry actionable and redact secrets and unnecessary personal data.

## V21 sustainable monetization contract
Use aggregate outcomes to improve product value and sustainability, never to pressure individual players.
