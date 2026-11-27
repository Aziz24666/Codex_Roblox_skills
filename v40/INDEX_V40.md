# V40 source index

Version: 40.0.0

## Components
- Four native Codex skills for profile lifecycle/session ownership, resilient saving, migrations, and idempotent transaction handling.
- `tools/v40.py`: offline persistence contract validator/auditor.
- `schemas/persistence-model.schema.json`: model contract.
- `examples/persistence-model.example.json`: synthetic project model.
- `tests/test_v40.py`: validation, migration, transaction, audit, and path-safety tests.
- `docs/`: architecture, migration/receipt guidance, and CLI reference.

## Commands
- `doctor`: verify Python and project root.
- `validate`: validate a persistence contract.
- `audit`: produce a structured warning report.

## Trust boundary
This tool validates supplied JSON metadata, not a Roblox experience. It does not connect to DataStoreService, inspect or execute Luau, read player data, run migrations, process receipts, or authenticate evidence. A valid model is not proof that code follows the model. Never use live production data in routine Studio testing.
