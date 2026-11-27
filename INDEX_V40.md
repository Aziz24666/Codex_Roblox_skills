# Roblox Codex Game Studio Kit — V40

V40.0.0 is the cumulative V1–V40 package with **264 native Codex skills**. Download only the current release.

## V40 additions — advanced data persistence and transaction integrity
- Profile lifecycle and exclusive session ownership.
- Resilient saves, retry/backoff, request budgeting, and shutdown recovery.
- Safe, linear, repeatable profile-schema migrations.
- Idempotent reward and developer-product receipt processing.
- An offline persistence-contract validator and auditor.
- JSON Schema, representative model, docs, regression tests, cumulative patcher/auditor, and release workflow.

## Commands
```powershell
python .\v40\tools\v40.py doctor --root C:\Path\To\YourGame
python .\v40\tools\v40.py validate --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json
python .\v40\tools\v40.py audit --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json --output .codex/reports/persistence-audit.json
```

## Boundaries
The CLI validates declared persistence architecture metadata only. It does not connect to Roblox, read or write DataStores, inspect Luau, implement session locks, run migrations, process receipts, or verify transaction settlement. Receipt processing must be designed so the unique purchase ID, grant, and deduplication marker are persisted in one atomic profile-key update where possible, and acknowledgement happens only after durable commit. This does not make unrelated keys transactional. Test in a separate published test experience before production. Never enable Studio API access against live production data for routine testing.
