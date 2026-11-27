# V37 Implementation Evidence and Handoff

Implementation reports map task IDs to statuses, changed paths, acceptance-criterion outcomes, and opaque evidence references.

## Completion rule

A task may be marked `completed` only when every planned acceptance criterion is recorded as `pass`. A passed `studio_manual` or `runtime_manual` criterion requires at least one opaque evidence reference.

Keep evidence files in authorized project storage and place only opaque `ev-` IDs in the report. Do not add private URLs, tokens, player data, or unbounded free-form notes.

## Distinguish verification types

- Static inspection: source/configuration review only.
- Automated test: an actual configured test or check was run.
- Studio manual: a human performed the named Studio scenario.
- Runtime manual: a human observed the named runtime/device/multiplayer scenario.

GitHub Actions success does not prove Studio or real-device behavior. A V37 report validates the structure and scope of recorded evidence; it does not verify that the evidence itself is genuine.
