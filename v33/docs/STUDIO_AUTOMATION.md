# Studio Automated Testing

## Supported test surfaces

Roblox Studio provides interactive Test, Test Here, Run, Server & Clients, Device Simulator, Controller Emulator, and Network Simulator modes. The Creator Hub also documents the Studio-only services StudioTestService, StudioDeviceSimulatorService, and VirtualInput. The V33 skills distinguish these runtime surfaces from offline source and JSON checks.

## A maintainable test architecture

Use a plugin to choose and launch scenarios, a server-side test fixture to inspect authoritative state and end the session, and client-side fixtures to perform client assertions. Keep test-only scripts and assets in a clearly separated location. Do not place plugin-only APIs in published game scripts.

For multiplayer test sessions, StudioTestService:ExecuteMultiplayerTestAsync is plugin-facing and yields until the test ends. It accepts 1-8 simulated clients and an optional Roblox-serializable argument. It cannot be called from within an already-running test, and only one multiplayer session can run in one Studio instance. Run a long call in a spawned task so the plugin remains responsive.

The server DataModel owns AddPlayers and EndTest. Client DataModels own CanLeaveTest and LeaveTest. GetTestArgs has a currently documented client LocalScript issue, so read the test argument on the server and pass explicitly scoped fixture state to clients.

## Example orchestration pattern

The plugin selects a fixed test scenario, disables its launch control while the run is active, and invokes ExecuteMultiplayerTestAsync inside a task. It applies a watchdog timeout, catches errors, restores plugin UI state, and reports a fixed outcome. The server fixture checks the test argument, waits for the required player lifecycle event, asserts the expected server state, then ends the test with a fixed result. The client fixture waits for game load and performs its bounded client assertions. Keep this pattern small and isolated; adapt it to the exact Studio API version.

## Test cases to include

- Solo smoke test for boot, spawn, first UI, and clean stop.
- Multi-client join and replication.
- Join-in-progress and leave-in-progress.
- Respawn and cleanup.
- Invalid remote request rejected without state mutation.
- Data round trip in a dedicated test environment.
- Timeout and error handling in the test harness itself.

## What CI can verify

GitHub Actions can run Python unit tests, schema validation, static checks, cumulative audits, archive integrity checks, and report comparison. Do not claim the CI run executed StudioTestService or a real Roblox playtest unless an explicitly configured Studio runner actually ran and produced evidence.

## Links

- Roblox Studio testing modes: https://create.roblox.com/docs/studio/testing-modes
- StudioTestService: https://create.roblox.com/docs/reference/engine/classes/StudioTestService
- TestService: https://create.roblox.com/docs/reference/engine/classes/TestService
