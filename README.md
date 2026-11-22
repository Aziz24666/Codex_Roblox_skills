# Roblox Codex Game Studio Kit

[![V25 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v25-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v25-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release candidate: V25.0.0 — Session Continuity and Interruption Recovery.** This is the complete cumulative V1-V25 toolkit. Only the current release is required.

[Open the V25 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v25.0.0).

## What's included

- **207 native Codex skills** for Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and monetization.
- V23-V24 sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- V25 durable checkpoints, recoverable handoff prompts, backup recovery, a hash-chained event journal, and bounded-stage task execution.
- Atomic checkpoint writes, concurrent-write protection, integrity checks, and automatic Git-ignore rules for local session files.
- Existing V18-V24 no-gambling, fair-monetization, server-authority, evidence, and Roblox platform-compliance safeguards.

## Start a Roblox development session

1. Download and extract the V25 release, then open the cumulative package root in Codex.
2. Read AGENTS.md and INDEX_V25.md.
3. Initialize a checkpoint in the **actual game project folder**:

       python "C:\Path\To\roblox-codex-game-studio-kit-v25\v25\tools\v25.py" start --root "C:\Path\To\YourGame" --goal "Build and ship my Roblox game"

4. After each independently verified implementation stage, save progress:

       python "C:\Path\To\roblox-codex-game-studio-kit-v25\v25\tools\v25.py" checkpoint --root "C:\Path\To\YourGame" --stage "Server validation" --completed "Added server-side validation" --next "Run Studio integration tests" --test "Unit tests: PASS"

5. Before ending a conversation or after a significant stage, create a handoff:

       python "C:\Path\To\roblox-codex-game-studio-kit-v25\v25\tools\v25.py" handoff --root "C:\Path\To\YourGame" --stage "Server validation" --next "Run Studio integration tests"

6. In a new conversation, paste C:\Path\To\YourGame\.codex\session\RESUME_PROMPT.md. Verify the repository and tests before continuing.

Commands: start, checkpoint, handoff, resume, status, verify, and recover. Full instructions are in v25/docs/SESSION_CONTINUITY.md.

## Growth principles

Maximize sustainable player value and discover viable opportunities—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting.

## Automation and validation boundaries

V25 saves and restores local development context; it does **not** prevent ChatGPT conversation limits or network failures, recover unsaved work from a deleted workspace, or replace Git/source backups. V24 creates reviewable plans; it does not edit game source, create live products, change prices, access Creator Dashboard, automate in-game player activity, or publish experiences. Roblox Studio runtime, Creator Dashboard eligibility, live Marketplace behavior, platform configuration, and actual earnings require live verification and human approval.

## Documentation

- INDEX_V25.md and v25/INDEX_V25.md
- v25/docs/SESSION_CONTINUITY.md
- v24/docs/AUTOMATED_GROWTH_PIPELINE.md
- v23/docs/ROBLOX_REVENUE_OPPORTUNITY_PLAYBOOK.md
- v22/docs/MANAGED_PRICING_AND_SUBSCRIPTIONS.md
- v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
