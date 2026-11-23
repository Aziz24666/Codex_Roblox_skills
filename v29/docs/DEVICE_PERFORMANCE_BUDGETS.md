# Device-specific performance budgets

Use explicit budgets for each supported device class rather than one average target. The example file at `v29/tools/performance-budgets.example.json` provides illustrative ceilings only; it is not a Roblox guarantee or a universal recommendation.

## Configure and validate

Copy the example JSON into the game project's `.codex` directory, tune it from repeatable measurements, and validate it:

```powershell
python ".\v29\tools\v29.py" budget --root "C:\Path\To\YourGame" --config ".codex\performance-budgets.json"
```

Budgets are upper limits for the metrics supplied. A metric absent from a profile is not evaluated. Select limits appropriate to the game, scene complexity, player count, and target devices. Keep frame-time percentile and memory targets especially explicit for constrained mobile devices.

## Recommended dimensions

- Frame time: use consistent percentile measurements, not just a single best frame.
- Memory: track sustained usage and growth over a realistic session.
- Load time: define the start/end event and test cold and warm loading consistently.
- Script CPU: identify the same Script Profiler interval and scenario in each capture.
- Replication: measure comparable server/player activity and avoid treating a low traffic sample as representative.

A budget violation is a review signal. Verify the test conditions and capture quality before deciding whether a change is required.
