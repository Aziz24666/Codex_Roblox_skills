---
name: roblox-asset-release-and-migration-v35
description: Plan safe asset catalog revisions, version changes, dependency migrations, staged adoption, and rollback evidence for Roblox releases.
---

# Roblox Asset Release and Migration

Make asset changes reviewable and recoverable across a release boundary.

For each candidate catalog, identify new assets, removed assets and remaining dependents, changed sources/provider IDs/versions/targets/measurements, rights and moderation regressions, and dependencies that are not approved or released.

Safe migration:
1. Keep the previous catalog and release evidence immutable.
2. Create a candidate catalog with explicit version changes.
3. Run compare-catalogs and review additions, removals, changed fields, and regressions.
4. Check asset ownership and experience permissions using the authorized Roblox workflow.
5. Stage references in an isolated place/version where practical.
6. Test loading, streaming, visual/audio quality, and supported devices in Studio.
7. Promote through the V30 release dossier with human approval and a rollback plan.
8. Retain previous asset references until dependent systems have safely migrated.

Do not automatically delete, transfer, upload, publish, or replace Roblox assets. A catalog diff never proves that a live asset exists or is accessible. Preserve human approval and a reversible change plan.
