# V27.0.0 — Luau Intelligence and Architecture

V27.0.0 extends the cumulative Roblox Codex Game Studio Kit from V1-V26 with practical Luau analysis, architecture inventory, and Rojo project validation.

## New capabilities

- Add three native Codex skills:
  - `roblox-luau-static-analysis`
  - `roblox-luau-architecture-and-dependency-governance`
  - `roblox-remote-contract-and-rojo-validation`
- Add `v27/tools/v27.py` with:
  - `doctor`: detect Luau analyzer/Rojo CLI availability and project files.
  - `audit`: generate an offline JSON report of scripts, type modes, static dependency edges, possible cycles, possible unreferenced modules, RemoteEvent/RemoteFunction call-handler inventory, and Rojo mappings.
  - `typecheck`: invoke the official `luau-analyze` CLI in bounded batches, respecting per-file/project settings by default; explicit strict/nonstrict overrides are supported.
  - `rojo-check`: validate project JSON and paths, with an optional temporary `rojo build` whose output is automatically removed.
- Add documentation for incremental strict typing, module dependency governance, server/client remote contracts, and safe Rojo validation.
- Add an architecture report schema, regression tests, cumulative 213-skill package patcher, and auditor.

## Safety and reliability

- Keep the offline audit read-only; it does not modify source scripts or project files.
- Bound source scanning by file count and file/aggregate size; skip symlinks and generated/cache directories.
- Keep dependency-cycle and unreferenced-module findings advisory. Dynamic require patterns and complex Rojo mappings can make text-only results incomplete.
- Keep remote contract findings advisory. Static matching does not prove a missing handler, vulnerability, or payload safety.
- Do not mass-add `--!strict`, remove modules, rewrite remote interfaces, live-sync, save a place, or publish automatically.
- Preserve V1-V26 capabilities and all fair-monetization/no-gambling requirements.

## Validation

- V27 tests cover gradual type-mode inventory, symlink/file-count boundaries, dependency resolution and cycles, unresolved/dynamic requires, remote pairing heuristics, Rojo project path validation, and safe package integration.
- Cumulative package audit requires 213 native skills and all V27 deliverables.
- Repository-wide syntax, JSON, Markdown-link, and skill-metadata audit remains in CI.
- All inherited V14-V26 checks remain in the V27 workflow.
- Release ZIP and TAR.XZ archives are independently tested, compared, and checksummed.

## Compatibility

- V27 adds files and CLI commands; it does not change the V25 checkpoint schema, V26 Studio MCP utility, or existing V1-V26 commands.
- The Luau and Rojo CLIs are separate optional prerequisites. V27 does not install binaries or alter PATH.
