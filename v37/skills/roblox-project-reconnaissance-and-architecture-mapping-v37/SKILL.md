---
name: roblox-project-reconnaissance-and-architecture-mapping
description: Inspect an existing Roblox game project before changing it; map its structure, runtime boundaries, data flow, and conventions into a concise evidence-backed architecture overview.
---
# Roblox project reconnaissance and architecture mapping

Use this skill before implementing a substantial feature in an existing Roblox game, especially when the project structure, architecture, or conventions are unfamiliar.

## Required workflow

1. Confirm the actual project root. Do not assume the Codex workspace root and game project root are the same.
2. Start read-only. Inventory the repository tree with sensible exclusions for generated folders, dependency caches, binaries, and large media.
3. Identify project configuration and source mapping: Rojo project files, place/project files, package manifests, test configuration, build scripts, and documented entry points.
4. Map important code boundaries: server scripts, client scripts, shared modules, UI, data/persistence, remotes, assets, and tests. Use the project's actual naming and paths.
5. Trace the relevant feature's current flow across client, server, shared modules, persistence, and UI. Distinguish observed references from inferred behavior.
6. Record conventions and constraints: Luau type mode, module style, naming, dependency injection, remote validation, data schema, UI patterns, and test commands.
7. Identify unknowns and risky areas. Do not fill gaps with invented APIs, paths, services, or existing behavior.
8. Produce a compact architecture map and a proposed change surface. Do not modify files unless the user has separately authorized implementation.

## Deliverable

Return:
- Project-root and project-type confirmation.
- Key directory and entry-point map.
- Relevant call/data-flow map.
- Existing conventions and integration points.
- Candidate files likely to change, with reasons.
- Risks, unknowns, and questions requiring owner decisions.
- Verification commands that are actually configured in the repository.

## Boundaries

A file inventory is not proof of runtime behavior. Do not claim Studio playtests, multiplayer tests, or device tests occurred unless evidence exists. Never print secrets, tokens, private player data, or entire sensitive configuration files. Keep the reconnaissance focused on the requested feature.
