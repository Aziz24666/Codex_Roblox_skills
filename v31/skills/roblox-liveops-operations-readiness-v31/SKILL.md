---
name: roblox-liveops-operations-readiness-v31
description: Prepare Roblox LiveOps changes with explicit owners, monitoring, stop conditions, rollback plans, and privacy-minimal evidence.
---

# LiveOps Operations Readiness

## Before an operation

1. Describe the player-facing purpose and the systems affected.
2. Record start/end times, operator, review owner, environment, and audience eligibility rules.
3. Confirm that the experience remains understandable and enjoyable without spending.
4. Identify the feature-flag or configuration disable path and a tested rollback method.
5. Define monitoring indicators and the exact thresholds that trigger a pause.
6. Prepare concise player-support and team-communication notes.
7. Obtain required release approvals under V30 before production changes.

## During an operation

- Use a controlled rollout rather than changing every environment at once.
- Monitor aggregate technical health, errors, purchase failures, and support reports.
- Stop when a predeclared safety or quality guardrail is breached.
- Record decisions and timestamps without copying personal player data into reports.
- Do not extend a run merely to chase a preferred metric.

## After an operation

Compare the stated hypothesis with observed aggregate results and qualitative feedback. Record unexpected effects, unresolved risks, and whether to keep, change, or remove the feature. Preserve a rollback-ready known-good configuration.

## Safety

Do not automate production publishing, flag changes, notifications, or destructive operations. Do not use fake scarcity, forced sessions, pressure messaging, paid chance, or individual-spender targeting.
