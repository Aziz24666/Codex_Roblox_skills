# V42.0.0 — LiveOps, Events and Configuration Management

## Added
- Four native Codex skills for event lifecycle/scheduling, Roblox Experience Configs and feature flags, safe staged rollouts, and compatibility/rollback.
- Offline LiveOps config/event manifest validator and auditor.
- Baseline/candidate compatibility checker for removed config keys, type changes, default changes, and event additions/removals.
- Strict JSON handling, timezone-aware event windows, schedule-overlap checks, server-only config contracts, conditional-config limits, secret-value guardrails, draftHash/publish gates, and staged-restore requirements.
- JSON Schema, example model, documentation, regression tests, cumulative patcher/auditor, and Windows/Linux CI.

## Cumulative package
V1–V42, 272 native Codex skills. Download only the V42 package.

## Limitations
The CLI is offline and validates supplied metadata only. It does not inspect project Luau, call ConfigService or Open Cloud, stage or publish configurations, schedule live events, read live telemetry, or execute rollback. A compatibility report is a manifest comparison, not a whole-project reference proof. Production operations require authorized credentials, staged tests, human approval, published readback, and independent runtime verification.
