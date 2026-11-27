# Roblox Codex Game Studio Kit

[![V35 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v35-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v35-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V35.0.0 — Asset Pipeline Governance and Content Validation.** The complete cumulative V1-V35 toolkit contains **244 native Codex skills**. Only the current release is required.

[Open the V35 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v35.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210 native Codex skills; V27 — 213 native Codex skills; V28 — 216 native Codex skills; V29 — 220 native Codex skills; V30 — 224 native Codex skills; V31 — 228 native Codex skills; V32 — 232 native Codex skills; V33 — 236 native Codex skills; V34 — 240 native Codex skills; V35 — 244 native Codex skills.

- **244 native Codex skills** for Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio tools, testing, performance, release engineering, analytics, LiveOps, safety, moderation, sustainable monetization, and asset production.
- **V35** adds an asset catalog, provenance/review tracking, dependency-graph validation, per-device content budgets, and catalog migration comparison.
- **V34** adds long-session performance soak analysis, profiler evidence triage, repeated benchmark comparisons, and rollout monitoring.
- **V33** adds automated QA plans/reports, Studio test orchestration guidance, device/input/multiplayer regression, and regression comparison.
- **V32** adds player-safety guidance, bounded static review for custom text filtering, privacy-minimal moderation records, and human-review/appeal workflows.
- **V31** adds AnalyticsService event governance, instrumentation auditing, privacy-safe aggregate health checks, and LiveOps readiness.
- **V30** adds production release plans, environment gates, evidence validation, approval records, rollback/backup readiness, and configuration hygiene.
- **V29** adds profiling, Luau hot-path review, memory/asset optimization, device budgets, and single-capture measurement comparisons.
- **V28** adds server-authority, remote-contract, DataStore migration, and multiplayer reliability checks.
- **V27** adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contracts, and Rojo validation.
- **V26** adds Studio MCP workflows for inspection/editing, multiplayer/device/network testing, and evidence-based change review.
- **V25** adds durable checkpoints, recoverable handoffs, backup recovery, journal integrity, project-root binding, and staged task execution.
- **V23-V24** add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V35 release, then open the extracted package root in Codex.
2. Read AGENTS.md and INDEX_V35.md.
3. Initialize session continuity in the actual game project folder:

       python C:\Path\To\roblox-codex-game-studio-kit-v35\v25\tools\v25.py start --root C:\Path\To\YourGame --goal "Build and ship my Roblox game"

4. Run V35 asset checks:

       python C:\Path\To\roblox-codex-game-studio-kit-v35\v35\tools\v35.py doctor --root C:\Path\To\YourGame
       python C:\Path\To\roblox-codex-game-studio-kit-v35\v35\tools\v35.py validate-catalog --root C:\Path\To\YourGame --catalog .codex\assets\catalog.json
       python C:\Path\To\roblox-codex-game-studio-kit-v35\v35\tools\v35.py audit-catalog --root C:\Path\To\YourGame --catalog .codex\assets\catalog.json --policy .codex\assets\budget-policy.json --output .codex\reports\v35-asset-audit.json
       python C:\Path\To\roblox-codex-game-studio-kit-v35\v35\tools\v35.py compare-catalogs --root C:\Path\To\YourGame --baseline .codex\assets\catalog-v1.json --candidate .codex\assets\catalog-v2.json --output .codex\reports\v35-asset-diff.json

V25 commands: start, checkpoint, handoff, resume, status, verify, recover. V26: doctor, plan, verify-plan. V27: doctor, audit, typecheck, rojo-check. V28: doctor, audit, validate-migration. V29: doctor, audit, budget, compare, report. V30: doctor, plan, validate, audit. V31: doctor, validate-catalog, audit, evaluate-health. V32: doctor, audit, validate-policy, validate-case, validate-register. V33: doctor, audit, validate-plan, validate-report, compare. V34: doctor, validate-capture, analyze-soak, validate-suite, compare-repeated. V35: doctor, validate-catalog, audit-catalog, compare-catalogs.

## V35 content governance boundaries

The CLI validates supplied metadata and project-local source paths only. It does not inspect binary asset content, query Roblox, access Creator Store/private inventories, upload/publish/delete/transfer assets, or determine copyright, license scope, or moderation approval. Rights and moderation states must be verified and maintained by authorized humans. Device budgets are project-specific values and must be calibrated with actual Studio/device testing.

## Earlier verification boundaries and safeguards

V34 performance reports process supplied structured evidence only; they do not launch Studio, capture MicroProfiler dumps, execute Luau, access Creator Dashboard, or read live telemetry. A memory-growth signal is not proof of a leak.

V33 test plans and reports are offline; they do not launch Studio, simulate multiplayer, emulate devices, or inject input. A GitHub Actions pass does not prove Studio playtests passed.

Custom non-chat text visible to other players must follow Roblox's current server-side TextService filtering guidance. Moderation decisions must be human-reviewed and appealable. Keep game-critical state authoritative on the server, validate remote arguments, and protect persistence.

Keep analytics aggregate and purpose-bound; do not build individual-spender profiles. Keep paid outcomes fixed and disclosed, provide worthwhile free progression, and preserve the mandatory no-gambling policy.

## Documentation

- V35 feature index: INDEX_V35.md
- Asset catalog and provenance: v35/docs/ASSET_CATALOG_AND_PROVENANCE.md
- Content budgets and dependencies: v35/docs/CONTENT_BUDGETS_AND_DEPENDENCIES.md
- Asset release and migration: v35/docs/ASSET_RELEASE_AND_MIGRATION.md
- V34 performance soak testing: INDEX_V34.md
- V33 automated testing and regression: INDEX_V33.md
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
