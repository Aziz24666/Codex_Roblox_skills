# Roblox Codex Game Studio Kit

[![V26 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v26-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v26-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V26.0.0 — Roblox Studio MCP and Automated Testing.** This is the complete cumulative V1-V26 toolkit. Only the current release is required.

[Open the V26 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v26.0.0).

## What's included

- **210 native Codex skills** for Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and monetization.
- V23-V24 sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- V25 durable checkpoints, recoverable handoff prompts, backup recovery, validated journal integrity, project-root binding, and bounded-stage task execution.
- V26 Studio MCP workflow skills for safe inspection/editing, multiplayer/device/network testing, and evidence-based change review.
- A read-only V26 MCP configuration doctor and a review-only test-plan generator/verifier.
- Cumulative Luau compilation, Rojo builds, regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V26 release, then open the cumulative package root in Codex.
2. Read `AGENTS.md` and `INDEX_V26.md`.
3. Initialize session continuity in the **actual game project folder**:

       python "C:\Path\To\roblox-codex-game-studio-kit-v26\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. Check the Studio MCP configuration without executing it (optional):

       python "C:\Path\To\roblox-codex-game-studio-kit-v26\v26\tools\v26.py" doctor --root "C:\Path\To\YourGame" --config "C:\Path\To\mcp.json"

5. Generate a review-only Studio test plan:

       python "C:\Path\To\roblox-codex-game-studio-kit-v26\v26\tools\v26.py" plan --root "C:\Path\To\YourGame"

6. Follow the Studio MCP workflow in `v26/docs/STUDIO_MCP_WORKFLOW.md`. Keep Studio testing on an isolated test place and review edits before saving.

V25 commands: `start`, `checkpoint`, `handoff`, `resume`, `status`, `verify`, and `recover`. V26 commands: `doctor`, `plan`, and `verify-plan`.

## Studio MCP and testing boundaries

Roblox Studio's MCP server is local to the developer's machine. Enable it in Studio and connect a trusted Codex client using Studio's Quick Connect or its documented configuration. The V26 doctor only checks a JSON config's structure; it does not start Studio or prove a live connection. GitHub Actions cannot automatically control your local Studio session.

StudioTestService supports up to eight simulated clients in one Studio multiplayer test. Device and Network Simulator features apply to Studio playtests, not published experiences. V26 creates a test plan; actual Studio runs must be performed and evidenced in the connected Studio environment.

Saving a modified place, publishing, production DataStore writes, and player-impacting Open Cloud operations require explicit human review and approval. Use least privilege and isolated test data.

## Growth principles

Maximize sustainable player value and discover viable opportunities—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Documentation

- [INDEX_V26.md](INDEX_V26.md)
- [V26 Studio MCP workflow](v26/docs/STUDIO_MCP_WORKFLOW.md)
- [V26 multiplayer/device testing](v26/docs/MULTIPLAYER_DEVICE_TESTING.md)
- [V26 safe automation boundaries](v26/docs/SAFE_AUTOMATION_BOUNDARIES.md)
- [V25 session continuity](v25/docs/SESSION_CONTINUITY.md)
- [V18 no-gambling and fair monetization](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
