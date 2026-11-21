# V19 Roblox Studio and Multiplayer Test Automation

V19 distinguishes local static CI from tests that require the actual Roblox Studio runtime.

## StudioTestService

Roblox documents \`StudioTestService\` as a Studio service that plugins can use to automate Test and Run mode testing. Its documented surface includes \`ExecutePlayModeAsync\`, \`ExecuteRunModeAsync\`, \`ExecuteMultiplayerTestAsync\`, \`AddPlayers\`, \`GetTestArgs\`, \`EndTest\`, and \`LeaveTest\`.

Use a plugin-owned test launcher and bounded scenarios. A multiplayer test can coordinate:
1. a Studio plugin that starts the test and supplies scenario arguments;
2. a server-side test script that controls assertions and completion;
3. client-side test scripts that participate in the scenario.

Prioritize cases that are difficult to validate with a single client: lobby join/leave, matchmaking transitions, party membership, replicated state, server-authoritative rewards, ownership checks, disconnect/reconnect, and teleport flows where the environment permits.

Read the current API reference before implementing a plugin. Do not assume service methods or behavior beyond what the version of Studio currently exposes.

## Studio MCP

The built-in Studio MCP server can expose tools for inspecting and editing scripts, discovering connected Studio instances, running Luau commands, and playtesting. Discover the connected Studio instance and target its explicit ID before any action. Treat edit, save, upload, and publish capabilities as separate actions with appropriate approval.

Studio MCP is a connection to a user's open Studio session; it is not automatically available to GitHub Actions or to every Codex client. Never state that a Studio test ran unless the connected environment returned its result.

## Test fixture and data isolation

- Use a dedicated test place or isolated test configuration.
- Never point automated tests at production DataStores by assumption.
- Make fixtures repeatable and uniquely identified.
- Clean up only test-owned data.
- Keep test accounts, product identifiers, and place IDs explicit and authorized.
- Do not perform real purchases or production writes as part of ordinary CI.

## Reporting

Record Studio version, place/build identity, client count, scenario, expected result, observed result, logs/output, and limitations. A single-player play session must not be reported as a multiplayer pass.

## Official references

- StudioTestService: https://create.roblox.com/docs/reference/engine/classes/StudioTestService
- Studio testing modes: https://create.roblox.com/docs/studio/testing-modes
- Studio MCP: https://create.roblox.com/docs/studio/mcp
