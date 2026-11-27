---
name: roblox-implementation-verification-and-handoff
description: Verify Roblox implementation tasks against their acceptance criteria, distinguish automated and Studio evidence, and create a traceable handoff.
---
# Roblox implementation verification and handoff

Use this skill after implementation or when handing work between Codex sessions or developers.

## Required workflow

1. Load the exact plan and implementation report for the project root.
2. Confirm task identity, dependency completion, changed files, and acceptance-criterion IDs.
3. Run only repository-configured static checks and automated tests that are safe and available.
4. Report actual command, result, and evidence reference. A skipped or unavailable test is not a pass.
5. Treat Studio manual tests separately: record the exact place/build, Studio test mode, device/input context, scenario, observed result, and evidence reference in the project's authorized evidence store.
6. Treat runtime/manual multiplayer results separately from source-level tests and GitHub Actions.
7. Check each changed path against both project-wide scope and task allowed paths. Flag unplanned or cross-task edits.
8. Mark a task completed only when all its acceptance criteria pass and required manual evidence is present.
9. Carry unresolved failures, blocked tasks, migrations, approval needs, and follow-up work into the handoff.
10. Generate and validate the V37 report. Preserve a concise checkpoint in the project's normal continuity system when one is configured.

## Handoff format

Include:
- Plan ID and project key.
- Completed, in-progress, blocked, and not-started tasks.
- Changed files grouped by task.
- Acceptance-criterion outcomes.
- Automated checks actually run.
- Studio/device/multiplayer checks actually performed, or explicitly not performed.
- Evidence references and unresolved risks.
- Exact next action and required approval.

## Boundaries

Never fabricate logs, screenshots, runtime observations, approvals, or test outcomes. Do not place secrets, private URLs, personal data, or raw player records in the handoff.
