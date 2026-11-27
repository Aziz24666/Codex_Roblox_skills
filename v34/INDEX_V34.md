# Roblox Codex Game Studio Kit — V34

V34.0.0 is the complete cumulative V1-V34 package with **240 native Codex skills**.

## V34 additions

- Four native skills for performance soak testing, memory trend analysis, profiler evidence triage, repeated benchmark comparisons, and live rollout monitoring.
- v34/tools/v34.py commands:
  - doctor: inspect local tools and the presence of project evidence files.
  - validate-capture: validate time-ordered, privacy-minimal performance captures.
  - analyze-soak: calculate memory/instance growth trends and identify workload instability.
  - validate-suite: validate a repeatable benchmark manifest and every referenced capture.
  - compare-repeated: compare at least three baseline and three candidate runs under matched conditions.
- Two JSON schemas, two examples, three guides, 48 regression tests, cumulative package patcher/auditor, and the V1-V34 quality workflow.

## Quick start

    python .\v34\tools\v34.py doctor --root C:\Path\To\YourGame
    python .\v34\tools\v34.py validate-capture --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json
    python .\v34\tools\v34.py analyze-soak --root C:\Path\To\YourGame --capture .codex/perf/soak-run.json --output .codex/reports/v34-soak-analysis.json
    python .\v34\tools\v34.py validate-suite --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json
    python .\v34\tools\v34.py compare-repeated --root C:\Path\To\YourGame --manifest .codex/perf/repeat-suite.json --output .codex/reports/v34-repeated-comparison.json

V34 builds on V29's static review, device budgets, and individual-capture comparison. It adds long-duration trend validation and repeated benchmark cohorts; it does not replace V29.

## Verification boundary

V34 is an offline Python tool. It validates structured aggregate evidence supplied by the project and computes repeat/trend summaries. It does not launch Studio, capture profiler dumps, execute Luau, access the Creator Dashboard, read live telemetry, or change rollout settings. Detailed evidence stays in authorized project storage and is referenced by opaque IDs.

A positive memory trend is a diagnostic signal, not proof of a memory leak. A benchmark regression is a review signal, not automatic evidence of causality. Preserve all V1-V33 safeguards, including server authority, privacy, player safety, human-reviewed moderation, transparent monetization, and the mandatory no-gambling rule.
