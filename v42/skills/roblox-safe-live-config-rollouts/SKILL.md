---
name: roblox-safe-live-config-rollouts
description: Plan safe staging, testing, gradual publication, readback, and operational monitoring for Roblox experience config changes.
---

# Safe LiveOps config rollouts

## Goal
Ship remote configuration changes deliberately, with an auditable draft, a known publish plan, and verification that the intended values reached the experience.

## Open Cloud config workflow
1. Authenticate through an approved Open Cloud API key or OAuth application with the least required scope. Read operations use universe:read; draft, publish, and restore operations require universe:write.
2. Keep API credentials outside the repository, source files, logs, screenshots, and model manifests. Never ask Codex to print or commit a secret.
3. Read the current config before editing. Save the latest draftHash and use previousDraftHash on a subsequent write when supported to detect concurrent edits.
4. Prefer partial draft updates when changing a few keys. A full overwrite treats omitted keys as removed; inspect the full desired state before using it.
5. Stage the draft. Validate key names, types, defaults, conditions, consumer compatibility, schedule windows, and test scenarios.
6. Test staged values in Studio or an isolated test experience. Verify that all relevant server consumers use the intended snapshot and fallback.
7. Require explicit human approval before publish. Use a descriptive publish message and the selected Immediate or GradualRollout strategy.
8. Read the published config back and verify the exact values and version. Record the evidence and who approved the change.

## Runtime rollout behavior
ConfigSnapshot values do not automatically mutate when a config is published. Refresh at a safe boundary, especially for competitive rounds and active encounters. Prefer GradualRollout when a measured incremental rollout is useful; do not treat a rollout strategy as proof that runtime code is compatible.

## Operational checks
Define an aggregate health window, minimum sample size, warning thresholds, and a stop/rollback decision before publication. Keep telemetry aggregate and purpose-bound. A rollout should be paused for unexplained error or service-health changes; live mitigations require an authorized human operator.

## Required deliverables
- Config diff and compatibility report.
- Draft hash and publish message.
- Staged test evidence and approval.
- Rollout strategy and observation window.
- Published readback and rollback rehearsal.

## Non-negotiable safeguards
- Staging and tests precede publication.
- No credential values in manifests or source control.
- Explicit human approval gates production publish.
- Never assume a config publish instantly rewrites existing ConfigSnapshot objects.
