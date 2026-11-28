# V43 CLI reference

Run with Python 3.10 or newer. All paths are relative to the selected Roblox project root.

## Commands

~~~powershell
python .\v43\tools\v43.py doctor --root C:\Path\To\YourGame
python .\v43\tools\v43.py validate --root C:\Path\To\YourGame --manifest .codex\experiments\onboarding-plan.json
python .\v43\tools\v43.py audit --root C:\Path\To\YourGame --manifest .codex\experiments\onboarding-plan.json --output .codex\reports\experiment-audit.json
python .\v43\tools\v43.py compare --root C:\Path\To\YourGame --baseline .codex\experiments\baseline.json --candidate .codex\experiments\candidate.json --output .codex\reports\experiment-diff.json
python .\v43\tools\v43.py analyze --root C:\Path\To\YourGame --manifest .codex\experiments\onboarding-plan.json --results .codex\experiments\results.json --output .codex\reports\experiment-review.json
~~~

## Commands and exit codes

- validate: validates hypothesis, config contract, variant values/weights, duration, rollout, metrics, instrumentation, privacy/cardinality declarations, and operation/decision gates.
- audit: writes a design report with sample/MDE and instrumentation warnings.
- compare: marks config key/type changes as breaking and other plan changes as requiring review.
- analyze: reviews a results summary using the confidence intervals and SRM state supplied from Roblox. A fully-run `DECISION_NEEDED` or `COMPLETED` experiment can be reviewed. It requires each treatment's results to include exactly the predeclared guardrails and checks that every point estimate lies within its confidence interval. It flags invalid SRM, incomplete duration, inconclusive results, adverse guardrails, and cases ready for a human decision.
- 0: command completed without a blocking compatibility result.
- 1: invalid manifest/results or a breaking comparison.
- 2: path, input, or runtime error.

## Important limitations

The tool is offline. It does not calculate MDE, statistical significance, sample-size power, confidence intervals, or SRM; use Roblox Creator Hub or the authorized calculateMde endpoint for MDE. It does not call Roblox Open Cloud, poll asynchronous operations, access Creator Hub, assign players, start experiments, complete experiments, select winners, or publish configs. The confidence intervals and SRM state must come from Roblox. A candidate-for-human-review result is not an approval or rollout command.
