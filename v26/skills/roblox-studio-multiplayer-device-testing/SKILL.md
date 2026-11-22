---
name: roblox-studio-multiplayer-device-testing
description: Design and validate Roblox Studio multiplayer, device, controller, and degraded-network test coverage using Studio-only testing features and recorded evidence.
---

# Roblox Studio Multiplayer and Device Testing

Use this skill when a feature depends on replication, multiple players, touch/controller input, responsive UI, join/leave handling, or network timing.

## Choose the minimum useful matrix

Start with static validation and a single-client smoke test. Add coverage based on the feature's risks:

- 1 client: spawn, UI, primary interaction, and clean exit.
- 2 clients: replication, ownership, shared state, and player-to-player interaction.
- 4 clients: join/leave sequencing and multi-actor state transitions.
- Up to 8 clients: bounded edge cases and concurrency-sensitive flows.
- Device profiles: phone, tablet, desktop, and controller/orientation combinations the game supports.
- Network profiles: baseline, added latency, jitter, and packet loss when relevant.

Eight simulated clients is the documented StudioTestService maximum for one session, not a general load-test guarantee.

## StudioTestService rules

- Verify current API and plugin context before using StudioTestService.
- `ExecuteMultiplayerTestAsync` is plugin-facing, yields until the test finishes, and supports up to eight clients.
- Only one multiplayer test session can run at a time per Studio instance.
- `AddPlayers` and `EndTest` must be called from the server DataModel of an active test.
- Never assume plugin-only APIs run in a published experience.
- Keep test players and data synthetic and isolated.

## Device and input checks

- Use Device Simulator to review viewport size, density, orientation, touch UI, keyboard overlap, and supported platforms.
- Use controller emulation for gamepad flows.
- Use StudioDeviceSimulatorService only from supported Studio/plugin contexts; inspect current mode restrictions before changing simulation state.
- VirtualInput is for Studio testing and must be obtained through UserInputService:CreateVirtualInput(). Do not treat it as production input automation.
- Do not interact with Roblox CoreGui or protected platform UI through simulated input.

## Network checks

Use Studio Network Simulator where available. Record exact inbound/outbound settings. Test whether the game remains correct with extra delay, timing variation, and occasional packet loss. Check server acknowledgements, duplicate requests, state correction, and assumptions about event ordering.

Network simulation applies to Studio playtests only; it does not change live players' network conditions or published game behaviour.

## Evidence and honest reporting

For every scenario, record expected behaviour, observed behaviour, and PASS/FAIL/BLOCKED/NOT RUN. Attach relevant console output and screenshots. Report exact simulated client count and device/network settings. Keep unit tests, static checks, Studio playtests, and production validation as separate evidence classes.

Never describe a test as passed when it was skipped, blocked, or only planned.
