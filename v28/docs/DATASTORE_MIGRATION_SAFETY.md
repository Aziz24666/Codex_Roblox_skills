# DataStore and Schema Migration Safety

## Keep the migration explicit

Persistent data evolves. Store a schema version with each profile or record and define deterministic, ordered transitions from one version to the next. Keep migration functions small, testable, repeatable, and independent of live services where possible.

A migration should preserve fields it does not own. Avoid replacing a complete profile with a partial default object. Define how missing, malformed, and unknown fields are treated. Make defaults explicit and distinguish absent values from valid zero/false values.

## Safer update behavior

Use atomic update patterns for concurrent profile changes. A transform supplied to UpdateAsync must be safe to run more than once: retries can occur, so do not perform external side effects inside the transform. Do not assume that a callback runs exactly once. Handle nil/invalid existing records deliberately and make conflict behavior clear.

Wrap service calls in protected error handling, use bounded retry/backoff behavior, monitor request budgets, and avoid tight retry loops. Do not swallow errors and report a save as successful when persistence failed. Respect the project's profile/session-locking strategy so concurrent servers cannot silently overwrite each other.

SetAsync and RemoveAsync are not automatically wrong, but deserve explicit review for overwrite or deletion semantics. Check whether concurrent writers, session ownership, and failure recovery are handled. Never infer safety from the method name alone.

## Required migration evidence

Before rollout, use synthetic data and verify:

- [ ] Each supported legacy schema version has a fixture and expected migrated output.
- [ ] Current-version records remain unchanged.
- [ ] Missing, malformed, oversized, and partially populated records have an explicit policy.
- [ ] Unknown fields are preserved unless a documented data-retention rule says otherwise.
- [ ] Re-running the migration produces the same result (idempotency).
- [ ] A failed step can be retried without duplicating external effects.
- [ ] Backup restore and rollback procedures have been rehearsed.
- [ ] Staging telemetry and a stop/rollback threshold are defined.
- [ ] Production rollout requires a separate human decision and a verified backup.

## V28 migration manifest

The validate-migration command validates a JSON plan; it does not execute any migration. A valid plan must declare environment as synthetic or staging, dry_run true, production_writes false, a verified backup strategy, a rollback plan, and a contiguous sequence of idempotent version transitions. Each transition must include named test cases of kinds valid, invalid, legacy, and repeat. Plans must set preserve_unknown_fields true.

Validation is a structural safety gate, not proof that the migration code is correct or that a backup can be restored. The human operator must independently verify the backup and staging environment.
