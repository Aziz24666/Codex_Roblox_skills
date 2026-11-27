---
name: roblox-scoped-implementation-and-change-impact
description: Implement a planned Roblox feature within declared file scope, trace downstream impact, and detect unplanned edits before integration.
---
# Roblox scoped implementation and change impact

Use this skill when implementing a feature that has a reviewed V37 plan.

## Required workflow

1. Read the approved plan and identify the current task, prerequisites, allowed paths, acceptance criteria, and risk.
2. Confirm dependencies are complete before starting the task.
3. Re-inspect the target files and their callers, consumers, tests, data contracts, remotes, and configuration.
4. Change only files within the current task's allowed paths and project-wide included scope. Respect excluded paths.
5. Before editing, identify compatibility and integration impact: public module contracts, remote payloads, save data, asset references, UI flows, and other tasks.
6. Make the smallest coherent change. Follow existing Luau patterns and type mode; avoid unrelated formatting or refactors.
7. Add or update focused tests where the repository supports them. Do not invent test commands.
8. Review the diff for out-of-scope edits, duplicated logic, missing validation, server/client trust mistakes, persistence risks, and accidental secret or personal-data exposure.
9. Record changed paths and actual verification evidence against the plan. Do not report a test as passed unless it ran and passed.
10. If implementation requires scope expansion, stop and request plan revision rather than silently broadening permissions.

## Integration rules

- Keep authoritative game state on the server.
- Validate and bound all client-provided remote data on the server.
- Preserve existing data schemas or provide an explicit, reversible migration plan.
- Use Roblox text filtering requirements for player-visible user-generated text.
- Keep paid outcomes transparent and fixed; the toolkit's no-gambling policy remains mandatory.
- Avoid adding credentials, private URLs, personal data, or player-level analytics to source, reports, or manifests.

## Boundaries

A source diff review cannot prove a change behaves correctly in Studio. Do not claim that CI ran Studio, emulated devices, or verified live multiplayer unless the evidence specifically proves it.
