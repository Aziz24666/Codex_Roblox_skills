# Roblox Codex Game Studio Kit — V33

V33.0.0 is the complete cumulative V1-V33 package with **236 native Codex skills**.

## V33 additions

- Four native Codex skills for Studio test orchestration, multiplayer regression testing, device/input compatibility, and evidence-based QA triage.
- v33/tools/v33.py commands:
  - doctor: inspect local Luau inventory and optional tools.
  - audit: bounded read-only source and test-file inventory.
  - validate-plan: validate unique test IDs, scenarios, categories, client limits, platforms, and execution modes.
  - validate-report: validate the report against its plan, require one result per planned test, and reject unsafe free-form/identity fields.
  - compare: compare baseline/current reports to identify regressions, newly blocked tests, coverage gaps, and improvements.
- Two JSON schemas, two examples, four testing guides, 33 regression tests, cumulative package patcher/auditor, and a V1-V33 quality workflow.
- Cumulative package target: **236 native skills**.

## Quick start

From the extracted V33 package root:

    python .\v33\tools\v33.py doctor --root C:\Path\To\YourGame
    python .\v33\tools\v33.py audit --root C:\Path\To\YourGame
    python .\v33\tools\v33.py validate-plan --root C:\Path\To\YourGame --plan .codex/qa/test-plan.json
    python .\v33\tools\v33.py validate-report --root C:\Path\To\YourGame --plan .codex/qa/test-plan.json --report .codex/qa/test-report.json
    python .\v33\tools\v33.py compare --root C:\Path\To\YourGame --plan .codex/qa/test-plan.json --baseline .codex/qa/baseline-report.json --current .codex/qa/current-report.json

Start with the examples in v33/examples/. A report must include one result for every planned test. Blocked and not_run statuses are not passes.

## Studio execution boundary

The CLI is offline and does not launch Studio or contact Roblox services. Use Studio Test/Run, Server & Clients, Device Simulator, Controller Emulator, Network Simulator, and supported Studio-only services for actual testing. StudioTestService supports up to eight simulated clients and is plugin-facing; StudioDeviceSimulatorService and VirtualInput also have documented Studio execution restrictions. See docs/ for details.

A report validates structure and consistency only. It cannot prove that external evidence is genuine or that a Studio test actually ran. CI runs the Python tests, audits, and archive checks, not Roblox runtime simulations.

All V1-V32 safeguards remain cumulative, including the mandatory no-gambling policy.
