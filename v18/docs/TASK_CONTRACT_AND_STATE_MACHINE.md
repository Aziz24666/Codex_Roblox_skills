# V18 Task Contract and State Machine

## Canonical task

Each substantial task uses the JSON contract described by `schemas/work-item.schema.json`. The record includes a stable ID, task text, goal/non-goal boundaries, status, impacted domains, selected skills, workstreams, acceptance criteria, approvals, and evidence. Keep it concise and update it as facts change.

## State transitions

`DRAFT → DISCOVERED → SPECIFIED → DESIGNED → IMPLEMENTING → INTEGRATING → VERIFYING → REVIEWED → DONE`

Any state may move to `BLOCKED` when a required dependency, environment, research fact, or approval is unavailable. Resume only after re-checking repository state and the relevant artifact. Do not jump to DONE from planning.

## Acceptance criteria

Each criterion has a unique ID, observable description, verification method, owning workstream, and one of `PENDING`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or `NOT_APPLICABLE`. PASS requires evidence. Keep user-facing outcomes separate from internal implementation steps.

## Workstream graph

Every stream has an ID, owner, dependencies, owned paths, output contract, and status. The graph must be acyclic; all dependencies must exist; exclusive paths cannot overlap. Shared contracts are designed before dependent streams start.

## Evidence vocabulary

Check statuses are `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `NOT_APPLICABLE`. Use `NOT_RUN`, not an empty success, for Studio/device/live-service work that was not performed. Evidence includes environment, tool version, build identity, scenario, expected/actual result, logs/artifact, and limitations.
