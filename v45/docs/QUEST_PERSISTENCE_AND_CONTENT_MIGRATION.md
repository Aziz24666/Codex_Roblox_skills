# Quest persistence and content migration

Persist progress by stable quest and objective IDs, not localized labels, array positions, Instance names, or copies of the catalog. Keep authored content versioned independently from player profiles.

When content renames or removes an ID, provide an explicit deterministic migration. Decide whether active progress is preserved, mapped to a compatible replacement, or retired with a reviewed explanation. Test migrations on disposable profiles before rollout.

Quest/dialogue transitions are server-owned and idempotent. Duplicate events, reconnect retries, stale clients, and recovery must not duplicate durable effects. Use V40 profile, migration, and reward receipt guidance rather than a parallel persistence layer.

V45 does not inspect live profiles or execute migrations. Test actual Luau, recovery, stale UI, and old-content compatibility in a private experience.
