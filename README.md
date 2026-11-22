# Roblox Codex Game Studio Kit

[![V28 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v28-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v28-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V28.0.0 — Server Authority, DataStore Safety, and Multiplayer Reliability.** This is the complete cumulative V1-V28 toolkit. Only the current release is required.

[Open the V28 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v28.0.0).

## What's included

- **216 native Codex skills** for Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and sustainable monetization.
- V23-V24 sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- V25 durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution (**207 native Codex skills at V25**).
- V26 Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network testing, and evidence-based change review (**210 native Codex skills at V26**).
- V27 Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contract review, and Rojo project validation (**213 native Codex skills at V27**).
- V28 adds server-authority and remote-contract review, rate-limit/idempotency signals, DataStore API and schema-migration review, and a synthetic/staging-only migration-manifest validator.
- Read-only architecture and security reports, official luau-analyze integration, optional temporary Rojo builds, and safe migration-plan validation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V28 release, then open the cumulative package root in Codex.
2. Read AGENTS.md and INDEX_V28.md.
3. Initialize session continuity in the **actual game project folder**:

       python "C:\Path\To\roblox-codex-game-studio-kit-v28\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Run the V28 local project check:

       python "C:\Path\To\roblox-codex-game-studio-kit-v28\v28\tools\v28.py" doctor --root "C:\Path\To\YourGame"

5. Generate the read-only security and persistence review:

       python "C:\Path\To\roblox-codex-game-studio-kit-v28\v28\tools\v28.py" audit --root "C:\Path\To\YourGame"

6. Validate a human-authored migration manifest (see v28/tools/manifest-example.json):

       python "C:\Path\To\roblox-codex-game-studio-kit-v28\v28\tools\v28.py" validate-migration --root "C:\Path\To\YourGame" --manifest ".codex\migration-plan.json"

V25 commands: start, checkpoint, handoff, resume, status, verify, and recover. V26 commands: doctor, plan, and verify-plan. V27 commands: doctor, audit, typecheck, and rojo-check. V28 commands: doctor, audit, and validate-migration.

## V28 analysis boundaries

The V28 scanner reads local Luau text only. It inventories statically named remote calls and server handler patterns, searches a bounded area near handlers for validation, ownership, rate-limit, and idempotency signals, and records DataStore API calls and nearby migration/retry/backup indicators. It is a conservative heuristic, not a Luau parser, control-flow analyzer, DataModel emulator, security proof, or penetration test. Verify every finding against the full scripts and actual Studio hierarchy.

The migration-manifest command checks that a plan is explicitly synthetic/staging-only, dry-run, non-production-writing, sequential, idempotent, backed up, rollback-planned, and covered by valid/invalid/legacy/repeat cases. It validates structure only: it never executes migrations, connects to Roblox, touches DataStores, or calls Open Cloud.

## Studio MCP and production boundaries

Roblox Studio's MCP server is local to the developer's machine. Connect only trusted clients and confirm the target Studio instance/place. GitHub Actions cannot automatically control the local Studio session.

Saving a modified place, publishing, production DataStore writes, and player-impacting Open Cloud operations require explicit human review and approval. Use least privilege, isolated test places, and synthetic data. A generated test plan or static report must not be represented as an executed Studio test.

## Growth principles

Maximize sustainable player value and discover viable opportunities—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Documentation

- V28 feature index: INDEX_V28.md
- V28 server authority and remote security: v28/docs/SERVER_AUTHORITY_AND_REMOTE_SECURITY.md
- V28 DataStore migration safety: v28/docs/DATASTORE_MIGRATION_SAFETY.md
- V28 multiplayer reliability: v28/docs/MULTIPLAYER_RELIABILITY_VALIDATION.md
- V28 report reference: v28/docs/SECURITY_REPORT_REFERENCE.md
- V27 Luau and architecture: v27/INDEX_V27.md
- V26 Studio MCP workflow: v26/docs/STUDIO_MCP_WORKFLOW.md
- V25 session continuity guide: v25/docs/SESSION_CONTINUITY.md
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
