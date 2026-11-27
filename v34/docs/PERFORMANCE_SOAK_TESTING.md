# V34 Performance Soak Testing

## What V34 adds beyond V29

V29 supplies static review leads, device budgets, and comparison of individual captures. V34 adds:
- Long-session, time-ordered samples with fixed environment metadata.
- Server-age and connected-client tracking to identify workload confounders.
- Linear growth diagnostics for server memory, Lua heap, and instance count.
- Repeated benchmark cohorts (at least three baseline and three candidate runs).
- Matched-condition checks and median-of-runs comparisons.

## Capture protocol

1. Choose the relevant side: server or client.
2. Choose a repeatable scenario: idle server soak, steady gameplay, high activity, join/leave churn, asset streaming, spawn/respawn, or round transitions.
3. Keep player count and network profile stable.
4. Run a warm-up before measured samples.
5. Collect at least five samples over at least 75% of the planned measured window.
6. Include server age, connected-client count, and the same metric set in each sample.
7. Store raw detailed evidence only in an authorized project store and put an opaque evidence reference in the capture.

## Analyze

From the cumulative V34 package root:

    python .\v34\tools\v34.py validate-capture --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json
    python .\v34\tools\v34.py analyze-soak --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json --output .codex/reports/v34-soak-analysis.json

The analyzer fits a simple least-squares line against server age and reports the estimated per-hour slope, first-to-last change, and R-squared. It emits a growth signal only when the workload is sufficiently stable, the fit is strong enough, and the configured growth threshold is exceeded.

A trend is not proof of a memory leak. Confirm with repeated runs, Developer Console categories (LuaHeap, InstanceCount, PlaceScriptMemory), and object/connection lifecycle inspection.

## Repeated-run comparison

Use at least three captures per build under equivalent conditions. Copy v34/examples/repeat-suite.example.json into the project and replace the illustrative paths with actual captures:

    python .\v34\tools\v34.py validate-suite --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json
    python .\v34\tools\v34.py compare-repeated --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json --output .codex/reports/v34-repeated-comparison.json

Use --fail-on-regression when a CI job should return a non-zero exit code after a measured regression crosses the manifest threshold. This only evaluates supplied JSON evidence; it does not run Roblox Studio.

## Data and safety boundaries

No player identities, usernames, raw chat, voice recordings, credentials, private server identifiers, arbitrary logs, or free-form notes belong in a capture. The validator requires opaque evidence references. It never contacts Roblox, writes to production DataStores, changes the game, or accesses the Creator Dashboard.
