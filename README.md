# Roblox Codex Game Studio Kit

[![V34 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v34-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v34-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V34.0.0 — Performance Soak Testing and Repeatable Benchmarks.** The complete cumulative V1-V34 toolkit contains **240 native Codex skills**. Only the current release is required.

[Open the V34 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v34.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210 native Codex skills; V27 — 213 native Codex skills; V28 — 216 native Codex skills; V29 — 220 native Codex skills; V30 — 224 native Codex skills; V31 — 228 native Codex skills; V32 — 232 native Codex skills; V33 — 236 native Codex skills; V34 — 240 native Codex skills.

- **240 native Codex skills** for Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio tools, testing, performance, release engineering, analytics, LiveOps, safety, moderation, and sustainable monetization.
- **V34** adds four performance skills, time-series soak capture validation, memory/instance growth analysis, at-least-three-run benchmark comparisons, matched-environment checks, and rollout monitoring guidance.
- **V33** adds four QA skills, Studio test orchestration guidance, multiplayer/device/input regression plans, bounded test-plan and run-report validators, regression comparison, and cumulative QA/package audits.
- **V32** adds four player-safety skills, a bounded static audit for custom text-filtering hazards, privacy-minimal moderation records, and human-review/appeal guidance.
- **V31** adds AnalyticsService event governance, bounded instrumentation auditing, privacy-safe aggregate health checks, and LiveOps/experiment readiness.
- **V30** adds production release plans, environment gates, evidence validation, approval records, rollback/backup readiness, and configuration hygiene.
- **V29** adds profiling, Luau hot-path review, memory/asset optimization, device budgets, and single-capture measurement comparisons.
- **V28** adds server-authority, remote-contract, DataStore migration, and multiplayer reliability checks.
- **V27** adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contracts, and Rojo validation.
- **V26** adds Studio MCP workflows for inspection/editing, multiplayer/device/network testing, and evidence-based change review.
- **V25** adds durable checkpoints, recoverable handoffs, backup recovery, journal integrity, project-root binding, and staged task execution.
- **V23-V24** add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V34 release, then open the extracted package root in Codex.
2. Read AGENTS.md and INDEX_V34.md.
3. Initialize session continuity in the actual game project folder:

       python C:\Path\To\roblox-codex-game-studio-kit-v34\v25\tools\v25.py start --root C:\Path\To\YourGame --goal "Build and ship my Roblox game"

4. Run V34 performance diagnostics:

       python C:\Path\To\roblox-codex-game-studio-kit-v34\v34\tools\v34.py doctor --root C:\Path\To\YourGame
       python C:\Path\To\roblox-codex-game-studio-kit-v34\v34\tools\v34.py validate-capture --root C:\Path\To\YourGame --capture .codex\perf\soak-run.json
       python C:\Path\To\roblox-codex-game-studio-kit-v34\v34\tools\v34.py analyze-soak --root C:\Path\To\YourGame --capture .codex\perf\soak-run.json --output .codex\reports\v34-soak-analysis.json
       python C:\Path\To\roblox-codex-game-studio-kit-v34\v34\tools\v34.py validate-suite --root C:\Path\To\YourGame --manifest .codex\perf\repeat-suite.json
       python C:\Path\To\roblox-codex-game-studio-kit-v34\v34\tools\v34.py compare-repeated --root C:\Path\To\YourGame --manifest .codex\perf\repeat-suite.json --output .codex\reports\v34-repeated-comparison.json

V25 commands: start, checkpoint, handoff, resume, status, verify, recover. V26: doctor, plan, verify-plan. V27: doctor, audit, typecheck, rojo-check. V28: doctor, audit, validate-migration. V29: doctor, audit, budget, compare, report. V30: doctor, plan, validate, audit. V31: doctor, validate-catalog, audit, evaluate-health. V32: doctor, audit, validate-policy, validate-case, validate-register. V33: doctor, audit, validate-plan, validate-report, compare. V34: doctor, validate-capture, analyze-soak, validate-suite, compare-repeated.

## V34 performance evidence boundaries

V34 validates supplied, structured aggregate captures and computes trend/repeated-run summaries. It does not launch Roblox Studio, capture MicroProfiler dumps, execute Luau, access Creator Dashboard, read live telemetry, or modify release settings. Detailed evidence stays in authorized project storage and is referenced by opaque IDs.

A memory-growth signal is not proof of a memory leak. A repeated benchmark regression is a review signal, not automatic proof of causality. Use consistent conditions, review every run, and apply project-specific budgets. Current Creator Hub Performance Dashboard charts are activity-dependent; record unavailable data as unavailable rather than fabricating estimates.

## V33 QA verification boundaries

V33's Python tools are offline. They validate structured test plans and reports, compare supplied baseline/current results, and inventory Luau files. They do not launch Roblox Studio, execute Luau, simulate multiplayer, emulate devices, inject input, or contact Roblox services. A passing GitHub Actions workflow verifies the checks run in CI; it does not prove that Studio tests passed.

Use Roblox Studio's Test/Run, Server & Clients, Device Simulator, Controller Emulator, Network Simulator, and supported Studio-only test services for actual playtesting. Every planned test must be recorded as passed, failed, blocked, or not_run. Blocked and not_run are not passes. Use opaque evidence references and do not put player IDs, usernames, raw chat, credentials, or private logs into QA reports.

## V32 player-safety boundaries

Custom non-chat text visible to other players must follow Roblox's current server-side TextService filtering guidance. If filtering fails, do not display the submitted text. Prefer native TextChatService for chat. Moderation decisions must be human-reviewed and appealable; no sanctions are generated by report counts or static findings.

## Earlier safeguards retained

Keep game-critical state authoritative on the server, validate remote arguments, and protect persistence. Use evidence-backed profiling and release dossiers. Keep analytics aggregate and purpose-bound; do not build individual-spender profiles. Keep paid outcomes fixed and disclosed, worthwhile free progression, and the mandatory no-gambling policy.

## Documentation

- V34 feature index: INDEX_V34.md
- [Performance soak testing](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v34/docs/PERFORMANCE_SOAK_TESTING.md)
- [MicroProfiler and Dashboard evidence](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v34/docs/MICROPROFILER_AND_DASHBOARD_EVIDENCE.md)
- [Repeated benchmarks and rollout](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/v34/docs/REPEATED_BENCHMARKS_AND_ROLLOUT.md)
- [V33 automated testing and regression](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/INDEX_V33.md)
- [V32 text filtering, moderation, and appeals](https://github.com/Aziz24666/Codex_Roblox_skills/blob/main/INDEX_V32.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
