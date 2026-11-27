# Incident triage and service health

## Triage sequence
Establish the environment, detection timestamp, symptoms, source, and current owner. Maintain a distinction between observed facts, interpretations, and unknowns. Use timezone-aware timestamps and record UTC. Assign an incident commander, technical lead for high/critical incidents, and data/communications owners as needed.

## Severity
Assess scope, duration, player-facing functionality, data integrity, safety, and confidence. Critical/high severity requires prompt escalation and active ownership. Review severity when new evidence arrives; preserve the previous decision and rationale in the timeline.

## Health signals
Use aggregate error-rate, availability, latency percentiles, queue depth, failed operation counts, and platform status over defined windows. Compare with baselines. Include source, denominator, window, and confidence. Never write player identifiers, chat, contact information, credentials, or individual histories into incident records.

## Roblox-specific domains
Consider DataStore operations/consistency, matchmaking and teleport, networking, core gameplay, content delivery, purchase/economy, publishing, analytics, and moderation. A dashboard status is one input, not proof of experience impact.

## Decision record
Document impact scope, source references, unknowns, role acknowledgement, next update time, and the safest next step. The validator does not query live systems or calculate service health.
