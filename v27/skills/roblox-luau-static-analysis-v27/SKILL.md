---
name: roblox-luau-static-analysis-v27
description: Analyze Roblox Luau projects with the official luau-analyze CLI, incremental strict typing, and evidence-based static diagnostics.
---

# Roblox Luau Static Analysis

Use this skill when writing, reviewing, diagnosing, or improving Luau code quality.

## Establish the baseline

- Identify the actual game project root and source directories.
- Inspect the current type-mode directives and any `.luaurc` files.
- Check whether the official `luau-analyze` CLI is available.
- Use the V27 offline audit to inventory source files, type modes, and conservative architecture signals.
- Use `luau-analyze` for type checking and linting; do not claim the offline inventory is a parser or type checker.

## Gradual type migration

- Start with stable leaf modules, pure helpers, shared data definitions, and low-dependency interfaces.
- Add parameter types, return types, generic constraints, optional-field handling, and shared payload types.
- Move one bounded module or subsystem at a time to `--!strict`.
- Run the analyzer and relevant tests after each change.
- Prefer precise records and unions over broad `any` casts.
- Keep intentional dynamic/reflection-heavy modules in a justified mode until they can be typed safely.

Never add `--!strict` to every script in one mass edit. Never automatically alter type directives or suppress diagnostics to make a report green.

## Diagnostics workflow

1. Capture the baseline analyzer output.
2. Sort issues by runtime risk, affected callers, and shared-interface impact.
3. Fix root causes rather than hiding errors with casts.
4. Update affected callers and tests together.
5. Re-run static checks and focused Studio tests.
6. Report unresolved diagnostics and skipped tests.

## Honest evidence

- Keep compiler/type-checker output separate from Studio runtime logs.
- Record the exact CLI mode, project config, and files analyzed.
- Distinguish analyzer errors from heuristic warnings.
- A clean analyzer run does not prove the experience is correct at runtime.
