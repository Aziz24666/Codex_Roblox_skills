# Roblox Codex Game Studio Kit

[![V29 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v29-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v29-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V29.0.0 — Performance Engineering and Optimization.** This is the complete cumulative V1-V29 toolkit. Only the current release is required.

[Open the V29 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v29.0.0).

## What's included

- **220 native Codex skills** across Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and sustainable monetization.
- V29 adds performance profiling, Luau hot-path review, memory and asset optimization, device-specific budgets, and measurement regression comparison.
- V28 adds server-authority and remote-contract review, rate-limit/idempotency signals, DataStore schema-migration review, and a synthetic/staging-only migration-manifest validator (**216 native Codex skills at V28**).
- V27 adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contract review, and Rojo project validation (**213 native Codex skills at V27**).
- V26 adds Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network test planning, and evidence-based change review (**210 native Codex skills at V26**).
- V25 adds durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution (**207 native Codex skills at V25**).
- V23-V24 add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V29 release, then open the cumulative package root in Codex.
2. Read AGENTS.md and INDEX_V29.md.
3. Initialize session continuity in the actual game project folder:

       python "C:\Path\To\roblox-codex-game-studio-kit-v29\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Run local V29 diagnostics:

       python "C:\Path\To\roblox-codex-game-studio-kit-v29\v29\tools\v29.py" doctor --root "C:\Path\To\YourGame"

5. Generate a read-only performance review:

       python "C:\Path\To\roblox-codex-game-studio-kit-v29\v29\tools\v29.py" audit --root "C:\Path\To\YourGame"

6. Validate device budgets and compare captures after recording actual measurements. See the V29 profiling guide.

V25 commands: start, checkpoint, handoff, resume, status, verify, and recover. V26 commands: doctor, plan, and verify-plan. V27 commands: doctor, audit, typecheck, and rojo-check. V28 commands: doctor, audit, and validate-migration. V29 commands: doctor, audit, budget, compare, and report.

## V29 performance evidence boundaries

V29's static scanner reads bounded local Luau text and flags patterns that deserve investigation. It is not a Luau parser or profiler and cannot measure FPS, frame time, memory, script CPU, replication, or load time. Confirm bottlenecks with Roblox Studio MicroProfiler, Script Profiler, Developer Console, and representative hardware.

The comparison tool reads developer-supplied JSON captures. It compares stated values; it does not verify capture authenticity, start Studio, connect to Roblox, or collect telemetry. GitHub Actions does not run live Studio profiling or device tests.

## V28 security and persistence boundaries

Treat client input as untrusted and keep game-critical state authoritative on the server. Validate ownership, permissions, state, bounds, and request frequency. Keep DataStore migrations staged, backed up, versioned, idempotent, and tested with synthetic data. Publishing, production DataStore writes, and player-impacting Open Cloud operations require explicit human approval.

## Growth principles

Maximize sustainable player value and discover viable opportunities—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Documentation

- V29 feature index: INDEX_V29.md
- V29 performance engineering: v29/docs/PERFORMANCE_ENGINEERING.md
- V29 device budgets: v29/docs/DEVICE_PERFORMANCE_BUDGETS.md
- V29 profiling and regression evidence: v29/docs/PROFILING_AND_REGRESSION_EVIDENCE.md
- V28 server authority and security: v28/INDEX_V28.md
- V27 Luau and architecture: v27/INDEX_V27.md
- V26 Studio MCP workflow: v26/docs/STUDIO_MCP_WORKFLOW.md
- V25 session continuity: v25/docs/SESSION_CONTINUITY.md
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
