# Roblox Codex Game Studio Kit

[![V22 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v22-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v22-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V22.0.0 — Platform Monetization Readiness and Creator Economics.** This is the complete cumulative V1–V22 toolkit. Only the current release is required.

## What's included
- **196 native Codex skills** covering Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tooling, testing, performance, release engineering, and monetization.
- Five V22 specialists for Creator Rewards, Managed Pricing, subscription operations, creator-revenue portfolios, and monetization launch readiness.
- A local Luau scanner for likely hard-coded Robux prices and evidence of dynamic price, price-level, and subscription APIs.
- A subscription-contract schema and validator for recurring benefits, renewal/cancellation disclosures, server-confirmed entitlements, and idempotent period grants.
- V21 game-aware offer discovery, V20 production reliability, V19 evidence verification, and V18 workflow/fair-economy controls.

## Requirements
Python 3.13 is the supported CI runtime. Install dependencies from the package root:
```bash
python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
```

## Quick start
1. Extract the V22 package and open its root in Codex.
2. Read `AGENTS.md` and `INDEX_V22.md`.
3. Start substantial tasks with `$roblox-end-to-end-development-orchestrator`.
4. Inspect the project with `python v18/tools/v18.py doctor --root .`.
5. Run V21 discovery: `python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json`.
6. Audit price handling: `python v22/tools/v22.py audit-pricing --root . --output reports/v22-pricing-readiness.json`.
7. Validate a subscription declaration: `python v22/tools/v22.py validate-subscription-contract --root . --file v22/examples/subscription-contract.example.json`.
8. Complete the V22 launch gate and test live platform flows in an authorized Roblox environment.

## Monetization principles
Prioritize genuine player value, accurate dynamic pricing, clearly disclosed recurring benefits, and verified program eligibility. Keep Creator Rewards, player purchases, advertising, and marketplace earnings as distinct accounting streams. Never fabricate earnings or target individuals by spending history. V18's no-gambling rule remains mandatory.

## Validation boundaries
CI validates metadata, tests, schemas, routing, cumulative audits, checksums, and archives. It does not inspect a live Creator Dashboard or prove eligibility, Managed Pricing behavior, live purchases, subscriptions, or earnings. Mark unexecuted live checks NOT_RUN or BLOCKED.

## Documentation
The extracted package contains the V22 index and guides at `INDEX_V22.md`, `v22/INDEX_V22.md`, and:
- `v22/docs/PLATFORM_EARNINGS_AND_CREATOR_REWARDS.md`
- `v22/docs/MANAGED_PRICING_AND_SUBSCRIPTIONS.md`
- `v22/docs/LAUNCH_GATE_AND_EVIDENCE.md`

Earlier reference guides: [V21 discovery/player value](v21/docs/MONETIZATION_DISCOVERY_AND_PLAYER_VALUE.md), [V20 production reliability](v20/docs/PRODUCTION_RELIABILITY.md), [V19 testing/evidence](v19/docs/TESTING_AND_EVIDENCE.md), [V18 no-gambling/fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md), and [MIT License](LICENSE).

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
