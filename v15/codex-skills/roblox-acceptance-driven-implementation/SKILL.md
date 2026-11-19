---
name: roblox-acceptance-driven-implementation
description: Plan and implement Roblox features as small complete vertical slices with observable acceptance criteria, explicit risks, and honest verification evidence.
---

# Roblox Acceptance-Driven Implementation

## When to use
Use for new features, substantial bug fixes, architecture changes, integrations, and milestones. Skip only trivial edits whose correctness is obvious and local.

## Procedure
1. Define the user-visible result and affected player/developer workflows.
2. Inspect the source of truth and select relevant specialists before planning implementation.
3. Write acceptance criteria that describe observable behavior, not vague activities such as "make it robust".
4. Map each criterion to an implementation area and verification method. Include negative/error cases and cleanup behavior.
5. Identify client/server authority, data persistence, permissions, performance, compatibility, and migration risks.
6. Choose the smallest complete vertical slice that proves the intended behavior end to end.
7. Implement in reviewable changes, keeping configuration separate from behavior and preserving project conventions.
8. Run available checks in order of value: static analysis, formatting, Luau compilation, Rojo build, unit tests, integration tests, then Studio runtime tests where required.
9. Mark every check with its real result. Use BLOCKED or NOT_RUN when its environment was unavailable; never infer a pass from code inspection or a successful build.
10. Review the diff against every acceptance criterion and report limitations, rollback/migration steps, and remaining manual work.

## Planning template
- Outcome
- Affected systems/files
- Dependencies and unknowns
- Security/data/performance risks
- Acceptance criteria
- Tests and evidence required
- Rollback or migration plan

## Pitfalls and fixes
- Too much scope: split the feature into a first playable/usable slice and defer optional polish.
- Unobservable criterion: rewrite it as behavior with an assertion or explicit manual check.
- Build treated as gameplay proof: report compiler/build results separately from Studio runtime results.
- No failure path: add rejection, timeout, retry, cleanup, and recovery criteria where applicable.

## Output contract
Report implemented behavior, files changed, criterion-by-criterion status, commands executed, evidence, known defects, and remaining work.
