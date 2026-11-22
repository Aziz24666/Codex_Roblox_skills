# Roblox Codex Game Studio Kit — V28

V28.0.0 is the cumulative V1-V28 release. It extends V27 with a defensive security and multiplayer reliability review workflow.

## V28 additions

- Three native Codex skills for server-authority review, DataStore migration safety, and multiplayer reliability validation.
- doctor: inspect source inventory and local test-tool availability without contacting Roblox services.
- audit: create a read-only JSON report covering statically named remotes, server-handler safeguards, high-impact operations, DataStore API usage, migration/retry/backup signals, and review priorities.
- validate-migration: validate a human-authored migration manifest for synthetic/staging-only dry runs, sequential schema transitions, idempotency, backup and rollback declarations, and positive/negative/repeat test coverage.
- Bounded Luau scanning, symlink/path-containment checks, safe atomic report writes, and explicit heuristic limitations.

## Quick start

Run these commands from the extracted toolkit root in PowerShell:

    python ".\v28\tools\v28.py" doctor --root "C:\Path\To\YourGame"
    python ".\v28\tools\v28.py" audit --root "C:\Path\To\YourGame"
    python ".\v28\tools\v28.py" audit --root "C:\Path\To\YourGame" --force
    python ".\v28\tools\v28.py" validate-migration --root "C:\Path\To\YourGame" --manifest ".codex\migration-plan.json"

The report is written to .codex/reports/v28-security-reliability-report.json. Review the findings against the real Roblox Studio DataModel and code before changing anything.

## Security and migration principles

- Treat every value supplied by a client as untrusted. The server independently validates types, ranges, ownership, permissions, game state, and request frequency before applying important changes.
- The server computes authoritative currency, damage, rewards, inventory, purchases, and progression. A client request is an intent, not proof that an outcome is valid.
- Make critical requests rate-limited and safe to retry. Use request/receipt identity and idempotent server-side handling where appropriate.
- Version persistent data explicitly. Test legacy, valid, invalid, repeated, partial, and rollback cases with synthetic data before a staged rollout.
- Keep backups, rollback plans, unknown-field preservation, and human review. Never point validation or routine automation at production DataStores.
- Do not automatically run migrations, invoke Open Cloud, write DataStores, publish places, or alter live player data.
- Preserve the toolkit's fair-monetization and no-gambling requirements.

## Boundaries

V28 scans local source text only. It does not connect to Roblox, emulate the server, execute migration code, infer full Luau control flow, prove security, or claim that a Studio multiplayer test has run. Findings are advisory review signals, not exploit demonstrations or a substitute for Studio testing.
