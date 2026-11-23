# Aggregate game health and LiveOps readiness

V31 evaluates operator-supplied aggregate snapshots against thresholds that the project team declared in advance. It deliberately does not ingest per-player records or calculate metrics from raw events.

## Configure guardrails

Copy `v31/examples/health-policy.example.json` to `.codex/analytics/health-policy.json`. Set:

- `minimum_sample_size`: the smallest aggregate sample the team considers meaningful.
- `maximum_age_hours`: the maximum age of a snapshot before it must be held.
- `metrics`: explicit `min` or `max` directions, a warning threshold, and a hard threshold.

Choose thresholds based on your game, test setup, platform measurements, and operational history. Do not copy example values blindly. Retention and onboarding measures are health context—not goals to maximize at the expense of player choice, accessibility, or a fair free experience. Review qualitative player feedback and known measurement gaps alongside the snapshot.

## Prepare a privacy-safe snapshot

A health snapshot must contain only aggregate values, a timestamp, an environment, a source description, and a sample size. It must not contain arrays of player rows, user identifiers, usernames, chat text, or a list of individual purchases. Keep the underlying aggregate report in approved project storage and export only the minimum summary required for review.

## Evaluate the snapshot

```powershell
python ".\v31\tools\v31.py" evaluate-health --root "C:\Path\To\YourGame"
```

V31 produces one of four states:

| State | Meaning |
|---|---|
| `clear` | Supplied values are within the declared guardrails and the snapshot is sufficiently recent and large |
| `warning` | One or more values crossed a warning threshold but not the hard limit |
| `alert` | One or more values breached a hard threshold |
| `hold` | Snapshot is stale, too small, incomplete, or otherwise insufficient to evaluate |

Missing metrics are not filled with zero. A stale or undersized snapshot is not called healthy. A clear result means only that the supplied values meet the selected policy; it does not prove the game is free from problems.

## LiveOps readiness

Before a live operation, document the player-facing purpose, eligibility, start/end times, affected systems, operator, monitoring owner, stop conditions, rollback method, and support/communications plan. Make the default experience understandable without purchases. Keep paid outcomes fixed and disclosed; do not use paid chance, gambling-like mechanics, artificial scarcity, forced playtime, or coercive notifications.

For experiments, write the hypothesis and primary metric before launch, define a minimum sample and observation window, and predeclare guardrails for errors, performance, purchase failures, and player support. Use a controlled rollout and stop when a safety or quality guardrail is breached. Do not target individual spenders or optimize for longer sessions regardless of player benefit.

## Operator checklist

- Verify the candidate build and environment.
- Check whether current dashboards are delayed or incomplete; Roblox documentation notes that new custom-event charts can take time to populate.
- Confirm sample size and snapshot freshness.
- Review warnings and alerts alongside qualitative reports.
- Confirm the feature flag, disable path, and rollback owner.
- Keep an incident log with aggregate evidence only.
- Recheck the release plan and manual approvals from V30 before production changes.

V31 does not schedule events, change feature flags, send notifications, publish an experience, deploy a change, or access Creator Dashboard. All live operations remain human-approved.
