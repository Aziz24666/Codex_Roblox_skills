---
name: roblox-project-intelligence
description: Inspect an existing Roblox project before changing it; map its source of truth, architecture, entry points, toolchain, dependencies, and risks, then create or update a V15 project manifest.
---

# Roblox Project Intelligence

## When to use
Use before substantial work in an existing Roblox experience, plugin, package, or shared Luau library. Do not use for a tiny text-only edit or a general Roblox question.

## Inputs to gather
- Repository or project root and the requested outcome.
- Existing AGENTS.md, README.md, Rojo project files, package manifests, CI workflows, and architecture documentation.
- Available commands, tool versions, and whether the project is Studio-native, Script Sync, partially Rojo-managed, or fully Rojo-managed.

## Procedure
1. Read repository instructions and applicable nested instructions before inspecting implementation details.
2. Inventory the project tree. Exclude generated folders, caches, vendored dependencies, and build outputs from source-of-truth conclusions.
3. Identify canonical locations for server, client, shared modules, configuration, assets, persistence, networking, plugins, tests, and generated output.
4. Trace actual entry points and project mappings. Inspect Rojo mappings and build commands; do not assume conventional paths.
5. Record toolchain versions from lockfiles, manifests, CI, or checked-in tool configuration. Mark unknown or conflicting versions as unknown.
6. Search existing modules and systems before proposing a duplicate. Map dependencies and ownership boundaries.
7. Identify trust boundaries, external services, persisted data, asset permission dependencies, and anything that could affect a live experience.
8. Write or update a project manifest using v15/schemas/project-manifest.schema.json. Keep paths relative to the project root and list only verified entry points.
9. Run python v15/tools/v15_validate.py --root v15 when editing the supplied V15 contract set. Validate project-specific manifest data against its schema.
10. Deliver an architecture map, unknowns, risks, source-of-truth decisions, and a prioritized next-step plan.

## Efficiency rules
- Inspect high-signal files first; do not read every source file without a reason.
- Follow imports and project mappings only as far as needed to understand the requested change.
- Reuse existing architecture unless evidence shows a concrete defect.
- Re-check version-sensitive APIs before implementation.

## Pitfalls and fixes
- Two apparent entry points: inspect project mappings and CI commands to identify the actual build source.
- Generated code mixed with source: trace the generator and edit its inputs, not generated output.
- Unknown tool version: report it as unknown and block version-sensitive implementation until verified.
- Missing architecture docs: infer only what source proves and list unresolved areas.

## Output contract
Provide a project map, manifest path, verified toolchain, source-of-truth notes, high-risk boundaries, unknowns, and suggested next slice. Do not claim a repository is fully understood from a shallow listing.
