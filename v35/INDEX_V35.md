# Roblox Codex Game Studio Kit — V35

V35.0.0 is the cumulative V1-V35 package with **244 native Codex skills**. Only this current cumulative release is required.

## V35 additions

- Four native Codex skills for asset catalog governance, provenance/rights review, device-aware content budgets, and asset release/migration.
- Offline CLI: doctor, validate-catalog, audit-catalog, and compare-catalogs.
- Strict asset catalog and budget-policy schemas with bounded fields and privacy-minimal opaque evidence references.
- Dependency validation for missing references, duplicates, self-dependencies, and cycles.
- Local source-path validation with symlink/traversal protection and optional file-size verification.
- Per-device budgets for source size, texture pixels, mesh triangles, audio duration, and animation keyframes.
- Candidate catalog diff reporting for additions, removals, changed fields, and provenance/moderation/lifecycle regressions.
- Two JSON schemas, two examples, three engineering guides, 40+ regression tests, cumulative package patcher/auditor, and V1-V35 release workflow.

## Quick start

From the extracted V35 package root:

    python .\v35\tools\v35.py doctor --root C:\Path\To\YourGame
    python .\v35\tools\v35.py validate-catalog --root C:\Path\To\YourGame --catalog .codex/assets/catalog.json
    python .\v35\tools\v35.py audit-catalog --root C:\Path\To\YourGame --catalog .codex/assets/catalog.json --policy .codex/assets/budget-policy.json --output .codex/reports/v35-asset-audit.json
    python .\v35\tools\v35.py compare-catalogs --root C:\Path\To\YourGame --baseline .codex/assets/catalog-v1.json --candidate .codex/assets/catalog-v2.json --output .codex/reports/v35-asset-diff.json

Copy the examples from v35/examples/ and replace all illustrative values with real reviewed project data before use.

## Difference from previous versions

V29 and V34 cover runtime performance profiling, budgets, soak trends, and benchmark evidence. V35 addresses the content production pipeline: source/provenance cataloging, asset dependency integrity, rights/review-state tracking, per-device content budgets, and catalog migration diffs. It does not inspect binary asset formats or replace Studio/device tests.

## Verification boundaries

All V35 commands run offline on user-supplied JSON and local source paths. The tools do not query Roblox, upload or publish assets, access private inventories, infer copyright or permissions, or change live experiences. Rights and moderation states are human-reviewed assertions; budget values are project policy, not universal Roblox limits.

All V1-V34 safeguards remain cumulative, including server authority, secure persistence, privacy, player safety, human-reviewed moderation, transparent monetization, fixed paid outcomes, and the mandatory no-gambling policy.
