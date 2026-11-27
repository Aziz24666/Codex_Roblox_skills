---
name: roblox-feature-decomposition-and-dependency-planning
description: Turn a Roblox feature request into small, dependency-ordered, testable implementation tasks with explicit acceptance criteria and scope.
---
# Roblox feature decomposition and dependency planning

Use this skill after understanding the project and before making a multi-file or architectural change.

## Required workflow

1. Restate the desired player-visible and technical outcomes without silently adding features.
2. Separate product decisions from engineering decisions. List unresolved decisions instead of inventing them.
3. Break the work into small tasks with one clear outcome each.
4. Define task dependencies explicitly. Tasks must form a directed acyclic graph.
5. Give every task a bounded allowed-path list. Align it with project scope and avoid unnecessarily broad roots.
6. Add stable acceptance-criterion IDs and describe how each criterion will be verified: static inspection, automated test, Studio manual test, or runtime manual test.
7. Identify risk and state whether human approval is required. High-risk changes and any Studio/runtime acceptance criterion require human review.
8. Include integration sequencing, migration/rollback considerations where relevant, and a final end-to-end verification task.
9. Validate the plan with the V37 CLI before implementation.

## Task quality rules

- Prefer independent tasks only when their file scopes do not conflict.
- If two tasks touch overlapping paths, put them in an explicit dependency order or redesign their scope.
- Keep server authority, remote validation, persistence compatibility, filtering, privacy, and player safety as explicit acceptance criteria when relevant.
- Avoid vague tasks such as "finish gameplay" or acceptance criteria such as "works correctly."
- Do not mark manual Studio/runtime testing as passed based on static checks or CI alone.

## Deliverable

Produce a V37 implementation plan with goal, included/excluded paths, task objectives, dependencies, allowed paths, risk, human-review requirement, acceptance criteria, and verification kinds.

## Boundaries

Planning does not execute code or guarantee feasibility. Do not invent test results, external service access, Roblox APIs, or user approvals.
