# Roblox Codex Game Studio Kit

[![V36 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v36-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v36-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V36.0.0 — Accessibility, Responsive UI, and Localization Readiness.** The cumulative V1-V36 toolkit contains **248 native Codex skills**. Only the current release is required.

[Open the V36 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v36.0.0).

## What's included
- 248 native Codex skills covering Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio tools, testing, performance, release engineering, analytics, LiveOps, safety, moderation, sustainable monetization, asset production, and accessibility.
- **V36** adds accessibility and inclusive interaction reviews, responsive UI/readability, localization/RTL readiness, sensory alternatives and reduced-motion guidance, plus an offline quality manifest validator/auditor.
- **V35** adds asset catalogs, provenance/review tracking, dependency validation, per-device content budgets, and catalog migration comparison.
- **V34** adds long-session performance soak analysis, profiler evidence triage, repeated benchmark comparisons, and rollout monitoring.
- **V33** adds automated QA plans/reports, Studio test orchestration guidance, device/input/multiplayer regression, and regression comparison.
- **V32** adds player-safety guidance, privacy-minimal moderation records, and human-review/appeal workflows.
- **V31** adds AnalyticsService event governance and privacy-safe aggregate health checks.
- **V30** adds production release plans, environment gates, evidence validation, approvals, rollback/backup readiness, and configuration hygiene.

## Start
1. Download and extract the V36 release.
2. Open the extracted package root in Codex.
3. Read AGENTS.md and INDEX_V36.md.
4. Run `python .\\v36\\tools\\v36.py doctor --root C:\\Path\\To\\YourGame`.
5. Copy `v36/examples/quality-manifest.example.json` into your game project and replace sample values with reviewed data.
6. Run validate-manifest and audit using the commands in INDEX_V36.md.

## Safeguards and limitations
All V1-V35 safeguards remain cumulative, including server authority, secure persistence, privacy, player safety, human-reviewed moderation, transparent monetization, fixed paid outcomes, and the mandatory no-gambling policy. V36 checks supplied metadata only; it does not inspect Studio UI or certify accessibility. Actual device testing and human review remain required. Do not store player health information, personal data, credentials, private URLs, or free-form player profiles in the manifest.

Released under MIT. Independent community toolkit; not affiliated with Roblox Corporation or OpenAI.
