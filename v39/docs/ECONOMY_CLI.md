# V39 economy CLI

Python 3.10+; standard library only.

```powershell
python .\v39\tools\v39.py doctor --root C:\Path\To\YourGame
python .\v39\tools\v39.py validate --root C:\Path\To\YourGame --model .codex\economy\economy-model.json
python .\v39\tools\v39.py simulate --root C:\Path\To\YourGame --model .codex\economy\economy-model.json --output .codex\reports\economy-simulation.json
```

The input is a project-relative JSON path and is limited to 1 MiB. Duplicate object keys, non-standard JSON constants, unknown fields, path traversal, and symlink paths are rejected. Simulation horizon and model dimensions are bounded.

The report is generated using deterministic integer arithmetic. Run with the same model to get the same report. Output paths must be safe project-relative paths and are written atomically.

## Exit codes
- 0: doctor, validation, or simulation succeeded.
- 1: model validation failed.
- 2: invalid root/path, unreadable input, or unsafe output.

## Limits
No Roblox API/telemetry/Studio/purchase access, no player data, no revenue or retention prediction, no random outcome modeling, and no automatic economy tuning. The output is a deterministic scenario, not evidence of production behavior.
