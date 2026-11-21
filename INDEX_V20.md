# Roblox Codex Game Studio Kit — V20 Index

V20 is the current cumulative release. It extends the V1–V19 toolkit with production reliability and live-operations governance. The cumulative package contains **185 installed native skills**: 175 inherited skills plus five V19 verification specialists and five V20 production specialists.

## Start here

1. Read root `AGENTS.md` and this index.
2. Start substantial work with `$roblox-end-to-end-development-orchestrator`.
3. Inspect the project using `python v18/tools/v18.py doctor --root .`.
4. Route relevant specialists using `python v18/tools/v18.py route --root . --task "..."`.
5. Generate a risk-based verification plan using `python v19/tools/v19.py plan-tests --root . --task "..."`.
6. Validate production declarations using `python v20/tools/v20.py validate-contract --root . --file path/to/production-contract.json`.
7. Run applicable checks in their real environments and validate results with V19 evidence rules.

## V20 specialist skills

- `$roblox-server-authority-and-remote-boundaries` — server-owned state, explicit remote operations, validation, ownership/context checks, rate limits, and duplicate-request safety.
- `$roblox-player-data-resilience-and-migrations` — profile lifecycle, UpdateAsync-safe writes, bounded retries, schema migrations, session ownership, and safe recovery.
- `$roblox-idempotent-economy-transactions` — verified receipt processing, exact fixed grants, durable transaction identifiers, and duplicate-delivery protection.
- `$roblox-live-operations-and-safe-rollouts` — development/staging/canary/production promotion, feature flags, kill switches, compatibility, and data-safe rollback.
- `$roblox-production-observability-and-incident-response` — actionable metrics, privacy-safe telemetry, alert ownership, incident triage, and recovery.

## V20 CLI

```bash
python v20/tools/v20.py evaluate-routing --root .
python v20/tools/v20.py validate-contract --root . --file v20/examples/production-contract.example.json
python v20/tools/v20.py verify --root .
```

The production contract is a static declaration validator. It does not inspect live Roblox configuration or execute Studio, DataStore, MarketplaceService, production telemetry, or deployment actions. Keep unexecuted checks NOT_RUN or BLOCKED under V19 rules.

## V19 testing and evidence layer

- `$roblox-test-matrix-and-risk-planning` builds a risk-selected test matrix.
- `$roblox-luau-static-analysis-and-type-safety` integrates configured Luau analysis and lint.
- `$roblox-studio-multiplayer-test-engineering` defines real multi-client Studio scenarios.
- `$roblox-skill-routing-benchmarking` maintains deterministic route regressions.
- `$roblox-test-evidence-auditing` checks evidence completeness and honest statuses.

V19's routing benchmark evaluates deterministic routing only, not LLM quality or generated-code correctness.

## V1–V18 foundations

V18 supplies task intake, connected workflow orchestration, dependency-aware workstreams, shared contracts, approval gates, and the no-gambling economy policy. V20 extends these foundations; it does not replace them.
