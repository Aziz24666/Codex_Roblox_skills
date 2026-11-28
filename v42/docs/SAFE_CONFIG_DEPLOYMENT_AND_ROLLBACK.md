# Safe config deployment and rollback

## Open Cloud permissions

For the Experience Configs Open Cloud workflow, read operations use universe:read. Draft, publish, and restore operations require universe:write. Use an approved key or OAuth application with the smallest scope required. Keep credentials in an approved secret manager or protected environment variables, never in the repository, JSON manifest, command output, or logs.

## Deployment workflow

1. Read the current published config and revision history.
2. Stage a partial draft when changing a few keys; a full overwrite treats omitted keys as removed.
3. Save the returned draftHash. Use previousDraftHash when performing a subsequent write to detect a concurrent draft change.
4. Validate the candidate manifest and compare it with the current baseline.
5. Test staged config values in Studio or an isolated test experience.
6. Review the exact diff, test evidence, publish message, rollout strategy, and fallback.
7. Obtain explicit human approval.
8. Publish with Immediate or GradualRollout. GradualRollout is a 15-minute rollout option in the current Open Cloud guide.
9. Read the published values back and verify the expected config version and values.
10. Observe aggregate health signals over a predeclared window.

## Rollback

Config revision restore stages the prior values as a new draft and clears any existing staged draft. It does not publish automatically. Inspect the staged restore, approve it, publish it with a descriptive message, and read back the published values. Refresh server snapshots at safe gameplay boundaries and verify consumers.

Do not auto-publish a rollback based only on a CLI warning. A human operator must confirm the affected feature, the target revision, the restore diff, and the player impact.

## Compatibility migration

When a config key or type must change, prefer an additive migration:
1. Add a new key while retaining the old key.
2. Deploy code that can read both contracts.
3. Migrate config values and verify the new consumer.
4. Confirm all deployed code versions have stopped reading the old key.
5. Remove the old key in a separately reviewed release.

The V42 compare command flags removed keys and changed types as breaking and default changes as review-required. It does not search Luau; inspect the actual project source and version-control diff.
