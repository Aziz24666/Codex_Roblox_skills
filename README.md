# Roblox Codex Game Studio Kit

[![V30 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v30-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v30-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V30.0.0 — Production Release Readiness.** This is the complete cumulative V1-V30 toolkit with **224 native Codex skills**. Only the current release is required.

[Open the V30 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v30.0.0).

## What's included

- **224 native Codex skills** across Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, procedural content, NPCs, Studio tools, testing, performance, release engineering, and sustainable monetization.
- **V30** adds candidate-specific production release plans, environment-specific release gates, evidence-path and optional SHA-256 validation, manual approval records, rollback/backup readiness checks, and a bounded local configuration/credential-hygiene audit.
- **V29** adds performance profiling, Luau hot-path review, memory and asset optimization, device-specific budgets, and measurement regression comparison (220 native skills at V29).
- **V28** adds server-authority and remote-contract review, rate-limit/idempotency signals, DataStore schema-migration review, and a synthetic/staging-only migration-manifest validator (216 native skills at V28).
- **V27** adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contract review, and Rojo project validation (213 native skills at V27).
- **V26** adds Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network test planning, and evidence-based change review (210 native skills at V26).
- **V25** adds durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution (207 native skills at V25).
- **V23-V24** add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V30 release, then open the cumulative package root in Codex.
2. Read `AGENTS.md` and `INDEX_V30.md`.
3. Initialize session continuity in the actual game project folder:

       python "C:\Path\To\roblox-codex-game-studio-kit-v30\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Run local V30 diagnostics:

       python "C:\Path\To\roblox-codex-game-studio-kit-v30\v30\tools\v30.py" doctor --root "C:\Path\To\YourGame"
       python "C:\Path\To\roblox-codex-game-studio-kit-v30\v30\tools\v30.py" audit --root "C:\Path\To\YourGame"

5. Create a review-only release plan using the candidate's real Git commit:

       python "C:\Path\To\roblox-codex-game-studio-kit-v30\v30\tools\v30.py" plan --root "C:\Path\To\YourGame" --version "1.2.3" --environment staging --source-revision "0123456789abcdef0123456789abcdef01234567"

6. Collect and link actual evidence for the required gates, then validate:

       python "C:\Path\To\roblox-codex-game-studio-kit-v30\v30\tools\v30.py" validate --root "C:\Path\To\YourGame"

V25 commands: start, checkpoint, handoff, resume, status, verify, and recover. V26 commands: doctor, plan, and verify-plan. V27 commands: doctor, audit, typecheck, and rojo-check. V28 commands: doctor, audit, and validate-migration. V29 commands: doctor, audit, budget, compare, and report. V30 commands: doctor, plan, validate, and audit.

## V30 release safety boundaries

V30 validates a release manifest and the files it references. It does not authenticate evidence authors, prove that Studio/device tests actually ran, certify dashboard settings, or grant permission to publish. All gates start as `not_run`; never mark a gate passed before collecting real evidence tied to the exact candidate revision.

Production plans require all standard gates, a staged rollout, rollback and backup references, and release-owner, QA-lead, and security-reviewer approval records. DataStore migrations add a migration-validation gate and data-owner approval. Publishing, migrations, production DataStore writes, and player-impacting operations remain outside the toolkit and require explicit human approval.

The local hygiene audit uses bounded static patterns. It intentionally does not copy matched secret values into reports and is not a complete secret scanner. Review findings manually.

## Earlier safeguards retained

Keep game-critical state authoritative on the server. Validate ownership, permissions, state, bounds, and request frequency. Keep DataStore migrations staged, backed up, versioned, idempotent, and tested with synthetic data. Treat static Luau findings as investigation leads; confirm performance with real Studio captures and representative hardware.

Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Documentation

- V30 feature index: INDEX_V30.md
- V30 production release readiness: v30/docs/PRODUCTION_RELEASE_READINESS.md
- V30 release evidence and rollback: v30/docs/RELEASE_EVIDENCE_AND_ROLLBACK.md
- V29 performance engineering: v29/docs/PERFORMANCE_ENGINEERING.md
- V28 server authority and DataStore safety: v28/INDEX_V28.md
- V27 Luau and architecture: v27/INDEX_V27.md
- V26 Studio MCP workflow: v26/docs/STUDIO_MCP_WORKFLOW.md
- V25 session continuity: v25/docs/SESSION_CONTINUITY.md
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
