---
name: roblox-safe-profile-schema-migrations
description: Plan backward-aware, idempotent Roblox profile schema migrations with backups, dry runs, and recovery.
---

# Roblox safe profile schema migrations

## Workflow
1. Record the current profile schema version and the minimum version still supported.
2. Define a linear migration chain with one version step per migration.
3. Make each step idempotent, bounded, and safe to retry after interruption.
4. Preserve fields not explicitly owned by the migration.
5. Create and verify a recoverable backup/snapshot before modifying production data.
6. Dry-run against representative copied fixtures from every supported prior version.
7. Test missing, malformed, partial, already-migrated, and unexpectedly newer profiles.
8. Persist the new profile value before marking the version as current.
9. Prepare a forward-fix or manual recovery path; do not blindly downgrade a partially migrated schema.

## Deliverables
Migration table, old/new schema examples, fixture set, dry-run report, backup reference, rollout gates, recovery plan, and human approval record.

## Safeguards
Never test migrations against live production data from Studio. Use a separate test experience and sanitized fixtures. Do not silently discard unknown fields, inventory, currency, entitlements, or player progress.
