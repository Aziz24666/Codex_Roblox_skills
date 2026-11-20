---
name: roblox-persistence-migration-testing
description: Design and test versioned Roblox data migrations with deterministic transforms, isolated fixtures, retries, and rollback plans.
---

## Mandatory current-source research gate

Before substantive implementation, perform fresh online research using the current official Roblox Creator Hub/API documentation and relevant Roblox platform updates, deprecations, security guidance, or release notes. Check upstream documentation for any external tool or framework involved. Compare viable approaches when an API, architecture, or platform behavior is version-sensitive. Record exact source URLs, access dates, verified claims, alternatives, decisions, and the verification plan in `research/decisions/`. Re-open sources for each new task; previous research is background, not a substitute for current verification. Never invent a citation or claim a source was checked when it was not. If a critical platform or tool claim cannot be verified, mark the affected implementation `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing.

# Roblox Persistence and Migration Testing

## When to use
Use when changing saved player profiles, DataStore keys, persistent schemas, ordered data, session handling, or migration code. Do not access live player data for convenience.

## Procedure
1. Identify the persistence service, key format, schema version, serialization format, session/lock strategy, retry policy, and read/write call sites.
2. Research current official Roblox documentation for the exact APIs and limits being used. Record the source and date in project research notes.
3. Define a versioned schema and explicit migration path from every supported prior version.
4. Keep migration functions deterministic and side-effect free where practical. Separate transformation from the final persistence write.
5. Define behavior for missing, malformed, partially written, newer-than-supported, and unknown-version records.
6. Test synthetic fixtures: fresh profiles, every supported historical version, edge values, corrupted fields, repeated migrations, and unknown future versions.
7. Test retry, throttling, duplicate request, session conflict, timeout, partial failure, and safe resume behavior with mocks or explicitly isolated environments.
8. Verify idempotency: repeating the same migration must not corrupt or unexpectedly change already migrated data.
9. Document backup/rollback strategy and when rollback requires a forward migration.
10. Keep staging and production identifiers separate. Require explicit authorization and the appropriate environment before live reads, writes, or migration.

## Pitfalls and fixes
- Migration depends on live data: build synthetic fixtures representing the required old versions.
- Partial writes: design a version marker and recovery path matching the actual storage API.
- Unknown newer version: stop safely; do not overwrite data the current code cannot understand.
- Retry duplicates an update: design idempotent operations and test replay behavior.

## Output contract
Provide schema versions, migration matrix, test cases, isolation proof, retry/session behavior, rollback plan, and checks actually run. A mock is not evidence of live DataStore behavior.
