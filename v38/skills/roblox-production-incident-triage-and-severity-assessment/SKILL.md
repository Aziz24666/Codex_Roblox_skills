---
name: roblox-production-incident-triage-and-severity-assessment
description: Structure production incident intake, severity, ownership, and a timestamped response timeline for Roblox experiences.
---

# Roblox production incident triage and severity assessment

## Purpose
Turn a suspected production issue into a disciplined, evidence-linked incident record without guessing at impact or taking live action.

## Workflow
1. Confirm the incident record refers to the correct experience/environment and use UTC timestamps.
2. State observable symptoms separately from hypotheses. Record the signal source and opaque evidence reference; never copy raw player reports or personal data.
3. Identify affected service categories and the broadest defensible audience scope. Use aggregate counts or platform status, not identities.
4. Assess severity using player impact, scope, duration, critical gameplay/data integrity, and confidence. Mark unknown information as unknown. Do not downgrade solely because telemetry is missing.
5. Assign an incident commander and relevant technical, data, and communications owners. Record acknowledgement and handoff times.
6. Keep a chronological timeline: detected, triaged, investigation, mitigation, verification, communication, resolved.
7. Reassess severity when evidence changes. Document why each change occurred.
8. Keep the incident open while customer impact or verification remains unresolved.

## Severity principles
- Critical: widespread or severe disruption, material data-integrity risk, or essential gameplay unavailable for a broad audience.
- High: substantial player-facing degradation or a major feature/service affected.
- Moderate: bounded degradation with a workable path around it.
- Low: limited impact or non-urgent issue with no material service interruption.

These are triage guidelines, not an automatic classifier. Use organizational escalation rules where they are stricter.

## Roblox-specific checks
Consider DataStore availability/error rates and data integrity, matchmaking/teleport, networking/remotes, core gameplay, content delivery, economy/purchases, publishing, analytics, and moderation systems. Keep server-authoritative state authoritative. Do not recommend exposing secrets, bypassing platform safeguards, or disabling security checks as a quick fix.

## Output
Produce a timestamped incident record with facts, unknowns, severity rationale, owners, next update time, and a safe next action. Escalate any possible data loss, account compromise, exploit, privacy incident, or platform-wide fault to the appropriate human owner.

## Limits
This skill guides human triage. It does not detect outages, inspect telemetry, assign real severity, contact Roblox, or operate live systems.
