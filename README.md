# Roblox Codex Game Studio Kit

[![V24 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v24-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v24-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V24.0.0 — Automated Monetization Portfolio and Growth Roadmap.** This is the complete cumulative V1–V24 toolkit. Only the current release is required.

[Open the V24.0.0 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v24.0.0).

## What's included
- **205 native Codex skills** for Roblox engineering, Luau, gameplay, characters, UI, networking, persistence, economy, procedural content, NPCs, Studio tools, testing, performance, release engineering, and monetization.
- All V23 monetization discovery tools and a **48-route opportunity catalogue**.
- Four V24 specialists for one-command growth automation, opportunity ranking/backlog creation, aggregate analytics comparison, and monetization quality gates.
- An automated pipeline that creates `portfolio.json`, `PORTFOLIO.md`, `ROADMAP_30_60_90.md`, `CODEX_BACKLOG.json`, `CODEX_BACKLOG.md`, `CODEX_PROMPT.md`, and `metrics-comparison.json`.
- Optional project context and sanitized before/after aggregate metrics.
- V22 pricing/subscription checks, V21 game-aware discovery, V20 production reliability, V19 evidence verification, and V18 no-gambling/fair-economy controls.

## One-command start
1. Download and extract the V24 release. Open the cumulative package root in Codex.
2. Read `AGENTS.md` and `INDEX_V24.md`.
3. Open PowerShell in the package root.
4. Run the automated workflow against the actual game project:

   `python v24/tools/v24.py run --root "C:\Path\To\YourGame" --output "reports\v24"`

5. Optionally add a project-context JSON and two aggregate metric snapshots:

   `python v24/tools/v24.py run --root "C:\Path\To\YourGame" --context "C:\Path\To\project-context.json" --baseline-metrics "C:\Path\To\baseline.json" --current-metrics "C:\Path\To\current.json" --output "reports\v24"`

6. Review `ROADMAP_30_60_90.md` and `CODEX_PROMPT.md`. Approve tasks manually before asking Codex to change game code.
7. Run `python v24/tools/v24.py verify --root .` and complete live Roblox Studio and Creator Dashboard checks.

Templates and complete instructions are in `v24/examples/` and `v24/docs/AUTOMATED_GROWTH_PIPELINE.md`.

## Growth principles
Maximize sustainable player value and discover the widest viable portfolio—not pressure. Keep the core game enjoyable without spending, show fixed outcomes and honest prices, improve genuine retention, and use aggregate analytics. Paid random outcomes and gambling-like mechanics remain prohibited. Do not use artificial playtime, AFK loops, fake scarcity, forced ads, or individual-spender targeting. Separate player purchases, Creator Rewards, ads, and creator marketplace income.

## Automation boundaries
V24 automates local source scanning, portfolio triage, roadmap generation, Codex backlog generation, and optional aggregate-metric comparison. It does **not** edit game source files, create live products, change prices, access Creator Dashboard, automate in-game player activity, or publish a Roblox experience. Every implementation and live release requires human approval and real Studio/platform evidence.

## Validation boundaries
Static checks cannot execute Roblox Studio, prove Creator Dashboard eligibility, verify live Marketplace behavior, or guarantee sales and Robux. V24 scores are triage heuristics, not revenue estimates. Missing metrics remain unknown; observed changes are not proof of causation.

## Documentation
- `INDEX_V24.md` and `v24/INDEX_V24.md`
- `v24/docs/AUTOMATED_GROWTH_PIPELINE.md`
- `v23/docs/ROBLOX_REVENUE_OPPORTUNITY_PLAYBOOK.md`
- `v23/docs/ENGAGEMENT_AND_STORE_OPTIMIZATION.md`
- `v22/docs/MANAGED_PRICING_AND_SUBSCRIPTIONS.md`
- `v21/docs/MONETIZATION_DISCOVERY_AND_PLAYER_VALUE.md`
- `v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md`
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
