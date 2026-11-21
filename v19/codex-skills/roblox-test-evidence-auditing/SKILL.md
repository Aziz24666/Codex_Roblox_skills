---
name: roblox-test-evidence-auditing
description: Audit verification evidence so status claims match the actual command, environment, observed result, and artifact.
---

# Test Evidence Auditing

## Mission

Make completion reports trustworthy. Check whether each verification claim has enough inspectable evidence and whether its status accurately describes what happened.

## Required record

For each check, capture its ID, category, status, environment, tool/runtime version, exact command or manual scenario, build identity, expected result, actual result, evidence artifact paths, and limitations.

## Status rules

- \`PASS\`: executed in the named environment; actual result meets expected result; command/scenario, tool version, build identity, and a non-empty artifact are recorded.
- \`FAIL\`: executed and did not meet expected result; preserve the failure output or screenshot.
- \`BLOCKED\`: could not run because an explicit prerequisite, permission, or environment was unavailable; name the blocker.
- \`NOT_RUN\`: not attempted; state why it remains outstanding.
- \`NOT_APPLICABLE\`: genuinely outside the changed scope; state why.

Do not promote static CI results into Studio, multi-client, device, performance, persistence, purchase, or live-service passes. Do not mark an environment-specific check as PASS based solely on a plan or a mock.

## Audit procedure

1. Validate the evidence JSON against \`v19/schemas/verification-evidence.schema.json\`.
2. Confirm each PASS/FAIL command or scenario is specific enough to reproduce.
3. Confirm artifact paths are inside the project and files are non-empty.
4. Inspect the artifact contents and verify they match the named build and scenario.
5. Check that Studio/multiplayer/device/live-service claims identify the actual environment and tool version.
6. Compare actual outcomes to the exact acceptance criteria.
7. Verify blocked and unrun items remain visible in the final report.
8. List missing, stale, ambiguous, or contradictory evidence.

Use \`python v19/tools/v19.py validate-evidence --root . --file <path>\` for schema and artifact-path checks. That CLI does not authenticate screenshots or independently verify that the command was executed; human review remains necessary.

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
