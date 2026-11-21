# V19 Testing Strategy and Evidence Rules

V19 introduces risk-based verification planning. The objective is not to run every possible test on every edit; it is to identify the changed trust boundaries and player-facing behavior, then select the smallest test set that gives meaningful confidence.

## Verification layers

| Layer | What it can establish | What it cannot establish |
|---|---|---|
| Formatting and lint | Style, configured lint rules, some suspicious patterns | Runtime correctness |
| Luau static analysis | Type and static-analysis findings under the configured project mode | Studio engine behavior |
| Unit tests | A bounded module or function contract | Cross-system behavior unless represented |
| Integration/contract tests | Interaction between connected modules and explicit interfaces | Full player experience by default |
| Studio playtest | Behavior in the actual Studio place/runtime for the tested scenario | Multi-client or device coverage unless included |
| Multi-client Studio test | The tested server/client interactions and player lifecycle | Every network condition or production scale |
| Device/input matrix | The tested device classes and input modes | Untested hardware/configurations |
| Performance profile | Measured client/server frame, memory, network, or load behavior in the recorded environment | Performance on all devices |
| Live-service validation | The specific authorized live operation tested | Unobserved production conditions |

## Risk-to-test selection

Always inspect the diff and route by affected systems. Add checks when the change touches:

- **Remote/network boundary:** server-side validation, ownership, rate limits, duplicate/replay behavior, malformed input, and at least one real multi-client scenario.
- **Persistence:** isolated test data, load/save failure paths, retries, migration compatibility, shutdown/reconnect behavior, and rollback/recovery evidence.
- **Economy/purchases:** fixed-price and exact-grant invariants, idempotent fulfillment, receipt replay, duplicate delivery, balance integrity, and the V18 no-gambling policy.
- **Character/animation:** spawn/respawn, rig compatibility, ownership/replication, animation state transitions, and relevant avatar configurations.
- **UI/input:** keyboard/mouse, touch, gamepad, focus/navigation, safe-area and scale behavior, and accessibility scenarios supported by the project.
- **World/assets:** streaming boundaries, asset permission/ownership, load behavior, and content provenance.
- **Performance:** compare before/after on named client and server environments; capture profiler or performance-stat artifacts rather than relying on subjective impressions.
- **Release/deployment:** reproducible package, checksum, version/tag consistency, staged validation, approvals, and rollback plan.

## Evidence status vocabulary

- \`PASS\`: the check ran in the named environment, its expected result is explicit, the observed result satisfies it, and a non-empty evidence artifact is referenced.
- \`FAIL\`: the check ran and did not meet its expected result. Preserve the failure evidence; do not relabel it as blocked.
- \`BLOCKED\`: the check could not run because a dependency, permission, environment, or prerequisite was unavailable. Explain the blocker.
- \`NOT_RUN\`: the check has not been attempted. State why it remains outstanding.
- \`NOT_APPLICABLE\`: the check does not apply to the changed scope. Record the reason.

A generated plan is not evidence. A command suggestion is not an executed command. A successful Python unit test is not a Studio, multiplayer, device, purchase, or live DataStore test.

## Evidence packet

For each check, record:
- stable check ID and category;
- exact command or manual scenario;
- environment and tool/runtime version;
- build identity or commit SHA;
- expected behavior;
- actual observed behavior;
- status and limitations;
- one or more root-relative evidence artifact paths.

V19 \`validate-evidence\` rejects a PASS record without an observed result, executed command, and existing non-empty artifact. It rejects evidence paths that escape the project root. It does not authenticate screenshots or prove that a tool actually ran; reviewers must inspect the artifact and context.

## Recommended sequence

1. Inspect source of truth, project instructions, and the Git diff.
2. Identify changed modules, public contracts, data ownership, remotes, lifecycle, and external effects.
3. Run formatting and static analysis for changed source.
4. Run targeted unit and contract tests.
5. Run integration and regression scenarios for affected systems.
6. Use Studio playtests and multi-client scenarios where the real engine or client/server lifecycle matters.
7. Run relevant device and performance checks.
8. Review evidence, risk, approvals, and unexecuted checks before reporting completion.

Use the least expensive checks first, but never allow a cheap check to stand in for a required higher-level check.
