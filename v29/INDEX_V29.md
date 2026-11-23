# Roblox Codex Game Studio Kit — V29

V29.0.0 is the cumulative V1-V29 release, extending V28 with performance profiling workflows, static Luau review leads, device-specific budgets, and comparison of externally captured measurement JSON.

## V29 additions

- Four native Codex skills for profiling, Luau optimization review, memory/assets, and performance regression evidence.
- `doctor`: inventory local Luau files and optional tool availability.
- `audit`: create a bounded, read-only heuristic report of possible hot-path patterns.
- `budget`: validate device-specific performance budget configuration.
- `compare`: compare baseline and candidate JSON captures for equivalent device profiles.
- `report`: combine existing audit and measurement comparison reports.
- JSON schemas, an example budget configuration, regression tests, cumulative package patching and auditing.

## Quick start

From the extracted cumulative kit root:

```powershell
python ".\v29\tools\v29.py" doctor --root "C:\Path\To\YourGame"
python ".\v29\tools\v29.py" audit --root "C:\Path\To\YourGame"
python ".\v29\tools\v29.py" budget --root "C:\Path\To\YourGame" --config ".codex\performance-budgets.json"
```

Copy and tune `v29/tools/performance-budgets.example.json` into the selected game project's `.codex` folder before running the budget command. Use the profiling guide to prepare matching capture JSON files before comparing builds.

## Important boundaries

- The static scanner is a text heuristic, not a Luau parser or profiler.
- V29 does not measure FPS, frame time, script CPU, memory, load time, or replication by scanning code.
- V29 does not connect to Roblox, execute Luau, launch Studio, read production data, mutate game source, or perform automatic optimization.
- Actual measurement evidence must be captured independently with Roblox Studio tools or a documented test harness on representative hardware.
- Keep server authority, DataStore protections, human approval for production changes, fair monetization, and no-gambling rules from earlier versions.
