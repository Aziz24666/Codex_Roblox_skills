# Feedback triage and action traceability

## Triage categories

Classify a theme as a confirmed defect, usability friction, accessibility barrier, preference, feature request, or unverified report. Route security vulnerabilities, player-safety concerns, and production incidents through their separate processes.

## Candidate action record

An action proposal should contain:
- Stable action ID and concise problem statement.
- Related theme and study-scoped evidence references.
- Severity, confidence in interpretation, and known sample limitations.
- Owner role, dependencies, risk, and target review date.
- Testable acceptance criteria and a regression plan.
- Human decision: accept, investigate, defer, or decline, with rationale.

A proposed action is not an approved task or a shipped feature. A person with the appropriate project authority must accept it.

## Prioritization

Consider impact, reproducibility, affected core loop, number of independent evidence sources, accessibility implications, risk, effort, and confidence. Do not rank solely by submission frequency. A single reproducible blocker can outweigh many low-impact preferences.

## Close the loop

After implementation, validate the fix on the relevant devices and game modes. Add a regression case when appropriate. Communicate only verified changes; do not promise delivery dates or expose participant submissions.
