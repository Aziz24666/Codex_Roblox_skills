# V21 Overlay

V21 adds six specialists for game-aware monetization discovery, product strategy, pricing experiments, purchase integrity, aggregate analytics, and storefront UX/policy.

## Commands

```bash
python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json
python v21/tools/v21.py discover --root . --metrics-file reports/aggregate-metrics.json --output reports/monetization-discovery.json
python v21/tools/v21.py validate-report --root . --file reports/monetization-discovery.json
python v21/tools/v21.py evaluate-routing --root .
python v21/tools/v21.py verify --root .
```

The discovery scanner examines readable files in the project root, excluding generated/dependency folders and prior toolkit overlays. It does not inspect live Roblox services or binary place files. Fit scores are not revenue forecasts. Actual monetization decisions require human review, real aggregate data, current platform-policy research, and runtime tests.
