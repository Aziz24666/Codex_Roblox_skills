# Roblox Codex Game Studio Kit — V37

V37.0.0 is the cumulative V1-V37 package with **252 native Codex skills**. Download only the current V37 package; it already includes V1-V36.

## V37 additions

- Four native Codex skills for project reconnaissance and architecture mapping, feature decomposition and dependency planning, scoped implementation and change-impact review, and implementation verification and handoff.
- Offline CLI commands: `doctor`, `validate-plan`, `audit-plan`, `validate-report`, and `audit-report`.
- Dependency DAG validation and deterministic execution ordering.
- Explicit included/excluded project paths and task-level allowed paths.
- Detection of missing dependencies, dependency cycles, independent task scope overlaps, out-of-scope changed files, incomplete acceptance criteria, and missing evidence for manual Studio/runtime checks.
- Strict JSON schemas, sample plan/report, documentation, and regression tests.

## Quick start

From the extracted V37 package root:

```powershell
python .\v37\tools\v37.py doctor --root C:\Path\To\YourGame
python .\v37\tools\v37.py validate-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json
python .\v37\tools\v37.py audit-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --output .codex\reports\feature-plan-audit.json
python .\v37\tools\v37.py validate-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json
python .\v37\tools\v37.py audit-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json --output .codex\reports\implementation-handoff.json
```

Copy the examples from `v37/examples/` and replace the illustrative values with reviewed project-specific data.

## Difference from previous versions

V33 plans test coverage and regression evidence. V37 plans and governs feature implementation itself: project reconnaissance, bounded tasks, dependency sequencing, path ownership, acceptance-criterion traceability, and implementation handoff. It complements, rather than replaces, V25 session continuity and V33 test planning.

## Verification boundaries

The V37 CLI validates supplied JSON metadata and declared paths only. It does not inspect source contents, calculate Git diffs, execute Luau, invoke Roblox Studio, run tests, contact Roblox services, or authenticate evidence references. Compare recorded changed-file lists against an actual version-control diff. Studio/runtime/device verification must be performed and recorded by a human.

All V1-V36 safeguards remain cumulative, including server authority, secure persistence, privacy, player safety, human-reviewed moderation, accessibility, transparent monetization, fixed paid outcomes, and the mandatory no-gambling policy.
