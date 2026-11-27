# Roblox Codex Game Studio Kit

[![V39 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v39-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v39-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V39.0.0 — Deterministic Economy and Progression Simulation.** The cumulative V1–V39 toolkit contains **260 native Codex skills**. Only the current release is required.

[Open the V39 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v39.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210 native Codex skills; V27 — 213 native Codex skills; V28 — 216 native Codex skills; V29 — 220 native Codex skills; V30 — 224 native Codex skills; V31 — 228 native Codex skills; V32 — 232 native Codex skills; V33 — 236 native Codex skills; V34 — 240 native Codex skills; V35 — 244 native Codex skills; V36 — 248 native Codex skills; V37 — 252 native Codex skills; V38 — 256 native Codex skills; V39 — 260 native Codex skills.

- **260 native Codex skills** spanning Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio workflows, testing, performance, release engineering, analytics, LiveOps, safety, moderation, monetization, asset production, accessibility, localization, implementation orchestration, and incident response.
- **V39** adds gameplay currency source/sink modeling, deterministic day-by-day simulations across synthetic activity archetypes, progression milestone rewards, and fairness review with an offline model validator/simulator.
- **V38** adds production incident triage/severity, privacy-safe service health and impact, human-approved mitigation/rollback/recovery, and player communications/postmortem readiness, plus an offline incident validator/auditor.
- **V37** adds project reconnaissance and architecture mapping, feature decomposition/dependency planning, scoped implementation/change-impact review, implementation evidence and handoff, plus an offline plan/report validator.
- **V36** adds accessibility and inclusive interaction reviews, responsive UI/readability, localization/RTL readiness, sensory alternatives and reduced-motion guidance, plus an offline quality manifest validator/auditor.
- **V35** adds an asset catalog, provenance/review tracking, dependency-graph validation, per-device content budgets, and catalog migration comparison.
- **V34** adds long-session performance soak analysis, profiler evidence triage, repeated benchmark comparisons, and rollout monitoring.
- **V33** adds automated QA plans/reports, Studio test orchestration guidance, device/input/multiplayer regression, and regression comparison.
- **V32** adds player-safety guidance, bounded static review for custom text filtering, privacy-minimal moderation records, and human-review/appeal workflows.
- **V31** adds AnalyticsService event governance, instrumentation auditing, privacy-safe aggregate health checks, and LiveOps readiness.
- **V30** adds production release plans, environment gates, evidence validation, approval records, rollback/backup readiness, and configuration hygiene.
- **V29** adds profiling, Luau hot-path review, memory/asset optimization, device budgets, and single-capture measurement comparisons.
- **V28** adds server-authority, remote-contract, DataStore migration, and multiplayer reliability checks.
- **V27** adds Luau static-analysis and architecture tools for dependency cycles, type-mode inventory, remote contracts, and Rojo validation.
- **V26** adds Studio MCP workflows for inspection/editing, multiplayer/device/network testing, and evidence-based change review.
- **V25** adds durable checkpoints, recoverable handoffs, backup recovery, journal integrity, project-root binding, and staged task execution.
- **V23–V24** add sustainable monetization discovery, opportunity ranking, backlog creation, and growth-roadmap automation.
- Cumulative regression suites, package audits, archive integrity checks, and release checks.

## Start a Roblox development session

1. Download and extract the V39 release, then open the extracted package root in Codex.
2. Read `AGENTS.md` and `INDEX_V39.md`.
3. Initialize session continuity in the actual game project folder:

       python C:\Path\To\roblox-codex-game-studio-kit-v39\v25\tools\v25.py start --root C:\Path\To\YourGame --goal "Build and ship my Roblox game"

4. For feature work, read `v37/INDEX_V37.md` and follow the V37 reconnaissance → plan → scoped implementation → evidence handoff workflow.
5. For a production incident, copy `v38/examples/incident.example.json` into `.codex/incidents/incident.json`, replace the example values with verified aggregate-only facts, then run:

       python .\v38\tools\v38.py doctor --root C:\Path\To\YourGame
       python .\v38\tools\v38.py validate --root C:\Path\To\YourGame --incident .codex\incidents\incident.json
       python .\v38\tools\v38.py audit --root C:\Path\To\YourGame --incident .codex\incidents\incident.json --output .codex\reports\incident-audit.json

   Keep personal/player-level information out of incident records. High-risk and recovery operations require explicit human approval outside the CLI.

6. For an economy model, copy `v39/examples/economy-model.example.json` to `.codex/economy/economy-model.json`, adjust only with documented design assumptions, then run:

       python .\v39\tools\v39.py doctor --root C:\Path\To\YourGame
       python .\v39\tools\v39.py validate --root C:\Path\To\YourGame --model .codex/economy/economy-model.json
       python .\v39\tools\v39.py simulate --root C:\Path\To\YourGame --model .codex/economy/economy-model.json --output .codex/reports/economy-simulation.json

   The model uses synthetic cohorts and is not a prediction of live player behavior. Do not include player-level data or gambling mechanics.

Commands: V25 — start, checkpoint, handoff, resume, status, verify, recover. V26 — doctor, plan, verify-plan. V27 — doctor, audit, typecheck, rojo-check. V28 — doctor, audit, validate-migration. V29 — doctor, audit, budget, compare, report. V30 — doctor, plan, validate, audit. V31 — doctor, validate-catalog, audit-catalog, evaluate-health. V32 — doctor, audit, validate-policy, validate-case, validate-register. V33 — doctor, audit, validate-plan, validate-report, compare. V34 — doctor, validate-capture, analyze-soak, validate-suite, compare-repeated. V35 — doctor, validate-catalog, audit-catalog, compare-catalogs. V36 — doctor, validate-manifest, audit. V37 — doctor, validate-plan, audit-plan, validate-report, audit-report. V38 — doctor, validate, audit. V39 — doctor, validate, simulate.

## V38 incident response boundaries

V38 validates supplied incident JSON and declared response metadata only. It does not inspect live Roblox telemetry, establish actual service impact, authenticate signal/evidence/approval/message references, trigger alerts, execute mitigations, roll back releases, restore DataStores, or send player notices. Privacy fields are human attestations, not automated PII detection. Never put player names, Roblox user IDs, chat contents, support conversations, contact details, credentials, or individual player histories in incident files. A successful validation is not approval to perform a live operation.

## V37 implementation workflow boundaries

V37 validates supplied plan/report metadata, dependency graphs, file-scope declarations, recorded changed paths, acceptance-criterion IDs, and opaque evidence references. It does not inspect the source tree, compute actual version-control diffs, execute code, run Luau, invoke Roblox Studio, contact Roblox services, or authenticate evidence references. Compare reported paths with the actual Git diff during review. A CI pass does not prove Studio, device, runtime, or multiplayer behavior.

## Earlier verification boundaries and safeguards

V36 quality checks validate supplied metadata only. They do not inspect Roblox Studio UI instances, analyze screenshots, execute Luau, test real devices, or certify accessibility. Contrast, navigation, captions, reduced-motion behavior, text scaling, localization, and RTL behavior require human review and actual target-device testing.

V35 catalog commands validate supplied metadata and project-local source paths only. They do not inspect binary asset content, query Roblox, access Creator Store/private inventories, upload/publish/delete/transfer assets, or determine copyright, license scope, or moderation approval. Rights and moderation states must be verified and maintained by authorized humans. Device budgets are project-specific and must be calibrated with actual Studio/device testing.

V34 performance reports process supplied structured evidence only; they do not launch Studio, capture MicroProfiler dumps, execute Luau, access Creator Dashboard, or read live telemetry. A memory-growth signal is not proof of a leak.

V33 test plans and reports are offline; they do not launch Studio, simulate multiplayer, emulate devices, or inject input. A GitHub Actions pass does not prove Studio playtests passed.

Custom non-chat text visible to other players must follow Roblox's current server-side TextService filtering guidance. Moderation decisions must be human-reviewed and appealable. Keep game-critical state authoritative on the server, validate remote arguments, and protect persistence.

Keep analytics aggregate and purpose-bound; do not build individual-spender profiles. Keep paid outcomes fixed and disclosed, provide worthwhile free progression, and preserve the mandatory no-gambling policy.

## Documentation

- V39 feature index: `INDEX_V39.md`
- Economy model design: `v39/docs/ECONOMY_MODEL_DESIGN.md`
- Interpreting simulation results: `v39/docs/INTERPRETING_SIMULATION_RESULTS.md`
- Economy CLI reference: `v39/docs/ECONOMY_CLI.md`
- V38 feature index: `INDEX_V38.md`
- Incident triage and service health: `v38/docs/INCIDENT_TRIAGE_AND_SERVICE_HEALTH.md`
- Mitigation approvals and rollback: `v38/docs/MITIGATION_APPROVAL_AND_ROLLBACK.md`
- Communications and postmortem: `v38/docs/COMMUNICATION_AND_POSTMORTEM.md`
- Incident CLI reference: `v38/docs/INCIDENT_CLI.md`
- V37 feature index: `INDEX_V37.md`
- Project reconnaissance and change impact: `v37/docs/PROJECT_RECONNAISSANCE_AND_CHANGE_IMPACT.md`
- Feature planning and dependency graphs: `v37/docs/FEATURE_PLANNING_AND_DEPENDENCY_GRAPHS.md`
- Implementation evidence and handoff: `v37/docs/IMPLEMENTATION_EVIDENCE_AND_HANDOFF.md`
- MIT License

Released under MIT. This is an independent community toolkit, not affiliated with or endorsed by Roblox Corporation or OpenAI.
