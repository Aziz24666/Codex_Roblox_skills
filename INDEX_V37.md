# Roblox Codex Game Studio Kit — V37

V37.0.0 is the cumulative V1-V37 package with **252 native Codex skills**. Only this current cumulative release is required.

## V37 additions
- Four native Codex skills for project reconnaissance, feature decomposition/dependency planning, scoped implementation/change impact, and implementation verification/handoff.
- Offline CLI for plan validation, dependency ordering, path-scope checks, implementation-report validation, and handoff audit.
- Strict plan/report schemas with bounded fields, stable task/criterion IDs, and opaque evidence references.
- Regression coverage for dependency cycles, scope conflicts, unsafe paths, unplanned changed files, manual evidence requirements, and handoff consistency.

## Commands
```powershell
python .\v37\tools\v37.py doctor --root C:\Path\To\YourGame
python .\v37\tools\v37.py validate-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json
python .\v37\tools\v37.py audit-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --output .codex\reports\feature-plan-audit.json
python .\v37\tools\v37.py validate-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json
python .\v37\tools\v37.py audit-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json --output .codex\reports\implementation-handoff.json
```

## Difference from previous versions
V33 plans test coverage and regression evidence. V37 plans and governs the implementation work itself: project reconnaissance, bounded feature tasks, dependency sequencing, changed-path scope, acceptance-criteria traceability, and handoff readiness. The V37 CLI does not replace V33 tests or V25 continuity.

## Verification boundaries
The V37 CLI validates supplied JSON and declared paths only. It does not inspect source contents, calculate Git diffs, execute Luau, invoke Roblox Studio, run tests, or authenticate evidence references. Compare recorded changed-file list against an actual version-control diff. Studio/runtime/device verification must be performed and recorded by a human.
