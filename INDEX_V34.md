# Roblox Codex Game Studio Kit — V34

V34.0.0 is the complete cumulative V1-V34 package with **240 native Codex skills**.

## V34 additions

- Four native skills for performance soak testing, memory trend analysis, profiler evidence triage, repeated benchmark comparisons, and live rollout monitoring.
- Offline CLI commands: doctor, validate-capture, analyze-soak, validate-suite, compare-repeated.
- Long-session time-series capture schema and server-age-aware growth analysis.
- Repeat-suite manifest that requires at least three baseline and three candidate captures under matched conditions.
- Median-of-runs comparison, workload consistency checks, and optional fail-on-regression exit behavior.
- Two JSON schemas, two examples, three guides, 48 regression tests, cumulative patcher/auditor, and a V1-V34 quality workflow.

## Quick start

From the extracted V34 package root:

    python .\v34\tools\v34.py doctor --root C:\Path\To\YourGame
    python .\v34\tools\v34.py validate-capture --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json
    python .\v34\tools\v34.py analyze-soak --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json --output .codex/reports/v34-soak-analysis.json
    python .\v34\tools\v34.py validate-suite --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json
    python .\v34\tools\v34.py compare-repeated --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json --output .codex/reports/v34-repeated-comparison.json

Copy the example capture and repeat-suite manifest from v34/examples/. Replace all illustrative paths/build labels with real project captures before running validate-suite or compare-repeated.

## Difference from V29

V29 remains responsible for static review hints, device budgets, and individual capture comparisons. V34 adds soak time series, server age and workload consistency analysis, and repeated independent benchmark cohorts.

## Verification boundaries

V34 validates supplied evidence. It does not launch Studio, capture profiler data, execute Luau, access the Creator Dashboard, or change rollout settings. A growth signal is not proof of a memory leak; a benchmark regression requires human review. All V1-V33 safety, privacy, security, moderation, fair-monetization, and no-gambling safeguards remain cumulative.
