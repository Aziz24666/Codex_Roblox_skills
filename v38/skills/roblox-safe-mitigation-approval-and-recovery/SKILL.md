---
name: roblox-safe-mitigation-approval-and-recovery
description: Plan reversible, human-approved mitigations, rollback, and recovery for Roblox production incidents.
---

# Safe mitigation approval and recovery

## Operating rule
Do not equate an incident audit or proposed action with authorization. A named human owner must approve each high-risk mitigation, rollback, restore, or data-affecting operation outside the toolkit.

## Decision workflow
1. State the intended outcome and link the action to evidence and the active incident.
2. Identify risk, blast radius, expected player impact, dependencies, and what could make the action worse.
3. Prefer reversible, narrow, observable changes over broad or destructive operations.
4. Define a pre-action snapshot/backup or recovery point where relevant, and verify it is actually available before proceeding.
5. Record an approver reference and approval timestamp. The person who executes should verify the approved scope has not changed.
6. Define success and failure signals, observation window, stop conditions, rollback trigger, and owner before execution.
7. After execution, verify the intended service and data behavior with independent evidence. Record applied/reverted status and evidence reference.
8. If verification fails, stop further changes and escalate to the incident commander; do not improvise a second destructive action.

## Roblox-specific safeguards
- Never disable server authorization, remote validation, TextService filtering, rate limits, or purchase validation as a quick mitigation.
- Treat DataStore restore/migration as high risk. Preserve backups, schema compatibility, idempotency, and concurrency controls.
- Roll back client and server versions only after compatibility and persisted-data implications are reviewed.
- For economy or purchase issues, preserve transaction integrity and reconcile through authorized platform workflows rather than manually granting/removing balances.

## Output
A mitigation proposal, explicit approval record, preconditions, verification plan, stop criteria, and recovery decision. Every action must be traceable to the incident.

## Limits
The skill does not execute commands, publish versions, roll back deployments, edit production data, or approve actions.
