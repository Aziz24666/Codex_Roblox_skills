# V33.0.0 — Automated QA and Regression Testing

V33 extends the cumulative V1-V32 Roblox Codex Game Studio Kit with repeatable test planning, Roblox Studio automation guidance, multiplayer/device/input regression scenarios, privacy-minimal run reports, and baseline comparison.

## New capabilities

- Four native Codex skills:
  - roblox-studio-automated-playtesting-v33
  - roblox-multiplayer-regression-testing-v33
  - roblox-device-and-input-testing-v33
  - roblox-test-evidence-and-defect-triage-v33
- v33/tools/v33.py commands:
  - doctor: inspect local Luau inventory and optional local tools.
  - audit: bounded read-only Lua/Luau test and Studio API inventory.
  - validate-plan: validate a structured QA test plan and the maximum of eight simulated clients.
  - validate-report: validate all results against the plan, status/outcome rules, timezones, and opaque evidence references.
  - compare: identify pass-to-fail regressions, newly blocked tests, coverage gaps, and improvements.
- Two JSON schemas, two sample plans/reports (including a local-static report), four guides, a cumulative package patcher/auditor, and 32 regression tests.
- Cumulative target: **236 native Codex skills**.

## Studio testing guidance

- Use Test/Run for solo checks and Server & Clients for actual client/server interaction.
- Use StudioTestService only from supported Studio plugin/test contexts; it is Studio-only, supports up to eight clients, and permits one multiplayer session per Studio instance.
- Use Device Simulator and Controller Emulator for supported device/input profiles.
- Use StudioDeviceSimulatorService and VirtualInput only within their documented Studio restrictions.
- Use Network Simulator to test selected latency, jitter, and packet-loss profiles.

## Evidence and honest verification

- Reports require one result for every planned test and distinguish pass, fail, blocked, and not_run.
- The comparison tool separates regressions from newly blocked tests and missing coverage.
- Reports reject unknown/free-form identity and evidence fields; they accept only fixed outcome codes and opaque evidence references.
- The offline CLI does not execute Studio, Luau, Roblox services, multiplayer sessions, or device/input simulation.
- GitHub Actions verifies the Python tools, repository/package audit, and generated archive integrity. Studio runtime behavior must be verified in an authorized Studio session and recorded separately.

All V1-V32 safeguards remain cumulative: server authority, privacy, player safety, human-reviewed moderation, fair and transparent monetization, fixed paid outcomes, and mandatory no-gambling requirements.
