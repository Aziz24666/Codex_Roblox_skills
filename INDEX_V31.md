# Roblox Codex Game Studio Kit — V31

V31.0.0 is the current cumulative release: V1-V31, 228 native Codex skills.

## V31 additions

- Four native Codex skills for AnalyticsService governance, privacy-safe aggregate health analytics, LiveOps operations, and experiment design.
- `v31/tools/v31.py`:
  - `doctor`: local source inventory and optional tool checks.
  - `validate-catalog`: validate the approved custom analytics event catalog, field cardinality, privacy review declarations, and optional request budget.
  - `audit`: bounded, read-only Luau audit for AnalyticsService methods, deprecated calls, likely client-context custom-event calls, uncatalogued literal event names, and suspicious personal-data access near event calls.
  - `evaluate-health`: evaluate an aggregate-only health snapshot against minimum sample, freshness, warning, and hard thresholds.
- Three JSON schemas, three example files, two guides, regression tests, cumulative package patching and auditing.
- Cumulative package target: **228 native Codex skills**.

## Quick start

From the extracted V31 package root:

```powershell
python ".\v31\tools\v31.py" doctor --root "C:\Path\To\YourGame"
python ".\v31\tools\v31.py" validate-catalog --root "C:\Path\To\YourGame"
python ".\v31\tools\v31.py" audit --root "C:\Path\To\YourGame" --catalog ".codex\analytics\event-catalog.json"
python ".\v31\tools\v31.py" evaluate-health --root "C:\Path\To\YourGame"
```

The event catalog, health policy, and health snapshot templates are in `v31/examples/`. Copy them into the selected project under `.codex/analytics/`, then replace example values with reviewed project data.

## Analytics governance

The catalog supports up to 100 custom event definitions, at most three bounded custom fields per event, short finite allowed-value lists, an explicit privacy-review declaration, and an optional declared request budget. The audit is a text heuristic; it cannot prove runtime behavior or fully resolve dynamic/shared modules. Current API details and limitations must be checked against the [Roblox AnalyticsService reference](https://create.roblox.com/docs/reference/engine/classes/AnalyticsService), [custom events guide](https://create.roblox.com/docs/production/analytics/custom-events), and [event types documentation](https://create.roblox.com/docs/production/analytics/event-types).

## Aggregate health and LiveOps

Health snapshots contain aggregate numeric metrics only. Stale, undersized, incomplete, future-dated, or unsupported inputs are held rather than treated as healthy. Thresholds are project-owned and must be set before evaluating a snapshot. V31 does not collect player telemetry, create user profiles, change feature flags, send notifications, publish, or call Roblox services.

## Retained safeguards

All V1-V30 tools and skills remain cumulative. Keep server-authoritative gameplay, protected persistence, evidence-backed performance, human-approved production releases, fixed paid outcomes, worthwhile free progression, and the mandatory no-gambling requirements.
