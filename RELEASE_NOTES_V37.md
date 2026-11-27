# V37.0.0 — Project-Aware Implementation Orchestration

## Added
- Four native Codex skills for project reconnaissance and architecture mapping, feature decomposition/dependency planning, scoped implementation/change impact, and implementation verification/handoff.
- Offline implementation-plan and implementation-report validation.
- Stable topological ordering, dependency-cycle checks, overlapping-scope detection, and explicit included/excluded/task path controls.
- Acceptance-criterion traceability, human-review gates for high-risk/manual checks, and opaque evidence-reference validation.
- Strict JSON schemas, examples, documentation, regression tests, cumulative package patcher/auditor, and GitHub Actions release workflow.

## Cumulative package
V1-V37, 252 native Codex skills. Download only the V37 package.

## Important limitations
The CLI validates supplied plan/report metadata and declared file paths only. It does not inspect source code, calculate actual diffs, run Luau, launch Roblox Studio, test devices, contact Roblox services, or authenticate evidence references. Compare recorded changed paths with the actual repository diff. A GitHub Actions pass does not prove Studio or live-game behavior.
