---
name: roblox-studio-automated-playtesting-v33
description: Design repeatable Roblox Studio test plans and safely orchestrate scripted solo or multi-client tests with StudioTestService, TestService, explicit preconditions, bounded timeouts, and verifiable results.
---

# Roblox Studio Automated Playtesting

## Goal

Turn a feature request or bug report into a repeatable test plan, run the supported parts in Roblox Studio, and report exactly what was and was not executed. Prefer the smallest deterministic test that proves the expected behavior.

## Required workflow

1. Identify the behavior, risk, expected state, and authoritative owner before writing tests.
2. Read the relevant game scripts and existing test harness. Reuse project conventions rather than introducing a competing framework.
3. Separate static-local checks from Studio runtime tests. Do not label a static scan as playtesting.
4. Define test IDs, scenarios, preconditions, expected result codes, platform, client count, and execution mode before running anything.
5. Use Studio's Test or Run mode for solo behavior. Use Server & Clients for actual client/server interactions.
6. Use StudioTestService from a Studio plugin for scripted sessions where the API and permissions allow it. It is a Studio-only service; do not add it to live gameplay scripts.
7. Record every planned test as passed, failed, blocked, or not_run. A missing result is a reporting defect, not a pass.
8. Capture minimal evidence references and reproducible steps. Keep raw player data, credentials, unfiltered chat, private logs, and identity details out of QA reports.
9. Re-run affected tests after a fix, then re-run relevant regression coverage. Compare reports to detect previously passing tests that now fail.
10. State the boundary of verification: static, local unit, Studio solo, Studio multiplayer, device simulation, or published-experience validation.

## StudioTestService use

The plugin-facing StudioTestService can start a multiplayer session through ExecuteMultiplayerTestAsync, pass a Roblox-serializable argument to test scripts, add simulated players from the server DataModel, and finish through EndTest. The documented maximum is eight clients. ExecuteMultiplayerTestAsync can only be called from a plugin script, cannot be called while a test is already running, and yields until the test ends. Run long test calls in a task/coroutine so the plugin UI remains responsive. Only one multiplayer test session can run at once per Studio instance.

A sound architecture has three roles:

- Plugin: selects a named scenario, launches the test, applies an external timeout/watchdog, and records the returned result.
- Server test script: checks test arguments, verifies server-owned state, simulates permitted join/leave flows, and calls EndTest with a fixed result code.
- Client test script: waits for the game to load, performs client-side assertions or leaves when instructed, and never decides authoritative game state.

AddPlayers and EndTest must run from the active server DataModel. CanLeaveTest and LeaveTest are client-side. GetTestArgs currently has a documented client LocalScript issue; prefer reading the argument on the server and pass only the necessary test state through an explicit test fixture.

## Test design rules

- Prefer deterministic fixtures, fixed seeded test data, explicit cleanup, and bounded timeouts.
- Make every test independent or document its required order.
- Avoid depending on public servers, real players, live purchases, live moderation, or production DataStores.
- Use isolated test keys/stores only when a separate authorized environment is explicitly configured.
- Assert both the expected success path and important failure paths.
- Verify client presentation and server authority separately.
- Test one-client and multi-client behavior; a solo pass does not establish multiplayer correctness.
- Test reconnect, respawn, join-in-progress, and leave-in-progress when relevant.
- Never fabricate a passing result when Studio is unavailable or a test was skipped.

## Output

Deliver the test matrix, exact setup steps, test IDs, expected outcomes, actual result codes, untested areas, reproducible defects, and a clear verification boundary. Preserve the no-gambling policy and all earlier security, privacy, and player-safety safeguards.
