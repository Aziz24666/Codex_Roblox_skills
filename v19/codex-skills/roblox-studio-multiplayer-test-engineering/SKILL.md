---
name: roblox-studio-multiplayer-test-engineering
description: Design and verify real Roblox Studio multi-client scenarios for server-client, lobby, matchmaking, and lifecycle behavior.
---

# Roblox Studio Multiplayer Test Engineering

## Mission

Design repeatable Studio tests for behavior that cannot be established by static analysis or a single local script test. Focus on the real client/server boundary and player lifecycle.

## Capability discovery

- Confirm the current Studio version and whether the project has a test plugin or test harness.
- Discover the available \`StudioTestService\` methods from current Creator Hub documentation and the active Studio version.
- If Studio MCP is connected, enumerate connected Studio instances and explicitly target the intended instance/place.
- Do not assume GitHub Actions or the local CLI can access Studio. Do not infer capabilities from the presence of this skill.

## Scenario design

Prefer bounded, deterministic scenarios with explicit starting state and completion conditions. Useful cases include:
- two or more clients join the same server and observe authoritative replicated state;
- lobby arrival, party membership, matchmaking success/failure, and join-in-progress;
- player leave, disconnect, reconnect, and cleanup;
- server-authoritative inventory/economy changes and rejection of invalid client requests;
- duplicate requests and retry behavior;
- teleport transitions when the experience and test environment support them;
- latency, jitter, or packet-loss cases using Studio's network simulation controls.

Specify the number of clients, roles, initial fixture, event sequence, expected server state, expected client-visible state, timeout, cleanup, and failure diagnostics.

## StudioTestService pattern

Roblox documents \`StudioTestService\` for plugin-controlled Test/Run mode automation, including multi-client tests. A typical setup has:
1. a plugin entry point that launches a bounded test and passes scenario arguments;
2. server-side test code that validates the authoritative result and ends the test;
3. client-side test code that participates and reports observations.

Use documented methods such as \`ExecuteMultiplayerTestAsync\`, \`GetTestArgs\`, \`AddPlayers\`, \`EndTest\`, and \`LeaveTest\` only as supported by the current API. Keep test code isolated from production game logic and avoid hidden side effects.

## Test safety and isolation

- Use a dedicated test place/configuration and test-owned data.
- Never point a test at production DataStores or live purchase flows by default.
- Make cleanup idempotent and restricted to resources created by that test.
- Do not save, publish, upload, or alter permissions unless explicitly approved.
- Keep test clients and fixtures deterministic so failures are reproducible.

## Evidence

Record Studio version, place/build identity, scenario ID, client count, roles, network simulation settings, exact observed server/client outcomes, logs, and evidence paths. A one-client playtest cannot pass a multi-client requirement. A disconnected MCP session must be recorded as BLOCKED or NOT_RUN, not PASS.

## V18 shared workflow and handoff contract

- Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned. Do not silently redefine shared APIs, schemas, remotes, data ownership, or another specialist's files.
- Return a structured handoff: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence, risks, blockers, and next owner.
- Update task/evidence artifacts. Use PASS only for checks that actually ran; keep unavailable Studio/device/live-service checks NOT_RUN or BLOCKED.
- Re-route when scope changes. Skills do not grant tools, permissions, MCP connections, or runtime capabilities.

## V19 verification and evaluation contract

- Select verification from changed paths, impacted systems, trust boundaries, and failure impact; do not run or report unrelated checks as proof.
- Separate formatting, static analysis, unit, contract, integration, Studio, multi-client, device, performance, persistence, economy, and live-service checks.
- A plan is not an execution result. Preserve NOT_RUN and BLOCKED states for checks that did not run.
- A PASS requires the exact command or scenario, named environment, tool/runtime version, build identity, expected behavior, observed behavior, and a non-empty inspectable evidence artifact.
- Keep failures visible. Do not weaken acceptance criteria, delete negative benchmark cases, or convert a failed check into a pass.
- Deterministic routing benchmarks measure router behavior only; they do not prove model reasoning quality, skill compliance, or game correctness.
