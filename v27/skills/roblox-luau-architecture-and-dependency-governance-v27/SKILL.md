---
name: roblox-luau-architecture-and-dependency-governance-v27
description: Review Luau module boundaries, static require dependencies, circular dependencies, public interfaces, and project layering without unsafe automatic rewrites.
---

# Roblox Luau Architecture and Dependency Governance

Use this skill when a task spans several modules, services, controllers, shared packages, or project layers.

## Architecture discovery

- Identify the selected game project and source mapping.
- Inspect the Rojo project file where present.
- Inventory modules and entrypoints before changing the structure.
- Use V27's dependency report as a conservative guide, then verify important relationships against the actual Studio DataModel and source.

## Dependency rules

- Prefer dependencies that point toward stable, lower-level interfaces.
- Keep pure shared types/configuration separate from stateful server services.
- Avoid circular initialization dependencies.
- Keep server-only systems from depending on client-only modules.
- Avoid accidental duplication of the same system in multiple services.
- Document intentional plugin/runtime-loaded modules.

## Cycle review

When V27 reports a cycle:
1. Read every module in the reported strongly connected group.
2. Identify the smallest shared contract or interface that can break the cycle.
3. Check module initialization order and side effects.
4. Plan a narrow refactor with explicit callers and acceptance tests.
5. Change one boundary, then run type checks and relevant tests.

Do not split, move, rename, or delete modules solely because a regex-based report labels them in a cycle or as potentially unreferenced.

## Unreferenced module review

The report's candidates can still be loaded by entrypoints, plugin code, string-built module paths, runtime registries, or Rojo mappings. Search all loading paths and verify runtime use before any removal.

## Rojo mapping

Compare the filesystem paths, project `$path` mappings, and actual Instance hierarchy. The V27 filesystem dependency graph is approximate whenever Rojo maps a source directory to a different logical service path.

## Change contract

For architecture changes, provide:
- Current dependency direction and identified problem.
- Intended module ownership and public interfaces.
- Callers and systems affected.
- Migration and rollback strategy.
- Static checks and runtime tests.
- Explicit list of unverified dynamic paths.
