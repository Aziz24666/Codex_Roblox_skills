# V21 — Game-aware monetization discovery and player value

## Purpose
V21 adds an evidence-first workflow for finding optional purchase opportunities that fit the actual game. It is designed to improve sustainable, long-term revenue by making offers more relevant and more valuable—not by pressuring players or degrading the free experience.

## How automatic discovery works

`python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json` scans readable source and design files in the selected project. It detects genre and system signals, records file/line evidence, and ranks a small set of deterministic product ideas. The Codex skills then inspect the actual design and implementation to decide whether each idea is appropriate.

The scanner is deliberately conservative:
- It excludes generated folders, dependencies, previous toolkit overlays, and binary assets.
- It has file-count and file-size limits.
- It does not connect to Roblox Studio, inspect a live experience, read analytics dashboards, or infer player demand.
- A match is evidence to review, not proof that a feature exists or should be sold.
- It reports fit and confidence, not a money forecast.

## Recommended purchase families

Offer families are conditional on evidence in the game and must be adapted to the actual experience:
- Fixed-price cosmetics, appearance catalogs, emotes, and visual customization.
- Clearly specified permanent passes.
- Exact-quantity developer products where a repeat purchase provides a genuine optional benefit.
- Time-limited benefits only when the effect and duration are exact and known before purchase.
- Subscriptions only when the team can deliver the promised recurring benefits reliably.
- Private servers only when private play is meaningful for that experience.

Do not add offers merely to fill a catalog. A feature with weak player value, no supporting game system, high fairness risk, or unclear delivery should be rejected or postponed.

## Ranking model

The CLI's `fit_score` is a deterministic heuristic based on matched project evidence. It is not expected revenue, conversion probability, user willingness to pay, or a substitute for playtesting. Confidence expresses evidence density, not commercial certainty. The Codex analysis must also assess player value, implementation/maintenance cost, accessibility, economy balance, and free progression.

## Evidence needed for revenue estimates

The CLI does not estimate Robux from source code. To calculate aggregate funnel metrics, provide a validated metrics JSON file:

`python v21/tools/v21.py discover --root . --metrics-file reports/aggregate-metrics.json --output reports/monetization-discovery.json`

The file must use `v21/schemas/aggregate-monetization-metrics.schema.json`. It must contain only aggregate values over a defined period. Optional `offer_performance` rows compare observed offers using gross Robux per eligible impression, with low-sample labels; this is descriptive, not a causal result or forecast. Do not include usernames, account IDs, chat logs, or sensitive player attributes.

## Player-first requirements

- Keep the core loop fun and completable without spending.
- Make benefits, total price, quantity, duration, recurrence, and limitations clear before a purchase prompt.
- Avoid false scarcity, fake timers, misleading discounts, pressure copy, repeated interruptions, and hidden costs.
- Preserve server authority and exact grants through V20 transaction rules.
- Review current Roblox platform documentation for the exact purchase type before shipping.
- The V18 no-gambling policy remains mandatory. V21 does not add gambling or paid chance mechanics.

## Official platform research

Re-check the current Roblox Creator Hub pages for passes, developer products, subscriptions, monetization, and price optimization. Confirm availability and configuration in Creator Dashboard; do not assume a feature is enabled merely because platform documentation describes it.
