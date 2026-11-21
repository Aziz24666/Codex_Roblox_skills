# V21 Overlay Index

## Six specialist skills

- `roblox-game-aware-monetization-discovery` — evidence-backed project scanning and offer discovery.
- `roblox-monetization-product-strategy` — selects product families based on genuine game/player value.
- `roblox-monetization-experiment-and-pricing` — controlled price and storefront experiments with player-trust guardrails.
- `roblox-monetization-purchase-integrity` — server-owned catalogs, exact grants, receipts, and entitlement reconciliation.
- `roblob-monetization-analytics-and-revenue-modeling` — privacy-safe aggregate metrics and evidence-based revenue analysis.
- `roblox-monetization-storefront-ux-and-policy` — accurate disclosures, accessibility, and current policy review.

## Tools

- `tools/v21.py discover` scans a project and writes a ranked evidence report.
- `tools/v21.py validate-report` validates a report against the V21 schema.
- `tools/v21.py evaluate-routing` evaluates six deterministic routing regressions.
- `tools/v21.py verify` runs inherited verification, V21 checks, and the cumulative package audit.
- `tools/patch_cumulative_package.py` integrates V21 into a verified V20 cumulative package and regenerates checksum manifests.

## Limitations

The scanner does not connect to Roblox Studio, inspect live services, infer sales, or guarantee revenue. Roblox runtime purchase, DataStore, telemetry, and UI behavior must be tested in real authorized environments.
