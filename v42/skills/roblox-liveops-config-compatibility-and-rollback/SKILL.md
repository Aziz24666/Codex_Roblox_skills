---
name: roblox-liveops-config-compatibility-and-rollback
description: Review config key compatibility and safely restore Roblox config revisions with explicit human approval and republishing.
---

# LiveOps config compatibility and rollback

## Goal
Prevent a remote config change from breaking deployed Luau consumers and make rollback a verified, reversible operation rather than an unreviewed button press.

## Compatibility contract
- Keep a typed registry of config keys and all known consumers.
- Compare baseline and candidate manifests before staging.
- Treat removed keys and type changes as breaking until every consumer has been migrated or the old key is retained.
- Treat default-value changes as requiring review, even when the type is unchanged.
- Update consumers and config manifests together. Use additive migrations: add a new key, deploy code that can read old and new keys, migrate values, then retire the old key only after verified adoption.
- Remember that an offline comparison cannot find every dynamic or string-built Luau key reference. Search the actual project source and review the diff.

## Revision history and rollback
- Preserve config revision history and descriptive publish messages.
- Identify the exact prior revision and inspect the before/after values.
- Restore creates a staged draft and clears any existing staged draft. It does not publish by itself.
- Review the staged restore diff, require human approval, publish it with a descriptive rollback message, and read back the published values.
- Re-test the affected runtime consumers and refresh snapshots at a safe gameplay boundary.
- Keep the current and rollback manifests together as traceable release artifacts.

## Required deliverables
- Baseline-to-candidate compatibility report.
- Consumer migration plan for removed or type-changed keys.
- Revision reference and reviewed restore diff.
- Approval, publish, and post-publish readback evidence.
- Follow-up verification and incident/postmortem notes where relevant.

## Non-negotiable safeguards
- No automatic production publish or rollback from an offline audit.
- Do not remove old keys until deployed consumers are confirmed migrated.
- Do not assume restoring a revision also publishes it.
- Never store secrets in experience configs.
