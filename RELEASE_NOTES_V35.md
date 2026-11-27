# V35.0.0 — Asset Pipeline Governance and Content Validation

V35 extends the cumulative V1-V34 Roblox Codex Game Studio Kit with a structured asset production and release-evidence layer.

## New capabilities

- Four native skills for catalog/dependency governance, provenance and rights review, device-aware content budgets, and asset release/migration.
- V35 tools:
  - doctor: inspect local Python and project-root readiness.
  - validate-catalog: validate strict asset metadata, provenance references, local source paths, and dependency graph integrity.
  - audit-catalog: evaluate human-maintained rights/moderation/lifecycle states and per-device content budgets.
  - compare-catalogs: report additions, removals, field changes, and release-readiness regressions between catalog revisions.
- Two JSON schemas, two examples, three engineering guides, cumulative package patcher/auditor, and a V1-V35 quality workflow.
- Cumulative target: **244 native Codex skills**.

## Verification boundaries

- The CLI is offline and processes only supplied JSON and local project-relative paths.
- It does not inspect binary asset formats, enumerate Roblox inventory, access Creator Store/private inventory, upload, publish, delete, or transfer assets.
- Rights and moderation statuses are human-maintained assertions, not automated determinations of copyright, license validity, or Roblox approval.
- Content budgets are project-defined thresholds, not universal platform limits.
- Catalog diffs identify changes for review; Studio testing and human release approvals remain required.

All V1-V34 safeguards remain cumulative: server authority, secure persistence, privacy, player safety, human-reviewed moderation, fair/transparent monetization, fixed disclosed paid outcomes, and mandatory no-gambling policy.
