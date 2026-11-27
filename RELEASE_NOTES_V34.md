# V34.0.0 — Performance Soak Testing and Repeatable Benchmarks

V34 extends the cumulative V1-V33 Roblox Codex Game Studio Kit with long-session performance evidence, server-age-aware memory trends, repeated benchmark cohorts, and rollout monitoring guidance.

## New capabilities

- Four native Codex skills:
  - roblox-performance-soak-and-memory-trend-v34
  - roblox-microprofiler-capture-triage-v34
  - roblox-repeated-benchmark-and-regression-v34
  - roblox-live-performance-rollout-monitoring-v34
- v34/tools/v34.py commands:
  - doctor: inspect local tools and project root.
  - validate-capture: validate time-ordered performance captures, sample consistency, device/target metadata, and opaque evidence references.
  - analyze-soak: calculate least-squares resource trends, per-hour slopes, R-squared, connected-client stability, and thresholded growth signals.
  - validate-suite: validate a repeat-suite manifest and all referenced baseline/candidate captures.
  - compare-repeated: compare per-run medians and cohort medians across at least three baseline and three candidate runs, with configurable regression threshold and optional non-zero exit on a regression.
- Two JSON schemas, two examples, three engineering guides, 48 regression tests, cumulative package patcher/auditor, and a V1-V34 quality workflow.
- Cumulative target: **240 native Codex skills**.

## What is different from V29

V29 continues to provide source-pattern review, device-specific budget validation, and individual-capture comparison. V34 adds long-session time-series validation, server-age and workload stability checks, trend quality indicators, and repeated independent benchmark cohorts. V34 does not replace V29.

## Evidence and verification boundaries

- The CLI is offline and only processes supplied structured JSON. It does not start Studio, run Luau, collect MicroProfiler/Script Profiler data, access Creator Dashboard, or query live Roblox telemetry.
- A memory trend is a diagnostic signal, not proof of a memory leak.
- Repeated-run comparisons require matched test conditions and report medians; they are not formal statistical significance tests.
- Creator Dashboard live monitoring and any release pause/rollback remain separate, authorized, human-reviewed operations.

All V1-V33 safeguards remain cumulative: server authority, secure persistence, privacy, player safety, human-reviewed moderation, fair and transparent monetization, fixed paid outcomes, and mandatory no-gambling requirements.
