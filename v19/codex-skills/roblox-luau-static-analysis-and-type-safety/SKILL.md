---
name: roblox-luau-static-analysis-and-type-safety
description: Apply project-aware Luau type checking, lint, and formatting gates with gradual strict-mode adoption.
---

# Luau Static Analysis and Type Safety

## Mission

Improve the reliability of Luau code using the project's actual analyzer, type-checking configuration, lint rules, and formatter. Keep the work incremental and compatible with the existing Rojo/Studio project.

## Discovery

- Inspect \`.luaurc\`, \`selene.toml\`, \`stylua.toml\`, \`rokit.toml\`, \`aftman.toml\`, \`wally.toml\`, project files, and repository guidance.
- Identify the installed Luau Analyzer, Selene, StyLua, and package/tool manager versions.
- Read the current tool help and configuration before choosing flags. Do not assume command-line options are identical across versions.
- Identify generated code, third-party packages, and legacy folders that should not be reformatted or analyzed under different rules.

## Type-checking strategy

Luau supports gradual type checking. Use the project's chosen mode deliberately:
- \`--!strict\` for new modules and well-owned boundaries where types can be maintained.
- \`--!nonstrict\` as an explicit transitional mode for modules that are not ready for full inference.
- \`--!nocheck\` only where there is a documented reason; do not use it to hide errors.

Start with leaf modules and high-value contracts. Add explicit types for public function parameters, return values, shared records, remote payloads after server validation, configuration, and module exports. Avoid broad \`any\` escape hatches. Narrow optional values and validate untrusted data before it enters typed internal state.

## Execution procedure

1. Record baseline analyzer findings before changing configuration.
2. Run the analyzer against the smallest changed surface.
3. Fix new errors and warnings caused by the change; classify pre-existing findings separately.
4. Add or update regression tests for corrected boundary behavior.
5. Run the repository lint and formatting tools in their documented check-only modes.
6. Expand analysis to dependent modules and then the wider project.
7. Review the diff for unrelated reformatting and generated-file churn.
8. Record exact commands, tool versions, analyzer mode, findings before/after, and output artifacts.

## Roblox-specific boundaries

Static analysis cannot prove instance existence, engine scheduling, replication, permissions, DataStore behavior, physics, animation playback, or visual correctness. Those require focused Studio/runtime scenarios. Server/client shared contracts should have explicit types, but types do not replace runtime validation of client input.

## Output

Provide a concise change report, strictness coverage, remaining warnings, files excluded from checks, and the next incremental migration target. Never claim the whole project is strict when only selected modules were checked.

## V18 shared workflow and handoff contract

- Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned. Do not silently redefine shared APIs, schemas, remotes, data ownership, or another specialist's files.
- Return a structured handoff: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence, risks, blockers, and next owner.
- Update task/evidence artifacts. Use PASS only for checks that actually ran; keep unavailable Studio/device/live-service checks NOT_RUN or BLOCKED.
- Re-route when scope changes. Skills do not grant tools, permissions, MCP connections, or runtime capabilities.

## V19 verification and evaluation contract

- Select verification from changed paths, impacted systems, trust boundaries, and failure impact; do not run or report unrelated checks as proof.
- Separate formatting, static analysis, unit, contract, integration, Studio, multi-client, device, performance, persistence, economy, and live-service checks.
- A plan is not an execution result. Preserve NOT_RUN and BLOCKED states for checks that did not run.
- A PASS requires the exact command or scenario, named environment, tool/runtime version, build identity, expected behavior, observed behavior, and a non-empty inspectable evidence artifact.
- Keep failures visible. Do not weaken acceptance criteria, delete negative benchmark cases, or convert a failed check into a pass.
- Deterministic routing benchmarks measure router behavior only; they do not prove model reasoning quality, skill compliance, or game correctness.
