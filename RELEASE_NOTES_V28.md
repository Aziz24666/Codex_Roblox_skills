# V28.0.0 — Server Authority, DataStore Safety, and Multiplayer Reliability

V28.0.0 extends the cumulative V1-V27 Roblox Codex Game Studio Kit with a defensive local review workflow for client/server boundaries, persistence, and multiplayer reliability.

## New capabilities

- Add three native Codex skills:
  - roblox-server-authority-review-v28
  - roblox-datastore-migration-safety-v28
  - roblox-multiplayer-reliability-validation-v28
- Add v28/tools/v28.py with:
  - doctor: inspect local Luau inventory and optional CLI availability without contacting Roblox services.
  - audit: produce a read-only JSON report of statically named remote calls/handlers, nearby validation/ownership/rate-limit/idempotency signals, high-impact operation tokens, DataStore APIs, and migration/retry/backup signals.
  - validate-migration: validate a human-authored manifest for synthetic/staging-only dry runs, explicit non-production writes, verified-backup declaration, rollback plan, contiguous schema versions, idempotency, and valid/invalid/legacy/repeat test cases.
- Add a security report schema, migration manifest schema/example, regression tests, cumulative package patcher/auditor, and documentation.

## Safety and reliability

- Treat client input as untrusted and keep important game state authoritative on the server.
- Require server-side validation, ownership and permission checks, cooldown/rate-limits, and idempotent handling for retryable high-impact operations.
- Keep DataStore migrations versioned, repeatable, field-preserving, tested with synthetic fixtures, backed up, and rollback-planned.
- Keep production DataStore writes, Open Cloud operations, publishing, and player-impacting changes behind explicit human approval.
- V28 does not connect to Roblox, execute migrations, access DataStores, mutate source scripts, or generate exploit instructions.
- Preserve V1-V27 functionality, sustainable monetization practices, and all no-gambling requirements.

## Validation

- V28 tests cover remote pairing and heuristic signals, DataStore API classification, migration manifest safety rules, path containment, symlink handling, and idempotent package integration.
- The cumulative package audit requires 216 native skills and all V28 deliverables.
- The V28 workflow reconstructs and validates the cumulative V1-V28 package, runs inherited regression/audit steps, checks archive equivalence, and verifies SHA-256 checksums.
- All inherited V14-V27 workflow checks remain active.

## Compatibility

- V28 adds files and commands; it does not change the V25 checkpoint format, V26 Studio MCP utility, or V27 Luau/Rojo commands.
- The report and manifest validator use Python's standard library and do not require Roblox service credentials or a live Studio connection.
