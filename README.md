# Roblox Codex Game Studio Kit

[![V21 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v21-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v21-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V21.0.0 — Game-aware Monetization Discovery and Sustainable Revenue.** This is the complete cumulative V1–V21 Roblox game-development toolkit for Codex. You only need the current V21 release; earlier versions do not need separate downloads.

## Download

The complete V1–V21 package will be attached to the [V21.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v21.0.0) as ZIP and TAR.XZ archives, with SHA-256 checksums after the V21 release workflow succeeds.

## What's included

- **191 native Codex skills** covering Roblox architecture, Luau, gameplay systems, characters and avatars, UI/input/accessibility, multiplayer/networking, security, persistence, economy, procedural content, NPCs, Studio plugins/MCP, performance, testing, research, and release engineering.
- **Six V21 monetization specialists** for game-aware discovery, product strategy, pricing experiments, purchase integrity, aggregate revenue analytics, and storefront UX/policy.
- A local Python CLI that scans readable project files, records evidence, ranks suitable direct-purchase ideas, and optionally analyzes aggregate store metrics.
- All V20 production reliability, V19 verification/evidence, and V18 workflow orchestration and fair economy controls.
- Versioned schemas, examples, documentation, regression tests, CI package audits, hierarchical SHA-256 manifests, and reproducible archive checks.

## Requirements

- **Python 3.13** is the supported and CI-validated runtime.
- Install validation dependencies from the extracted package root:

  ```bash
  python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
  ```

## Quick start with Codex

1. Download and extract the complete V21 ZIP.
2. Open the extracted package root in Codex.
3. Read `AGENTS.md` and `INDEX_V21.md`.
4. Start substantial work with `$roblox-end-to-end-development-orchestrator`.
5. Inspect the project with `python v18/tools/v18.py doctor --root .`.
6. Run automatic game-aware monetization discovery:

   ```bash
   python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json
   ```

7. Review the evidence-ranked offers with the V21 specialists. Add aggregate metrics only when available:

   ```bash
   python v21/tools/v21.py discover --root . --metrics-file reports/aggregate-metrics.json --output reports/monetization-discovery.json
   ```

8. Validate the report with `python v21/tools/v21.py validate-report --root . --file reports/monetization-discovery.json`.
9. Generate risk-based tests with V19 and run applicable checks in real authorized Roblox environments.

## V21 monetization principles

V21 ranks offers by evidence-backed game fit and player value. Fit is not a revenue forecast. It supports deterministic, clearly described products and privacy-safe aggregate measurement. V18's no-gambling and fair monetization rules remain mandatory; V21 does not add gambling or paid chance mechanics.

## Validation and evidence boundaries

GitHub Actions validates overlay metadata, Python tests, schemas, routing, cumulative package audits, SHA-256 manifests, and ZIP/TAR.XZ extraction integrity. It does **not** launch Roblox Studio, inspect a live game, verify Creator Dashboard configuration, prove live purchase fulfillment, or validate production analytics. Unexecuted runtime checks must remain `NOT_RUN` or `BLOCKED`, not `PASS`.

## Maintainer documentation

- [V21 index](INDEX_V21.md)
- [V21 monetization discovery and player value](v21/docs/MONETIZATION_DISCOVERY_AND_PLAYER_VALUE.md)
- [V21 offer selection and experiments](v21/docs/OFFER_SELECTION_AND_EXPERIMENTS.md)
- [V20 production reliability](v20/docs/PRODUCTION_RELIABILITY.md)
- [V19 testing and evidence strategy](v19/docs/TESTING_AND_EVIDENCE.md)
- [V18 no-gambling and fair monetization policy](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
