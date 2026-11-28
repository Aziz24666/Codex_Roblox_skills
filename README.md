# Roblox Codex Game Studio Kit

[![V43 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v43-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v43-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V43.0.0 — Experimentation and Decision Intelligence.** The cumulative V1–V43 toolkit contains **276 native Codex skills**. Only the current release is required.

[Open the V43 release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v43.0.0).

## What's included

Historical cumulative skill totals retained for compatibility: V25 — 207 native Codex skills; V26 — 210 native Codex skills; V27 — 213 native Codex skills; V28 — 216 native Codex skills; V29 — 220 native Codex skills; V30 — 224 native Codex skills; V31 — 228 native Codex skills; V32 — 232 native Codex skills; V33 — 236 native Codex skills; V34 — 240 native Codex skills; V35 — 244 native Codex skills; V36 — 248 native Codex skills; V37 — 252 native Codex skills; V38 — 256 native Codex skills; V39 — 260 native Codex skills; V40 — 264 native Codex skills; V41 — 268 native Codex skills; V42 — 272 native Codex skills; V43 — 276 native Codex skills.

- **276 native Codex skills** spanning Roblox gameplay, Luau, characters, UI, networking, persistence, procedural content, Studio workflows, testing, performance, release engineering, analytics, LiveOps, safety, moderation, monetization, asset production, accessibility, localization, implementation orchestration, and incident response.
- **V43** adds Roblox native in-game experiment planning, hypothesis/MDE review, AnalyticsService instrumentation, Open Cloud lifecycle guidance, and offline experiment-plan/result review.
- **V42** adds LiveOps event scheduling, Roblox Experience Configs, staged feature-flag rollouts, and an offline validator/auditor with config, event, consumer, and deployment compatibility reporting.
- **V41** adds skill-based matchmaking queues, party/lobby lifecycle, cross-server coordination, reserved-server teleport/reconnect recovery, and an offline matchmaking validator/auditor plus deterministic synthetic-ticket simulator.
- **V40** adds player-profile lifecycle/session ownership, bounded save/retry/recovery policies, safe schema migration chains, idempotent reward/receipt commits, and an offline persistence-contract validator/auditor.
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

1. Download and extract the V43 release, then open the extracted package root in Codex.
2. Read `AGENTS.md` and `INDEX_V43.md`.
3. Initialize session continuity in the actual game project folder:

       python C:\Path\To\roblox-codex-game-studio-kit-v43\v25\tools\v25.py start --root C:\Path\To\YourGame --goal "Build and ship my Roblox game"

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

7. For persistence architecture, copy `v40/examples/persistence-model.example.json` to `.codex/persistence/persistence-model.json`, adapt it to your server-side profile implementation, then run:

       python .\v40\tools\v40.py doctor --root C:\Path\To\YourGame
       python .\v40\tools\v40.py validate --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json
       python .\v40\tools\v40.py audit --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json --output .codex/reports/persistence-audit.json

   The CLI audits declared metadata; it does not inspect Luau, connect to Roblox, read or write player data, or verify real migrations/receipt handling. Use a separate test experience for DataStore testing and migration rehearsals.

8. For matchmaking, parties and server handoff, copy `v41/examples/matchmaking-model.example.json` into `.codex/matchmaking/matchmaking-model.json`, then run:

       python .\v41\tools\v41.py doctor --root C:\Path\To\YourGame
       python .\v41\tools\v41.py validate --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json
       python .\v41\tools\v41.py audit --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json --output .codex\reports\matchmaking-audit.json
       python .\v41\tools\v41.py simulate --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json --output .codex\reports\matchmaking-simulation.json

   The simulator uses synthetic tickets only. The CLI does not call Roblox services or prove live matchmaking, party coordination, or teleport success.

9. For LiveOps event and config governance, copy `v42/examples/liveops-model.example.json` to `.codex/liveops/liveops-model.json`, then run:

       python .\v42\tools\v42.py doctor --root C:\Path\To\YourGame
       python .\v42\tools\v42.py validate --root C:\Path\To\YourGame --model .codex\liveops\liveops-model.json
       python .\v42\tools\v42.py audit --root C:\Path\To\YourGame --model .codex\liveops\liveops-model.json --output .codex\reports\liveops-audit.json
       python .\v42\tools\v42.py compare --root C:\Path\To\YourGame --baseline .codex\liveops\baseline.json --candidate .codex\liveops\candidate.json --output .codex\reports\config-compatibility.json

   V42 validates manifests only. It does not call Roblox or publish config. Keep API credentials out of project files; stage and test changes, get human approval, publish through the authorized workflow, and read back the published values.

10. For an in-game experiment, copy `v43/examples/experiment-plan.example.json` to `.codex/experiments/experiment-plan.json`, adapt the hypothesis, config values, duration, metrics, and event names, then run:

       python .\\v43\\tools\\v43.py doctor --root C:\\Path\\To\\YourGame
       python .\\v43\\tools\\v43.py validate --root C:\\Path\\To\\YourGame --manifest .codex\\experiments\\experiment-plan.json
       python .\\v43\\tools\\v43.py audit --root C:\\Path\\To\\YourGame --manifest .codex\\experiments\\experiment-plan.json --output .codex\\reports\\experiment-audit.json

   After an authorized experiment completes, prepare a results review JSON from Creator Hub/Open Cloud results and run `analyze`. V43 is offline: it does not assign players, contact Roblox, calculate MDE/significance/SRM, start experiments, or publish a winning config. Never make a launch decision from incomplete runs or SRM-affected results.

Commands: V25 — start, checkpoint, handoff, resume, status, verify, recover. V26 — doctor, plan, verify-plan. V27 — doctor, audit, typecheck, rojo-check. V28 — doctor, audit, validate-migration. V29 — doctor, audit, budget, compare, report. V30 — doctor, plan, validate, audit. V31 — doctor, validate-catalog, audit-catalog, evaluate-health. V32 — doctor, audit, validate-policy, validate-case, validate-register. V33 — doctor, audit, validate-plan, validate-report, compare. V34 — doctor, validate-capture, analyze-soak, validate-suite, compare-repeated. V35 — doctor, validate-catalog, audit-catalog, compare-catalogs. V36 — doctor, validate-manifest, audit. V37 — doctor, validate-plan, audit-plan, validate-report, audit-report. V38 — doctor, validate, audit. V39 — doctor, validate, simulate. V40 — doctor, validate, audit. V41 — doctor, validate, audit, simulate. V42 — doctor, validate, audit, compare. V43 — doctor, validate, audit, compare, analyze.

## V43 experimentation boundaries

V43 validates local experiment plans and reviews confidence-interval/SRM summaries supplied by an authorized person. It does not calculate statistical significance or MDE, assign players, create or start experiments, retrieve live results, select winners, complete experiments, or publish config. Let experiments run their planned duration; investigate SRM and critical early-harm flags, and require human review before any winning-variant rollout.

## V42 LiveOps and configuration boundaries

V42 validates local config/event manifests only. ConfigService is server-side and read-only; Open Cloud draft, publish, and restore operations require authorized credentials and explicit human approval. Stage and test a draft, use the latest draftHash to guard concurrent updates, publish with a descriptive message, and verify the published values by reading them back. Restoring a revision stages a draft; a separate publish is still required. The V42 CLI does not contact Roblox or execute live operations.

## V41 matchmaking and teleport boundaries

V41 validates supplied matchmaking JSON and synthetic tickets only. MemoryStore is ephemeral; DataStore remains the durable player-data layer. MessagingService is best effort, not authoritative. Queue tickets are removed only after a safely claimed assignment. TeleportData is visible and unencrypted, so pass opaque non-sensitive references and revalidate destination arrivals. The CLI does not access Roblox services, run Studio, measure live queue fairness, reserve servers, or teleport players.

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

- V43 feature index: `INDEX_V43.md`
- Experiment design and metrics: `v43/docs/EXPERIMENT_DESIGN_AND_METRICS.md`
- Roblox Experiments and Open Cloud: `v43/docs/ROBLOX_EXPERIMENTS_OPEN_CLOUD.md`
- AnalyticsService instrumentation: `v43/docs/ANALYTICS_INSTRUMENTATION.md`
- Statistical review and decisions: `v43/docs/STATISTICAL_REVIEW_AND_DECISIONS.md`
- V43 CLI reference: `v43/docs/V43_CLI.md`
- V42 feature index: `INDEX_V42.md`
- LiveOps event lifecycle: `v42/docs/LIVEOPS_EVENT_LIFECYCLE.md`
- Experience Configs and feature flags: `v42/docs/EXPERIENCE_CONFIGS_AND_FEATURE_FLAGS.md`
- Safe config deployment and rollback: `v42/docs/SAFE_CONFIG_DEPLOYMENT_AND_ROLLBACK.md`
- V42 CLI reference: `v42/docs/V42_CLI.md`
- V41 feature index: `INDEX_V41.md`
- Matchmaking architecture: `v41/docs/MATCHMAKING_ARCHITECTURE.md`
- Party and lobby lifecycle: `v41/docs/PARTIES_AND_LOBBY_LIFECYCLE.md`
- Teleport and recovery: `v41/docs/TELEPORT_AND_RECOVERY.md`
- V41 CLI reference: `v41/docs/V41_CLI.md`
- V40 feature index: `INDEX_V40.md`
- Persistence architecture: `v40/docs/PERSISTENCE_ARCHITECTURE.md`
- Profile migrations and receipt handling: `v40/docs/MIGRATIONS_AND_RECEIPTS.md`
- Persistence CLI reference: `v40/docs/PERSISTENCE_CLI.md`
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
