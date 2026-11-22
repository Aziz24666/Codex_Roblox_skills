---
name: roblox-datastore-migration-safety-v28
description: Design and review versioned, idempotent Roblox DataStore migrations using synthetic fixtures, verified backups, rollback planning, and staging validation.
---

# Roblox DataStore Migration Safety

## Goal

Plan safe schema evolution without exposing or changing live player data. Use synthetic fixtures and staging evidence.

## Workflow

1. Inventory keys, profile shapes, schema versions, concurrent-write/session-locking behavior, and the code paths that save data.
2. Define supported source versions and a contiguous target-version sequence. Document missing, malformed, partial, and unknown-field behavior.
3. Keep migration transforms deterministic and idempotent. Treat UpdateAsync callbacks as retryable; do not place external side effects inside a transform.
4. Preserve fields that the migration does not own and avoid replacing full profiles with partial defaults.
5. Validate each old-version fixture, current-version no-op, malformed input, repeat execution, partial failure, and rollback.
6. Verify a restorable backup and a human-readable rollback plan before any staged migration.
7. Use the V28 migration-manifest validator as a structural gate. Keep environment set to synthetic or staging, dry_run true, and production_writes false.
8. Require separate human review before a staged or production rollout. Keep production DataStore access out of routine automation.

## Review output

Provide version transition diagrams, fixture inventory, migration idempotency analysis, backup/rollback evidence, retry and request-budget behavior, deployment gates, and unresolved assumptions.

## Safety boundaries

Do not execute migrations, invoke Open Cloud, read or write production keys, export player records, or claim a backup is verified from a manifest declaration alone. Never log secrets, player identifiers, or complete player profiles.
