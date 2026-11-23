# Roblox Codex Game Studio Kit — V33

V33.0.0 is the complete cumulative V1-V33 package with 236 native Codex skills.

## V33 additions

- Four native Codex skills for Studio test orchestration, multiplayer regression testing, device/input compatibility, and evidence-based QA triage.
- v33/tools/v33.py:
  - doctor: inspect local Luau inventory and optional developer tools.
  - audit: create a bounded, read-only test/source inventory.
  - validate-plan: validate a privacy-minimal, repeatable test plan.
  - validate-report: validate a complete run report against its plan.
  - compare: compare two reports and identify regressions, improvements, blocked tests, and coverage gaps.
- Two JSON schemas, two examples, four guides, regression tests, cumulative package patcher/auditor, and a V1-V33 release workflow.
- Cumulative package target: **236 native skills**.

## Quick start

From the extracted V33 package root, run:

    python .\v33\tools\v33.py doctor --root C:\Path\To\YourGame
    python .\v33\tools\v33.py audit --root C:\Path\To\YourGame
    python .\v33\tools\v33.py validate-plan --root C:\Path\To\YourGame --plan .codex/qa/test-plan.example.json
    python .\v33\tools\v33.py validate-report --root C:\Path\To\YourGame --plan .codex/qa/test-plan.json --report .codex/qa/test-report.json
    python .\v33\tools\v33.py compare --root C:\Path\To\YourGame --plan .codex/qa/test-plan.json --baseline .codex/qa/baseline-report.json --current .codex/qa/current-report.json

Copy the examples from v33/examples/ into your project's .codex/qa/ directory, then tailor the fixed scenario codes and test IDs to the project.

## Important execution boundary

The CLI is offline. It does not launch Roblox Studio, execute Luau, connect to Roblox, simulate input, contact live servers, or prove that a game works. Its audit is a bounded source inventory, not a Luau parser or runtime test. Use Roblox Studio's Test, Server & Clients, Device Simulator, Controller Emulator, Network Simulator, StudioTestService, and VirtualInput where supported. Record only test IDs, fixed result codes, timestamps, environment codes, and opaque evidence references; do not put player IDs, usernames, raw chat, credentials, private logs, or arbitrary player data into reports.

StudioTestService, StudioDeviceSimulatorService, and VirtualInput are Studio-only capabilities. CI can test the toolkit's Python validators and package integrity, but cannot claim Studio simulation passed unless a separate authorized Studio run actually occurred.

All V1-V32 safeguards remain cumulative, including server authority, privacy-safe analytics, player safety, human-reviewed moderation, fair monetization, disclosed fixed paid outcomes, and the mandatory no-gambling policy.
