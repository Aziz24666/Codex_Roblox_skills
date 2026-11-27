# V37 Plan and Report CLI

Copy `v37/examples/implementation-plan.example.json` into a project-local planning folder and replace illustrative values.

```powershell
python .\v37\tools\v37.py doctor --root C:\Path\To\YourGame
python .\v37\tools\v37.py validate-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json
python .\v37\tools\v37.py audit-plan --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --output .codex\reports\feature-plan-audit.json
python .\v37\tools\v37.py validate-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json
python .\v37\tools\v37.py audit-report --root C:\Path\To\YourGame --plan .codex\plans\feature-plan.json --report .codex\reports\implementation-report.json --output .codex\reports\implementation-handoff.json
```

The CLI validates supplied JSON and path declarations only. It does not inspect source code, calculate actual diffs, run Luau, invoke Roblox Studio, contact Roblox services, or authenticate evidence references. Compare recorded changed paths with the actual version-control diff during review.
