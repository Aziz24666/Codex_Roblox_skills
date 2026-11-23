# V31.0.0 — Privacy-Safe Analytics and LiveOps Health

V31 extends the cumulative V1-V30 Roblox Codex Game Studio Kit with privacy-reviewed AnalyticsService event governance, a bounded source instrumentation audit, aggregate game-health guardrails, and practical LiveOps/experiment readiness.

## New capabilities

- Four native Codex skills:
  - `roblox-analytics-instrumentation-governance-v31`
  - `roblox-privacy-safe-game-health-analytics-v31`
  - `roblox-liveops-operations-readiness-v31`
  - `roblox-experiment-design-and-guardrails-v31`
- `v31/tools/v31.py` commands:
  - `doctor`: inspect local Luau inventory and optional tools.
  - `validate-catalog`: validate a finite custom event catalog, privacy review declaration, Roblox custom-field slot mappings, conservative combination-space limits, and optional telemetry request budget.
  - `audit`: detect AnalyticsService call sites, deprecated methods, likely client-context custom-event use, uncatalogued literal events, and suspicious identifying/free-text fields around custom-event calls.
  - `evaluate-health`: evaluate operator-supplied aggregate numeric metrics with predeclared thresholds, minimum sample size, and freshness limits.
- Three schemas, three examples, documentation, regression tests, cumulative package patcher/auditor, and a V1-V31 quality workflow.
- Cumulative package target: **228 native Codex skills**.

## Evidence and privacy boundaries

- Roblox AnalyticsService limits are encoded as review guardrails, not a promise that a request will succeed at runtime. The catalog maps semantic field labels to the accepted `CustomField01`/`02`/`03` enum keys and conservatively estimates the 8,000 unique-combination ceiling. Check the current Creator Hub documentation before instrumentation.
- The source audit is static, bounded, and advisory. It does not execute Luau, prove server/client execution context, send analytics, inspect player data, or contact Roblox.
- Aggregate health evaluation accepts only numeric metrics plus limited snapshot metadata. It rejects extra snapshot fields, holds stale/undersized/incomplete samples, and never fills missing values.
- The toolkit does not collect player-level telemetry, construct individual-spender profiles, or prescribe retention/revenue targets.
- LiveOps, experiments, feature-flag changes, notifications, releases, and production operations remain human-approved.
- All V1-V30 functionality and safeguards remain, including fair monetization and the mandatory no-gambling policy.

## Validation

The V31 workflow reconstructs the pinned V17 baseline, applies V18-V31 overlays, runs inherited regression suites plus V31 tests, audits the 228-skill package and repository, builds ZIP and TAR.XZ archives, compares extracted contents, and verifies SHA-256 checksums. Actual Studio execution, published-experience event delivery, Creator Dashboard verification, and LiveOps execution remain human-run tasks.
