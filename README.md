# Roblox Codex Game Studio Kit

[![V27 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v27-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v27-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V27.0.0 — Luau Intelligence and Architecture.** This is the complete cumulative V1-V27 toolkit. Only the current release is required.

[Open the V27 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v27.0.0).

## What's included

- **213 native Codex skills** for Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and monetization.
- V23-V24 sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- V25 durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution.
- V26 Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network testing, and evidence-based change review.
- V27 Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contract review, and Rojo project validation.
- Read-only architecture reports, official `luau-analyze` integration, and optional temporary Rojo builds.
- Cumulative Luau compilation, Rojo builds, regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V27 release, then open the cumulative package root in Codex.
2. Read `AGENTS.md` and `INDEX_V27.md`.
3. Initialize session continuity in the **actual game project folder**:

       python "C:\Path\To\roblox-codex-game-studio-kit-v27\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Check local tooling:

       python "C:\Path\To\roblox-codex-game-studio-kit-v27\v27\tools\v27.py" doctor --root "C:\Path\To\YourGame"

5. Generate an architecture report:

       python "C:\Path\To\roblox-codex-game-studio-kit-v27\v27\tools\v27.py" audit --root "C:\Path\To\YourGame"

6. Run the official Luau analyzer (requires `luau-analyze` installed on PATH):

       python "C:\Path\To\roblox-codex-game-studio-kit-v27\v27\tools\v27.py" typecheck --root "C:\Path\To\YourGame"

7. Validate a Rojo project (requires the Rojo CLI for `--build`):

       python "C:\Path\To\roblox-codex-game-studio-kit-v27\v27\tools\v27.py" rojo-check --root "C:\Path\To\YourGame" --build

V25 commands: `start`, `checkpoint`, `handoff`, `resume`, `status`, `verify`, and `recover`. V26 commands: `doctor`, `plan`, and `verify-plan`. V27 commands: `doctor`, `audit`, `typecheck`, and `rojo-check`.

## V27 analysis boundaries

The offline architecture report is a conservative text-based heuristic, not a full Luau parser or DataModel emulator. It resolves a subset of static `require(script.Parent...)` patterns, identifies possible dependency cycles and unreferenced modules, and inventories statically named remote calls. Check all findings against the actual source and Studio hierarchy.

Use `luau-analyze` for type checking and linting, and Roblox Studio Script Analysis for engine-aware diagnostics. The type checker mode is respected per project/file by default; strict-mode overrides are explicit. V27 does not mass-add `--!strict`, rewrite remotes, or remove modules.

Rojo validation checks the project JSON and path mappings. An optional build writes to a temporary directory and deletes the result. It does not live-sync to a Studio place or publish.

## Studio MCP and production boundaries

Roblox Studio's MCP server is local to the developer's machine. Connect only trusted clients and confirm the target Studio instance/place. GitHub Actions cannot automatically control the local Studio session.

Saving a modified place, publishing, production DataStore writes, and player-impacting Open Cloud operations require explicit human review and approval. Use least privilege and isolated test data.

## Growth principles

Maximize sustainable player value and discover viable opportunities—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Documentation

- V27 feature index: `INDEX_V27.md`
- V27 Luau analysis: `v27/docs/LUAU_STATIC_ANALYSIS.md`
- V27 dependency and remote contracts: `v27/docs/DEPENDENCY_AND_REMOTE_CONTRACTS.md`
- V27 Rojo validation: `v27/docs/ROJO_PROJECT_VALIDATION.md`
- V27 gradual strict typing: `v27/docs/STRICT_TYPING_MIGRATION.md`
- V26 Studio MCP workflow: `v26/docs/STUDIO_MCP_WORKFLOW.md`
- V25 session continuity guide: `v25/docs/SESSION_CONTINUITY.md`
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
