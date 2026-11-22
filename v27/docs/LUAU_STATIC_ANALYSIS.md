# V27 Luau Static Analysis and Type Checking

V27 adds an offline project inventory and an optional adapter for the official Luau analyzer.

## Commands

`doctor` checks whether `luau-analyze` and `rojo` can be found on PATH. It does not install tools or change system configuration.

`audit` writes a JSON report to `.codex/reports/v27-architecture-report.json` by default. It scans up to 10,000 Luau files, skips common generated/tool directories and symlinks, and enforces per-file and aggregate-size limits. Use `--force` to replace an existing report.

`typecheck` calls `luau-analyze` with an argument array and no command shell. It processes bounded batches and respects each file's Luau directives and `.luaurc` configuration by default:

    python v27/tools/v27.py typecheck --root "C:\Path\To\YourGame"

You can explicitly select a default mode:

    python v27/tools/v27.py typecheck --root "C:\Path\To\YourGame" --mode strict

Use the strict override only when intentionally validating the whole selected source set under strict mode. The default `project` setting is preferred because it preserves per-file configuration and supports incremental migration.

## Gradual strict typing

Luau supports `--!nocheck`, `--!nonstrict`, and `--!strict`. V27 reports the number of scripts in each mode but never changes their directives.

Recommended migration sequence:

1. Start with shared type definitions, stable utility modules, and leaf modules with few dependencies.
2. Add parameter and return annotations to public module functions.
3. Define shared records and remote payload types at explicit system boundaries.
4. Run the analyzer and fix actionable diagnostics before moving a caller or service to strict mode.
5. Expand to higher-level services and UI only after their dependencies have stable contracts.
6. Keep intentional dynamic/reflection-heavy code in a justified mode until it can be typed safely.

Avoid changing every script at once. A large strict-mode flip often produces noisy diagnostics that hide real regressions and encourages unsafe `any` casts.

## What the offline report contains

- Script counts and type-mode coverage.
- Constant `require(script.Parent...)` dependency edges that can be resolved against the filesystem-shaped script tree.
- Static missing and ambiguous references, plus dynamic/non-script require counts.
- Strongly connected dependency components (cycles).
- Possible unreferenced module candidates.
- Remote API call/handler counts and statically named client calls without a matching server handler.
- Rojo project mapping validation.
- Tool availability and explicit limits.

## Trust the right evidence

The offline report is a conservative heuristic and does not parse the entire Luau grammar. Use `luau-analyze` for Luau-aware type checking and linting, and Roblox Studio's Script Analysis window for engine-aware diagnostics. A clean static report does not prove that the experience behaves correctly at runtime.

## Sources

- [Luau: Getting started and CLI tools](https://luau.org/getting-started/)
- [Luau: Type checking](https://luau.org/types/)
- [Roblox Creator Hub: Type checking](https://create.roblox.com/docs/luau/type-checking)
- [Roblox Creator Hub: Script Editor and Script Analysis](https://create.roblox.com/docs/studio/script-editor)
