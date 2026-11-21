# V20 Live Operations and Safe Rollouts

## Before promotion

Treat each deployment as a controlled change with an owner, release identity, risk statement, promotion criteria, rollback plan, and evidence record. Use V19's test-plan and evidence tools for actual checks. A green package workflow is not a production approval.

## Promotion stages

| Stage | Purpose | Required evidence |
|---|---|---|
| Development | Fast iteration with isolated test data | Unit/static checks and developer scenario |
| Staging | Integration against release-like configuration | Regression results, schema compatibility and service checks |
| Canary | Small, bounded exposure with explicit stop conditions | Health metrics, error/latency comparison and owner sign-off |
| Production | Broader rollout after canary review | Promotion approval, release identity and monitoring owner |

Do not infer canary success from a deployment job completing. Define a measurable observation window and stop conditions before promotion.

## Feature flags and kill switches

- Keep flag names, owner, default state, scope, and expiry/review date documented.
- Make disabling the feature safe for existing data and in-flight operations.
- Confirm server acknowledgement and observable state after toggling.
- Use a kill switch for containment; do not mistake it for a rollback of incompatible data changes.
- Avoid permanent flag accumulation. Remove flags only after all supported clients/data versions no longer need them.

## Rollback and data compatibility

- Prefer disabling the feature or reverting compatible code before restoring data.
- Never blindly restore an old snapshot over newer player writes.
- Keep schema readers/writers compatible through the rollout window.
- For irreversible migrations, require a forward-recovery plan and owner approval; a source-control revert cannot reverse changed player data.
- Preserve failed promotion evidence and incident context.

## Incident response

1. Detect and acknowledge the alert; identify the affected build, place, region, and player cohort where available.
2. Contain the issue using an approved flag or bounded mitigation.
3. Preserve relevant logs and metrics while redacting personal data and secrets.
4. Determine whether the incident affects authority, persistence, economy, availability, or data integrity.
5. Escalate to the named service/data owner before destructive recovery.
6. Restore service using the documented rollback or forward-recovery path.
7. Verify recovery in the proper environment and record residual risk, follow-up owners, and prevention work.

## Approval boundary

Publishing, changing live configuration, disabling a production feature, touching live player data, or fulfilling real purchases are external effects. Require the appropriate owner approval and use test places, test accounts, and isolated stores for rehearsal. Do not treat this document as authorization to perform any live operation.
