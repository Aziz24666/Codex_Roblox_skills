# Release evidence, rollback, and incident response

## Evidence quality

Each evidence item should identify the candidate source revision, environment, test place or scenario, test date/time with timezone, tool/build version, expected result, observed result, owner, and known limitations. Prefer concise machine-readable reports plus a short human interpretation.

Mark a gate passed only after the corresponding work has actually run and a reviewable evidence file exists. Use `blocked`, `failed`, `not_run`, or `not_applicable` honestly. A plan, checklist, screenshot of an empty test window, or generated test template is not execution evidence.

The V30 validator verifies file presence and optional SHA-256 integrity. It cannot authenticate the author, timestamp, Studio session, device, dashboard, or origin of an artifact. Keep evidence sanitized and never attach API keys, access tokens, private player data, or production DataStore exports.

## Rollback preparation

Before a production release, document:

1. The last known-good version and the exact condition that triggers rollback.
2. The person authorized to stop rollout and the person authorized to approve restoration.
3. The reversible application/configuration changes and any changes that are not safely reversible.
4. How to disable or route around a faulty feature while preserving player data.
5. How to communicate status to the team and players without exposing private data.
6. The evidence from an isolated rollback rehearsal.

A backup reference must identify a verified, recoverable backup location or approved backup record. A filename alone is not proof that a backup is restorable. Do not rehearse a production restore against live player data.

## Persistent-data changes

Treat schema changes and data migrations as a separate release risk. Define compatibility between old and new server versions, idempotency, retry behavior, partial completion handling, backup verification, and a tested recovery strategy. Use synthetic data in isolated test environments. Production migrations require explicit owner approval and the extra `migration_validation` gate. V30 validates the declaration and evidence reference; it never executes a migration or accesses a DataStore.

## Incident response

When a release causes unexpected player impact:

- Stop further rollout and preserve the current candidate identity and logs.
- Determine the scope using aggregate, privacy-respecting signals; do not expose individual player data in public reports.
- Compare observed behavior with the release's declared changes and known-good baseline.
- Follow the pre-approved rollback or mitigation plan. Do not improvise destructive DataStore changes.
- Record decisions, timestamps, affected systems, mitigations, and unresolved risks.
- Verify recovery with functional, multiplayer, persistence, security, and performance checks before resuming rollout.
- Produce a short post-incident review with root cause, contributing factors, prevention work, and owners.

A rollback is not always a simple code revert. Persistent schema changes, external configuration, and already-granted entitlements may require a compatible forward fix. Plan these separately and obtain the required human approvals.
