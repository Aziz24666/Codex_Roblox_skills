# Roblox Codex Game Studio Kit — V19 Index

V19 is the current cumulative release. It extends the V1–V18 toolkit with testing intelligence and evidence governance. The cumulative package contains **180 installed native Codex skills**: 175 inherited skills plus five V19 specialists.

## Start here

1. Read root \`AGENTS.md\` and this index.
2. Start substantial work with \`$roblox-end-to-end-development-orchestrator\`.
3. Inspect the project using \`python v18/tools/v18.py doctor --root .\`.
4. Route relevant specialists using \`python v18/tools/v18.py route --root . --task "..."\`.
5. Generate a risk-based verification plan using \`python v19/tools/v19.py plan-tests --root . --task "..."\`.
6. Run supported static checks and project tests; use Studio workflows for checks that need the real Roblox runtime.
7. Validate the evidence packet with \`python v19/tools/v19.py validate-evidence --root . --file path/to/verification-evidence.json\`.
8. Use \`python v19/tools/v19.py evaluate-routing --root .\` to run the deterministic skill-routing regression corpus.

## V19 specialist skills

- \`$roblox-test-matrix-and-risk-planning\` — turn affected systems and risk into a prioritized test matrix.
- \`$roblox-luau-static-analysis-and-type-safety\` — use Luau type checking, linting, and formatting as repeatable quality gates.
- \`$roblox-studio-multiplayer-test-engineering\` — design real Studio multi-client tests with StudioTestService and record actual outcomes.
- \`$roblox-skill-routing-benchmarking\` — maintain deterministic, adversarial routing cases and track regressions.
- \`$roblox-test-evidence-auditing\` — validate evidence, environment claims, and honest PASS/FAIL/BLOCKED/NOT_RUN states.

## V1–V18 capability areas

The cumulative library still covers architecture, core game systems, Luau, character and avatar pipelines, animation, user interface and accessibility, networking and security, persistence and economy, NPCs, assets and procedural worlds, Studio and plugins, QA/performance, analytics/live operations, originality, and release engineering.

V18 remains the orchestration foundation: intake, discovery, routing, contracts, dependency-aware planning, bounded implementation, approvals, task handoff, evidence-first completion, and the no-gambling monetization policy.

## V19 CLI

\`\`\`bash
python v19/tools/v19.py evaluate-routing --root .
python v19/tools/v19.py plan-tests --root . --task "Implement a cross-platform character inventory" --changed src/Client/Inventory.luau
python v19/tools/v19.py validate-evidence --root . --file .codex/workflows/tasks/example/verification-evidence.json
python v19/tools/v19.py verify --root .
\`\`\`

## Evidence boundaries

The CLI does not launch Studio or create real multi-client sessions. GitHub Actions validates package logic, schemas, routing behavior, tests, and archive integrity. Studio, multiplayer, device, performance, DataStore, purchase fulfillment, asset permissions, and production checks must be performed in their actual authorized environments. Do not infer them from static CI success.

Read \`v19/docs/TESTING_AND_EVIDENCE.md\`, \`v19/docs/STUDIO_TEST_AUTOMATION.md\`, and \`v19/docs/SKILL_BENCHMARKS.md\` before extending the testing pipeline.
