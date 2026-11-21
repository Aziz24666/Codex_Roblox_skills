# Roblox Codex Game Studio Kit

[![V20 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v20-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v20-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V20.0.0 — Production Reliability and Live Operations.** This is the complete cumulative V1–V20 Roblox game-development toolkit for Codex. You only need the current V20 release; earlier versions do not need separate downloads.

## Download

The complete V1–V20 package will be attached to the [V20.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v20.0.0) as ZIP and TAR.XZ archives, with SHA-256 checksums after the V20 release workflow succeeds.

## What's included

- **185 native Codex skills** across Roblox architecture, Luau, gameplay systems, characters and avatars, UI/input/accessibility, multiplayer/networking, security, persistence, economy, procedural content, NPCs, Studio plugins/MCP, performance, testing, research, and release engineering.
- **Five V20 production specialists** for server authority, resilient player data and migrations, idempotent economy transactions, safe rollouts, and production observability/incident response.
- A machine-readable production contract with schema and example.
- A local Python CLI for static contract validation and deterministic V20 routing regressions.
- All V19 risk-based testing, static-analysis guidance, Studio multi-client workflows, routing benchmark, and evidence governance.
- All V18 workflow orchestration, shared contracts, approval gates, and mandatory no-gambling monetization policy.
- Versioned schemas, examples, documentation, regression tests, CI package audits, hierarchical SHA-256 manifests, and reproducible archive checks.

## Requirements

- **Python 3.13** is the supported and CI-validated runtime. The inherited package uses `tomllib`, included in Python 3.11 and later.
- From the extracted package root, install validation dependencies:

  ```bash
  python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
  ```

## Quick start with Codex

1. Download and extract the complete V20 ZIP.
2. Open the extracted package root in Codex.
3. Read `AGENTS.md` and `INDEX_V20.md`.
4. Start substantial work with `$roblox-end-to-end-development-orchestrator`.
5. Inspect the project with `python v18/tools/v18.py doctor --root .`.
6. Generate a risk-based verification plan with `python v19/tools/v19.py plan-tests --root . --task "..." `.
7. Validate the project's production architecture declarations:

   ```bash
   python v20/tools/v20.py validate-contract --root . --file path/to/production-contract.json
   ```

8. Run the applicable checks in their actual environments and record outcomes with V19 evidence rules.

## V20 commands

```bash
python v20/tools/v20.py evaluate-routing --root .
python v20/tools/v20.py validate-contract --root . --file v20/examples/production-contract.example.json
python v20/tools/v20.py verify --root .
```

The production contract validator checks declared controls and cross-field consistency. It does not connect to Roblox or prove that remote handlers, DataStores, receipts, feature flags, alerts, deployments, or rollback procedures work.

## Validation and evidence boundaries

GitHub Actions validates overlay metadata, Python regression tests, schemas, routing, production-contract declarations, cumulative package audits, SHA-256 manifests, and ZIP/TAR.XZ extraction integrity. It does **not** launch Roblox Studio. Studio playtests, multi-client runtime checks, device testing, performance profiling, live DataStore behavior, asset permissions, live purchase fulfillment, production telemetry, and release operations must be executed in their real authorized environments and recorded separately. Unexecuted checks must remain `NOT_RUN` or `BLOCKED`, not `PASS`.

## Maintainer documentation

- [V20 index](INDEX_V20.md)
- [Production reliability contract](v20/docs/PRODUCTION_RELIABILITY.md)
- [Server authority and player data](v20/docs/REMOTE_AUTHORITY_AND_DATA.md)
- [Live operations and rollouts](v20/docs/OPERATIONS_AND_ROLLOUTS.md)
- [V20.0.0 release notes](RELEASE_NOTES_V20.md)
- [V19 testing and evidence strategy](v19/docs/TESTING_AND_EVIDENCE.md)
- [V18 no-gambling and fair monetization policy](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
