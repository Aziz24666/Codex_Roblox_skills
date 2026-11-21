# V20 Overlay Index

V20 adds five production reliability specialists, a production contract schema and example, a CLI validator, and five deterministic routing regression cases.

## Source specialists
- `roblox-server-authority-and-remote-boundaries`
- `roblox-player-data-resilience-and-migrations`
- `roblox-idempotent-economy-transactions`
- `roblox-live-operations-and-safe-rollouts`
- `roblox-production-observability-and-incident-response`

## Tools
- `tools/v20.py` — validates project production declarations, evaluates routing, and runs cumulative V19/V20 verification.
- `tools/validate_v20_overlay.py` — checks V20 source files, skill contracts, schema, and routing corpus.
- `tools/patch_cumulative_package.py` — upgrades a verified V19 package and regenerates V20 manifests.
- `tools/audit_cumulative_package.py` — verifies the 185-skill cumulative tree, source/install parity, schemas, routing report, production contract, and checksum hierarchy.

## Evidence boundaries
All checks requiring Roblox Studio, live DataStores, real MarketplaceService receipts, production dashboards, deployments, and rollback operations must be executed in their real authorized environments. Static validation does not prove live behavior.
