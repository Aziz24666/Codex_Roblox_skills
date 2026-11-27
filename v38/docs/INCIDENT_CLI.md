# V38 incident CLI

Python 3.10+; no third-party packages required.

```powershell
python .\v38\tools\v38.py doctor --root C:\Path\To\YourGame
python .\v38\tools\v38.py validate --root C:\Path\To\YourGame --incident .codex\incidents\incident.json
python .\v38\tools\v38.py audit --root C:\Path\To\YourGame --incident .codex\incidents\incident.json --output .codex\reports\incident-audit.json
```

The incident path and output path must be safe project-relative paths. The input is bounded to 1 MiB. Duplicate object keys and non-standard JSON constants are rejected. Timestamps must include a timezone and events must be chronological.

The validator checks schema, bounded fields, unique IDs, role/severity requirements, service categories, aggregate audience scope, privacy-review attestations, evidence reference shapes, action approval/verification gates, communication review, and closure requirements.

`audit` writes a JSON report with warnings and recommended next steps. A non-resolved incident can pass validation and still need human action.

## Exit codes
- 0: doctor/validation pass, or audit report written.
- 1: schema or policy validation failures.
- 2: invalid root/path, unreadable input, or unsafe output.

## Important limits
No live telemetry access, Roblox service calls, PII scanning, reference authentication, action execution, rollback, DataStore restore, alerts, or player messaging. A pass is not a production authorization.
