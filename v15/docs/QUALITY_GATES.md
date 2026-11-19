# V15 Quality Gates and Evidence Policy

## Gate A — Source integrity
- No generated output is mistaken for canonical source.
- Dependency and tool versions are pinned where practical.
- Reproducible package assembly is preferred over opaque manual archives.
- All package manifests, JSON schemas, examples, and native Codex skill entry points validate.
- The final cumulative package has a generated inventory and verified per-file SHA-256 manifest.

## Gate B — Code quality
- Luau sources compile with the pinned compiler.
- Rojo projects build successfully.
- Public module interfaces and ownership are documented.
- Error paths and cleanup are covered by tests where practical.
- V15 Python contracts and regression tests pass.

## Gate C — Skill quality
- Each Codex skill is a directory with a required SKILL.md.
- YAML frontmatter includes a unique valid name and useful description.
- Skill names match folder names and stay within naming constraints.
- Instructions define triggers, inputs, a concrete procedure, pitfalls, and a verification/output contract.
- The cumulative package copies skills into .agents/skills/.

## Gate D — Security
- Client input is treated as untrusted.
- Server validates type, range, ownership, permissions, distance, state, and rate limits as appropriate.
- Critical rewards, inventory, currency, progression, and match outcomes are server-authoritative.
- Remote contracts have negative tests, not only happy-path tests.
- No production secrets or real player data are used in fixtures.

## Gate E — Persistence
- Schema versions and migrations are explicit.
- Retry, failure, duplicate request, and session-conflict behavior are defined.
- Test data is isolated from production data.
- Destructive migration tests use disposable fixtures and documented rollback.

## Gate F — Runtime
- Studio runtime tests are distinguished from compile/build checks.
- Multiplayer tests state client count and scenario.
- Device simulation records the simulated preset and orientation.
- Physical device testing is reported separately from simulation.
- External service tests record environment and authorization.

## Gate G — Performance
- Budgets are defined per target experience, not invented globally.
- Measurements identify device, server/client context, workload, sample duration, and metric.
- Regressions are compared against a recorded baseline.
- Profiling evidence is not inferred from source inspection.

## Evidence vocabulary
- PASS: a check actually ran and its assertions passed.
- FAIL: a check ran and one or more assertions failed.
- BLOCKED: the check could not run because a dependency, permission, or environment was unavailable.
- NOT_RUN: no execution was attempted.
- NOT_APPLICABLE: the check does not apply, with a reason.

A successful CI build is not evidence of a successful Studio playtest. A simulated device is not a physical device. A local mock is not a live production service.
