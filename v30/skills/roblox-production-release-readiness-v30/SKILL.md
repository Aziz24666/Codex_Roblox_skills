---
name: roblox-production-release-readiness-v30
description: Prepare and review evidence-based Roblox staging and production releases with explicit environment-specific gates and human authorization.
---

# Roblox Production Release Readiness

## Goal

Produce a candidate-specific release dossier and a defensible hold/ready recommendation. Keep the decision distinct from the publish action: Codex may review evidence, but publishing remains a manual operation by an authorized human.

## Workflow

1. Identify the exact source revision, candidate version, target environment, place, configuration, and release summary.
2. Confirm the plan is tied to that candidate. Do not carry test evidence forward from a different revision without a documented reason and reviewer decision.
3. Run the applicable functional, multiplayer, server-authority, persistence, security, Studio smoke, and performance checks in isolated environments.
4. Review V29 performance captures under equivalent device/scenario conditions. Treat static Luau scans as investigation leads, not measured results.
5. Review V28 remote boundaries, DataStore compatibility, retries, idempotency, and migration plans.
6. Review monetization against fixed outcomes, clear prices, fair free progression, and the no-gambling policy.
7. Verify rollback and backup readiness. Production needs a staged rollout and the production approval roles.
8. Use the V30 release-plan validator to check manifest structure and local evidence references.
9. Present missing, failed, blocked, stale, or mismatched evidence explicitly. Recommend HOLD when a required gate is incomplete or evidence does not match the candidate.
10. Leave the final publish decision and action to the authorized release owner.

## Gate policy

- Development: functional test evidence.
- Staging: functional tests, server-authority, persistence, security, and Studio smoke evidence.
- Production: all standard V30 gates, staged rollout, rollback/backup references, and release-owner, QA-lead, and security-reviewer approval records.
- A DataStore migration adds migration validation; production also needs data-owner approval.

## Output format

Summarize candidate identity, environment, passed gates, failed/blocked/not-run gates, evidence limitations, rollback readiness, open risks, and recommended next decision. Never describe a manifest as a live verification or a validator result as permission to publish.

## Safety

Do not publish places, update live configuration, run migrations, write production DataStores, or perform player-impacting operations. Preserve all prior V1-V29 safeguards.
