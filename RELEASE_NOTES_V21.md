# V21.0.0 — Game-aware monetization discovery and sustainable revenue

**Release:** `v21.0.0`  
**Type:** Feature release  
**Base:** V20.0.0  
**License:** MIT

V21 extends the cumulative Roblox Codex Game Studio Kit with six monetization specialists, a local project-scanning CLI, validated discovery and aggregate-metrics schemas, routing regressions, and a cumulative release audit.

## What's new

- **Game-aware discovery:** inspects readable source and design files, records file/line evidence, detects game mechanics, and ranks optional purchase ideas by game fit.
- **Product strategy:** maps actual player value to fixed cosmetics, passes, deterministic products, subscriptions with ongoing delivered benefits, and private servers where suitable.
- **Experimentation:** plans controlled pricing/storefront experiments with retention, refund, sample-size, and player-trust guardrails.
- **Purchase integrity:** reinforces server-owned catalogs, verified receipts, exact grants, idempotent delivery, and entitlement reconciliation.
- **Aggregate analytics:** calculates store funnel and revenue measures only from supplied, validated aggregate data; reports missing denominators instead of guessing.
- **Storefront UX and policy:** requires exact descriptions, transparent prices/durations, accessible interfaces, and optional purchases.

## Hard policy

V18's no-gambling and fair-monetization policy remains mandatory. V21 does not add gambling, paid random rewards, or paid modifiers to random odds. Any paid temporary benefit must have a fixed, known effect and duration disclosed before purchase.

## Run

```bash
python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json
python v21/tools/v21.py discover --root . --metrics-file reports/aggregate-metrics.json --output reports/monetization-discovery.json
python v21/tools/v21.py validate-report --root . --file reports/monetization-discovery.json
python v21/tools/v21.py evaluate-routing --root .
python v21/tools/v21.py verify --root .
```

## Evidence boundaries

The scanner reads local text files; it does not connect to Roblox Studio, inspect live services or Creator Dashboard analytics, or verify live purchases. Fit scores are heuristics, not revenue forecasts. Roblox runtime purchase, persistence, analytics, and UI behavior must be tested in an authorized Roblox test environment.
