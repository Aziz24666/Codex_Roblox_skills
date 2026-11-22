# V26 Multiplayer, Device, and Network Testing

Updated 2026-11-22 against the official Roblox Creator Hub documentation.

## Test matrix

Start with the smallest test that can reveal the defect. Expand coverage only when the feature's risks require it.

| Pass | Studio mode | Coverage | Required evidence |
|---|---|---|---|
| A | Edit/static | Luau analysis, script contracts, project mapping | Compiler/linter output and changed-file list |
| B | One client | Basic entry, UI load, primary interaction, clean exit | Console output and focused screenshot |
| C | Two clients | Ownership, replication, trading/team/lobby flows where relevant | Both client observations and server output |
| D | Four clients | Join/leave sequencing and shared-state behaviour | Player count, server log, reproduction |
| E | Up to eight clients | Bounded multiplayer edge cases | Test result, server log, simulation limits |
| F | Device simulation | Phone, tablet, desktop, controller/orientation where relevant | Device profile and screenshots |
| G | Network simulation | Added latency, jitter, packet loss | Exact staged settings and observations |
| H | Evidence review | Re-run critical path and classify findings | Pass/fail/blocked table with evidence |

Eight simulated clients is StudioTestService's ceiling for one simulated multiplayer test session, not a recommendation that every feature needs eight clients or a substitute for production load testing.

## StudioTestService

Roblox documents StudioTestService as a plugin-facing testing service. It can launch a server and simulated clients, pass serializable arguments into a test, add clients during a session, and end a test with a result. A multiplayer test supports up to eight simulated clients, and only one multiplayer test session can run at a time per Studio instance.

Important constraints:

- `ExecuteMultiplayerTestAsync` is plugin-facing and must be called from a plugin script.
- It yields until the test finishes; a plugin may need a coroutine to remain responsive.
- It cannot be called from inside a running test.
- `AddPlayers` and `EndTest` are called from the server DataModel of an active test.
- Client leave/disconnect APIs have context restrictions; inspect the current API reference.

Do not put plugin-only APIs in a normal published server script and assume they will work.

## Device Simulator and VirtualInput

Use Device Simulator to check screen dimensions, density, orientation, platform-specific UI, keyboard overlap, and touch layout. Use controller emulation when supported.

Roblox's `StudioDeviceSimulatorService` exposes scriptable profile and viewport operations from supported Studio/plugin contexts. Some state-changing methods are restricted by DataModel mode; inspect the current API reference before calling them.

Roblox's `VirtualInput` simulates keyboard, mouse, and pointer events for testing. It is obtained through `UserInputService:CreateVirtualInput()`. It is not a general-purpose input automation facility for a published experience, and calls that affect Roblox CoreGui can error.

## Network Simulator

Roblox's Network Simulator can add latency, jitter, and packet loss to Studio playtest connections. Record values separately for inbound and outbound traffic; the configured delay adds to real connection conditions.

Test baseline conditions, moderate added latency, jitter that reveals timing/order assumptions, packet loss when relevant, and recovery after degraded conditions.

Network Simulator affects Studio playtests only. It does not change published experiences or live player connections. It is documented as a beta feature, so do not hard-code assumptions about its UI or API.

## Test isolation

- Prefer an unpublished test place or separate test universe.
- Use distinct test keys/namespaces and non-production DataStores.
- Use synthetic player data only.
- Never use production player accounts or live player state to validate a test.
- Avoid irreversible writes and purchases in automated test flows.
- Do not enable broad Open Cloud scopes merely to make a test pass.
- Clean up only test-owned records and only after verifying their namespace.

## Evidence contract

For each meaningful test, record place and Studio instance identity; test name/date/mode/client count; device profile/orientation; network settings; expected and observed results; relevant console output; screenshot/log references; evidence class; and known limitations. Classify each scenario as PASS, FAIL, BLOCKED, or NOT RUN. Never convert a skipped or unavailable scenario into a PASS.

## Sources

- [Roblox: Studio testing modes](https://create.roblox.com/docs/studio/testing-modes)
- [Roblox: StudioTestService API](https://create.roblox.com/docs/reference/engine/classes/StudioTestService)
- [Roblox: StudioDeviceSimulatorService API](https://create.roblox.com/docs/reference/engine/classes/StudioDeviceSimulatorService)
- [Roblox: VirtualInput API](https://create.roblox.com/docs/reference/engine/classes/VirtualInput)
- [Roblox: Network Simulator](https://create.roblox.com/docs/studio/network-simulator)
