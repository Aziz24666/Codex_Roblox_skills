# Roblox Codex Game Studio Kit

[![V31 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v31-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v31-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V31.0.0 — Privacy-Safe Analytics and LiveOps Health.** This is the complete cumulative V1-V31 toolkit with **228 native Codex skills**. Only the current release is required.

[Open the V31 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v31.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210 native Codex skills; V27 — 213 native Codex skills; V28 — 216 native Codex skills; V29 — 220 native Codex skills; V30 — 224 native Codex skills; V31 — 228 native Codex skills.

- **228 native Codex skills** across Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, procedural content, NPCs, Studio tools, testing, performance, release engineering, analytics, LiveOps, and sustainable monetization.
- **V31** adds a reviewed AnalyticsService custom-event catalog, bounded source audit for deprecated/client-side/uncatalogued analytics calls, privacy-oriented field rules, aggregate game-health guardrails, and LiveOps/experiment readiness skills.
- **V30** adds candidate-specific production release plans, environment-specific release gates, evidence-path and optional SHA-256 validation, manual approval records, rollback/backup readiness checks, and a bounded local configuration/credential-hygiene audit (224 native skills at V30).
- **V29** adds performance profiling, Luau hot-path review, memory and asset optimization, device-specific budgets, and measurement regression comparison (220 native skills at V29).
- **V28** adds server-authority and remote-contract review, rate-limit/idempotency signals, DataStore schema-migration review, and a synthetic/staging-only migration-manifest validator (216 native skills at V28).
- **V27** adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contract review, and Rojo project validation (213 native skills at V27).
- **V26** adds Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network test planning, and evidence-based change review (210 native skills at V26).
- **V25** adds durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution (207 native skills at V25).
- **V23-V24** add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V31 release, then open the cumulative package root in Codex.
2. Read `AGENTS.md` and `INDEX_V31.md`.
3. Initialize session continuity in the actual game project folder:

       python "C:\Path\To\roblox-codex-game-studio-kit-v31\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Run local V31 diagnostics:

       python "C:\Path\To\roblox-codex-game-studio-kit-v31\v31\tools\v31.py" doctor --root "C:\Path\To\YourGame"
       python "C:\Path\To\roblox-codex-game-studio-kit-v31\v31\tools\v31.py" validate-catalog --root "C:\Path\To\YourGame"
       python "C:\Path\To\roblox-codex-game-studio-kit-v31\v31\tools\v31.py" audit --root "C:\Path\To\YourGame" --catalog ".codex\analytics\event-catalog.json"

5. Evaluate an operator-supplied aggregate health snapshot against your project's predeclared guardrails:

       python "C:\Path\To\roblox-codex-game-studio-kit-v31\v31\tools\v31.py" evaluate-health --root "C:\Path\To\YourGame"

V25 commands: start, checkpoint, handoff, resume, status, verify, and recover. V26 commands: doctor, plan, and verify-plan. V27 commands: doctor, audit, typecheck, and rojo-check. V28 commands: doctor, audit, and validate-migration. V29 commands: doctor, audit, budget, compare, and report. V30 commands: doctor, plan, validate, and audit. V31 commands: doctor, validate-catalog, audit, and evaluate-health.

## V31 analytics and LiveOps boundaries

V31's AnalyticsService audit is static and local. It does not collect telemetry, execute Luau, authenticate dashboard setup, publish, or verify event delivery. Confirm the current Roblox Creator Hub API documentation before instrumenting; custom analytics events are server-side and are not sent from Studio. Static source findings are review leads, not proof.

The health evaluator consumes only supplied aggregate numeric snapshots, enforces a minimum sample size and freshness window, and never fills missing metrics with zero. It does not infer player behavior, score individual players, build spender profiles, or prescribe a retention/revenue target. A clear status means only that the supplied aggregate values meet the project's own thresholds.

LiveOps changes, experiments, feature flags, notifications, and production operations remain manually approved. Keep outcomes fixed and transparent, free progression worthwhile, and the game enjoyable without spending. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, coercive notifications, or individual-spender targeting.

## Earlier safeguards retained

Keep game-critical state authoritative on the server. Validate ownership, permissions, state, bounds, and request frequency. Keep DataStore migrations staged, backed up, versioned, idempotent, and tested with synthetic data. Treat static Luau findings as investigation leads; confirm performance with real Studio captures and representative hardware. Use V30 release dossiers before production changes.

## Documentation

- V31 feature index: INDEX_V31.md
- V31 analytics event governance: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v31/docs/ANALYTICS_EVENT_GOVERNANCE.md)
- V31 aggregate game health and LiveOps: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v31/docs/AGGREGATE_GAME_HEALTH_AND_LIVEOPS.md)
- V30 production release readiness: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v30/docs/PRODUCTION_RELEASE_READINESS.md)
- V29 performance engineering: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v29/docs/PERFORMANCE_ENGINEERING.md)
- V28 server authority and DataStore safety: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v28/INDEX_V28.md)
- V27 Luau and architecture: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v27/INDEX_V27.md)
- V26 Studio MCP workflow: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v26/docs/STUDIO_MCP_WORKFLOW.md)
- V25 session continuity: [documentation](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v25/docs/SESSION_CONTINUITY.md)
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
