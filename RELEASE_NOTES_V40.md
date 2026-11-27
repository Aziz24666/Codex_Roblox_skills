# V40.0.0 — Advanced Data Persistence and Transaction Integrity

## Added
- Four native Codex skills for profile lifecycle/session ownership, resilient persistence/recovery, safe schema migrations, and idempotent rewards/receipt processing.
- Offline persistence contract validator and design auditor.
- Strict JSON validation, duplicate-key rejection, bounded inputs, safe project-relative paths, symlink rejection, and atomic report writing.
- Explicit DataStore budget, UpdateAsync, session-lock lease, autosave, bounded retry/backoff/jitter, shutdown, migration-chain, field-budget, and transaction-idempotency contracts.
- JSON Schema, example model, regression suite, documentation, cumulative patcher/auditor, and CI release workflow.

## Cumulative package
V1–V40, 264 native Codex skills. Download only the V40 package.

## Limitations
The CLI only validates supplied metadata. It does not access Roblox services, connect to DataStores, inspect project Luau, run live migrations, grant rewards, or process receipts. A green audit does not prove production safety, data preservation, or actual implementation correctness. Use a separate test experience, backups, human review, and real failure-injection tests before production.
