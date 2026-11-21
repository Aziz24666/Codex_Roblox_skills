---
name: roblox-test-matrix-and-risk-planning
description: Build a risk-based Roblox verification matrix from changed systems, acceptance criteria, and failure impact.
---

# Roblox Test Matrix and Risk Planning

## Mission

Translate a task and its diff into a small, prioritized set of checks that proves the changed behavior at the correct level. Prefer targeted tests first, then broaden coverage where the change crosses system or trust boundaries.

## Required inputs

Inspect the work item, acceptance criteria, project profile, source-of-truth markers, changed paths, dependency graph, existing test harnesses, and current evidence. Do not invent test frameworks or claim a local test runner exists without checking.

## Planning procedure

1. Map changed modules to owning systems and their public contracts.
2. Identify the highest-impact failures: lost player data, unauthorized state changes, duplicate grants, broken join/leave, incompatible rigs, inaccessible controls, content permission failures, performance regressions, or invalid releases.
3. For every acceptance criterion, write at least one observable verification scenario.
4. Select checks by layer:
   - formatting and lint for modified source;
   - Luau static analysis and type checking for Luau modules;
   - unit tests for local logic and deterministic calculations;
   - contract/integration tests for producer-consumer boundaries;
   - Studio playtests for engine/runtime behavior;
   - multi-client tests for replication, server authority, matchmaking, and player lifecycle;
   - device/input checks for affected interaction modes;
   - profiling for performance-sensitive changes;
   - isolated test data for persistence/economy changes;
   - package and approval checks for releases or external effects.
5. Order checks from inexpensive deterministic checks to environment-specific scenarios.
6. Identify the required environment, fixtures, test accounts, tool versions, build identity, evidence artifact, and cleanup.
7. Mark every unavailable check NOT_RUN or BLOCKED. Do not treat a plan as evidence.
8. After execution, compare actual outcomes with acceptance criteria and preserve all failures.

## Risk guidance

- Remote/client input changes require server-authority and malformed/duplicate request coverage, plus an actual multi-client scenario when behavior depends on networking.
- Persistence and economy changes require isolated fixtures, retry/replay coverage, idempotency checks, and failure recovery.
- UI/input changes require each affected input mode and screen size; a desktop screenshot alone is insufficient for touch/gamepad claims.
- Character changes require the rig types, spawn/respawn paths, ownership, and animation states in scope.
- Performance changes require a comparable before/after baseline on named client/server environments.
- Release changes require reproducible artifacts, checksums, version/tag agreement, and approval boundaries.

## Output

Produce a verification plan with check IDs, category, reason, status initially NOT_RUN, suggested tools or scenarios, prerequisites, and the evidence required. Map each acceptance criterion to one or more checks. Explain exclusions and residual risk. Use \`python v19/tools/v19.py plan-tests\` for a deterministic first draft, then review it against the real project.

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
