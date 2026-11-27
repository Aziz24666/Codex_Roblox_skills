# V40 persistence CLI

Python 3.10+; standard library only.

```powershell
python .\v40\tools\v40.py doctor --root C:\Path\To\YourGame
python .\v40\tools\v40.py validate --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json
python .\v40\tools\v40.py audit --root C:\Path\To\YourGame --model .codex/persistence/persistence-model.json --output .codex/reports/persistence-audit.json
```

Input must be a project-relative JSON file of at most 1 MiB. Duplicate keys, unsupported fields, non-standard JSON constants, path traversal, absolute paths, and symlink traversal are rejected. Reports use a project-relative output path and atomic replacement.

## Audit warnings
The auditor highlights very high declared payload budgets, autosave intervals that leave little margin under the session lease, and models without a receipt/transaction path. Warnings need human interpretation.

## Exit codes
- 0: doctor, validation, or audit completed successfully.
- 1: model contract invalid.
- 2: invalid root/path, unreadable input, or unsafe output.

## What the CLI does not do
It does not call Roblox APIs, inspect Luau files, execute migrations, test session-lock races, contact MarketplaceService, verify real backups, or write player data. A passing report is not an implementation certification.
