# V23 — Monetization Opportunity Discovery and Sustainable Growth

V23 adds a broad, evidence-based monetization opportunity finder and five specialists for opportunity discovery, healthy engagement, store discovery, revenue analytics, and growth compliance.

## Commands
~~~bash
python v23/tools/v23.py discover-opportunities --root . --output reports/v23-opportunities.json
python v23/tools/v23.py evaluate-routing --root .
python v23/tools/v23.py verify --root .
~~~

The catalogue contains 48 deterministic routes across cosmetics, content, convenience, consumables, subscriptions, social features, private servers, Creator Rewards, ads, avatar items, and Creator Store products. The scanner reports every catalogue entry, ranks evidence-supported matches, and includes source paths and line numbers. A keyword match is not proof of demand or expected Robux.

The output separates in-experience purchases, Roblox-funded programs, advertising, and creator marketplace sales. The tool cannot inspect live Creator Dashboard eligibility, player analytics, or actual earnings.

## Growth rules
- Discover the widest set of opportunities, then implement only those supported by the actual game and player value.
- Keep purchased rewards deterministic, fixed, and disclosed. The V18 no-gambling rule remains absolute.
- Keep the core game enjoyable and completable without Robux.
- Improve retention through fun, stable, accessible, social, replayable content—not artificial playtime or forced attendance.
- Use Roblox product-intelligence APIs only within current rate limits; do not profile or target players by spending history.
- Do not use fake scarcity, misleading discounts, countdown pressure, hidden costs, forced ads, or purchase interruptions.
- Never invent Robux forecasts. A fit score is not revenue probability.

See the revenue opportunity playbook and engagement/store optimization guide in v23/docs.
