# Roblox Codex Game Studio Kit — V18 Index

V18 adds a connected development control plane to the complete V1–V17 package. After integration, the cumulative package includes 175 native Codex skills. V18 provides 16 specialist definitions: 12 new workflow/orchestration skills and updated versions of four economy/monetization skills already present in V17, alongside task graphs, shared contracts, agent coordination, validation, safe autonomy, and evidence-backed completion.

## Start here
- Root `AGENTS.md` — operating contract.
- Root `INDEX_V18.md` — full skill routing.
- `v18/docs/AUTOMATED_WORKFLOW.md` — task lifecycle and quick start.
- `v18/docs/SKILL_INTEROPERABILITY.md` — shared specialist contract.
- `v18/docs/TASK_CONTRACT_AND_STATE_MACHINE.md` — task state and evidence rules.
- `v18/docs/APPROVAL_BOUNDARIES.md` — safe automation boundaries.
- `v18/tools/v18.py` — local project doctor, router, planner, and validator.

## V18 skills
- `$roblox-end-to-end-development-orchestrator` — owns the whole task lifecycle.
- `$roblox-task-intake-and-requirements` — request-to-acceptance-criteria.
- `$roblox-project-reconnaissance-automation` — read-only project/toolchain discovery.
- `$roblox-impact-aware-skill-routing` — minimal specialist selection.
- `$roblox-cross-system-contract-governance` — shared APIs/data/remote/lifecycle contracts.
- `$roblox-dependency-aware-workstream-planning` — acyclic dependency graph and exclusive ownership.
- `$roblox-autonomous-implementation-loop` — bounded inspect/edit/check/repair execution.
- `$roblox-agent-delegation-and-coordination` — parallel work only when genuinely independent.
- `$roblox-continuous-validation-and-repair` — impact-selected validation and regression.
- `$roblox-risk-and-approval-gating` — preserves user control of external side effects.
- `$roblox-workflow-state-and-context-handoff` — validated task/project state across sessions.
- `$roblox-evidence-first-completion` — truthful completion and release reporting.

## V18 economy and monetization specialists
- `$roblox-player-friendly-monetization` — mandatory no-gambling policy and transparent monetization strategy.
- `$roblox-deterministic-progression-shop` — fixed catalogs, explicit prices, exact grants, and idempotent fulfillment.
- `$roblox-tiered-catalog-progression` — all required items in every earlier tier must be owned before the next tier unlocks; required items need a non-Robux route.
- `$roblox-earned-currency-economy` — predictable gameplay earnings, server-authoritative balances, and auditable transactions.

Read `docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md` before any store, economy, currency, or monetization work. Paid random outcomes and gambling-like mechanics are prohibited by V18.

## Existing specialists by domain
Use the generated `v18/data/skill-registry.json` and `v18/workflow/skill-routing.json` as routing aids. Major domains include core game development; architecture; UI/input/accessibility; character/avatar/animation; multiplayer/networking/security; data/persistence/economy; NPC/gameplay; assets/content/procedural world; Studio/plugins/MCP; QA/performance; analytics/liveops; research/reference originality; and CI/release.

## Recommended automation sequence
1. `$roblox-end-to-end-development-orchestrator`
2. `$roblox-task-intake-and-requirements`
3. `$roblox-project-reconnaissance-automation` and `python v18/tools/v18.py doctor --root .`
4. `$roblox-impact-aware-skill-routing` and `python v18/tools/v18.py route --root . --task "..."`
5. `$roblox-cross-system-contract-governance` and `$roblox-dependency-aware-workstream-planning`
6. `$roblox-autonomous-implementation-loop` with relevant V1–V17 specialists
7. `$roblox-continuous-validation-and-repair`
8. `$roblox-evidence-first-completion`

The sequence is adaptive: do not load irrelevant specialists or create subagents for work that is small, coupled, or unsupported by the current runtime.
