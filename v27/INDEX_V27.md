# Roblox Codex Game Studio Kit — V27

V27.0.0 is the current cumulative release. It contains V1-V26 plus Luau code intelligence and architecture validation.

## V27 additions

- Three native Codex skills for Luau static analysis, dependency architecture, and RemoteEvent/Rojo contract review.
- `doctor`: checks the project and detects whether `luau-analyze` and `rojo` are available on PATH.
- `audit`: creates a read-only architecture report with script inventory, gradual type-mode coverage, static dependency edges, potential cycles, possible unused modules, RemoteEvent call/handler inventory, and Rojo project checks.
- `typecheck`: runs the official `luau-analyze` CLI without a shell, respecting project configuration by default; strict/nonstrict override is explicit.
- `rojo-check`: validates project JSON and `$path` mappings; optional `--build` runs Rojo to a temporary output file that is deleted after the check.
- Path containment, symlink rejection, bounded file counts/sizes, atomic report writes, and explicit heuristic limitations.
- A 213-skill cumulative package audit and CI workflow retaining V14-V26 checks.

## Quick start

Open PowerShell in the extracted V27 toolkit directory, then check your project/tool installation:

    python ".\v27\tools\v27.py" doctor --root "C:\Path\To\YourGame"

Generate an architecture report:

    python ".\v27\tools\v27.py" audit --root "C:\Path\To\YourGame"

Replace an existing report only after reviewing it:

    python ".\v27\tools\v27.py" audit --root "C:\Path\To\YourGame" --force

Run the official Luau analyzer using the modes declared in each file and project config:

    python ".\v27\tools\v27.py" typecheck --root "C:\Path\To\YourGame"

Run Rojo's structural validation and optionally a temporary build:

    python ".\v27\tools\v27.py" rojo-check --root "C:\Path\To\YourGame" --build

For projects with multiple `.project.json` files, pass `--project` with the intended file.

## Core architecture practices

- Use Luau's gradual type system. Migrate stable modules and service boundaries toward `--!strict` incrementally; do not mass-add strict directives without resolving diagnostics.
- Keep module dependencies directional and small. Review cycles and unreferenced candidates rather than blindly deleting or rearranging scripts.
- Treat remote identifiers, payload schemas, server validation, authorization, and rate limits as explicit contracts. V27's static matching is a review aid, not a security verdict.
- Validate Rojo project mappings before building or syncing. Confirm the selected project and target place before any live sync.
- Run the Script Analysis window in Roblox Studio as an additional engine-aware check.

## Important limitations

- `audit` is a conservative text-based inventory, not a full Luau parser or Roblox DataModel emulator.
- Static dependency resolution only handles constant `require(script.Parent...)` chains and approximates filesystem hierarchy. Complex Rojo mappings, dynamic registries and runtime-generated module paths need human review.
- A possible unreferenced module is not proof that a script is unused.
- An apparently unmatched client remote call is not proof that a server handler is absent; aliases, wrappers, generated names and shared modules can hide relationships.
- `typecheck` requires the official `luau-analyze` executable installed separately.
- `rojo-check --build` requires the Rojo CLI. Its temporary build artifact is not saved into the project.
- V27 never edits scripts, adds `--!strict`, renames modules, deletes files, changes remotes, or modifies place files automatically.

## Cumulative scope

V27 includes **213 native Codex skills** and all V1-V26 features. The no-gambling and fair-monetization requirements remain unchanged.
