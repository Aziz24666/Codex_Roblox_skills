# Roblox Codex Game Studio Kit

[![V36 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v36-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v36-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V36.0.0 — Accessibility, Responsive UI, and Localization Readiness.** The complete cumulative V1-V36 toolkit contains **248 native Codex skills**. Only the current release is required.

[Open the V36 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v36.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210; V27 — 213; V28 — 216; V29 — 220; V30 — 224; V31 — 228; V32 — 232; V33 — 236; V34 — 240; V35 — 244; V36 — 248.

- **248 native Codex skills** for Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio tools, testing, performance, release engineering, analytics, LiveOps, safety, moderation, sustainable monetization, asset production, accessibility, and localization.
- **V36** adds accessibility and inclusive interaction reviews, responsive UI/readability, localization/RTL readiness, sensory alternatives and reduced-motion guidance, plus an offline quality manifest validator/auditor.
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

1. Download and extract the V36 release, then open the extracted package root in Codex.
2. Read AGENTS.md and INDEX_V36.md.
3. Initialize session continuity in the actual game project folder:

       python C:\Path\To\roblox-codex-game-studio-kit-v36\v25\tools\v25.py start --root C:\Path\To\YourGame --goal "Build and ship my Roblox game"

4. Run V36 quality checks:

       python .\v36\tools\v36.py doctor --root C:\Path\To\YourGame
       python .\v36\tools\v36.py validate-manifest --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json
       python .\v36\tools\v36.py audit --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json --output .codex\reports\v36-quality-audit.json

Copy the example manifest from v36/examples/ and replace its illustrative values with reviewed project data before use.

V25 commands: start, checkpoint, handoff, resume, status, verify, recover. V26: doctor, plan, verify-plan. V27: doctor, audit, typecheck, rojo-check. V28: doctor, audit, validate-migration. V29: doctor, audit, budget, compare, report. V30: doctor, plan, validate, audit. V31: doctor, validate-catalog, audit-catalog, evaluate-health. V32: doctor, audit, validate-policy, validate-case, validate-register. V33: doctor, audit, validate-plan, validate-report, compare. V34: doctor, validate-capture, analyze-soak, validate-suite, compare-repeated. V35: doctor, validate-catalog, audit-catalog, compare-catalogs. V36: doctor, validate-manifest, audit.

## V36 quality review boundaries

The V36 CLI validates supplied metadata only. It does not inspect Roblox Studio UI instances, analyze screenshots, execute Luau, test real devices, or certify accessibility. Contrast, navigation, captions, reduced-motion behavior, text scaling, localization, and RTL behavior require human review and actual target-device testing. The manifest uses opaque evidence references and must not contain player health information, personal data, credentials, private URLs, or free-form player profiles.

## Earlier verification boundaries and safeguards

V35 catalog commands validate supplied metadata and project-local source paths only. They do not inspect binary asset content, query Roblox, access Creator Store/private inventories, upload/publish/delete/transfer assets, or determine copyright, license scope, or moderation approval. Rights and moderation states must be verified and maintained by authorized humans. Device budgets are project-specific and must be calibrated with actual Studio/device testing.

V34 performance reports process supplied structured evidence only; they do not launch Studio, capture MicroProfiler dumps, execute Luau, access Creator Dashboard, or read live telemetry. A memory-growth signal is not proof of a leak.

V33 test plans and reports are offline; they do not launch Studio, simulate multiplayer, emulate devices, or inject input. A GitHub Actions pass does not prove Studio playtests passed.

Custom non-chat text visible to other players must follow Roblox's current server-side TextService filtering guidance. Moderation decisions must be human-reviewed and appealable. Keep game-critical state authoritative on the server, validate remote arguments, and protect persistence.

Keep analytics aggregate and purpose-bound; do not build individual-spender profiles. Keep paid outcomes fixed and disclosed, provide worthwhile free progression, and preserve the mandatory no-gambling policy.

## Documentation

- V36 feature index: INDEX_V36.md
- Accessibility and interaction review: v36/docs/ACCESSIBILITY_AND_INTERACTION_REVIEW.md
- Localization and responsive UI: v36/docs/LOCALIZATION_AND_RESPONSIVE_UI.md
- Quality manifest and audit: v36/docs/QUALITY_MANIFEST_AND_AUDIT.md
- V35 feature index: INDEX_V35.md
- Asset catalog and provenance: v35/docs/ASSET_CATALOG_AND_PROVENANCE.md
- Content budgets and dependencies: v35/docs/CONTENT_BUDGETS_AND_DEPENDENCIES.md
- Asset release and migration: v35/docs/ASSET_RELEASE_AND_MIGRATION.md
- V34 performance soak testing: INDEX_V34.md
- V33 automated testing and regression: INDEX_V33.md
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
