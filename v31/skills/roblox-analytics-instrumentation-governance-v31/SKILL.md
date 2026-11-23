---
name: roblox-analytics-instrumentation-governance-v31
description: Design a minimal, privacy-reviewed Roblox AnalyticsService event catalog and verify instrumentation against current server-side API guidance.
---

# Analytics Instrumentation Governance

## Workflow

1. State the specific gameplay or service-quality question each event answers.
2. Prefer platform-provided analytics when they already answer the question.
3. Define stable event names, purpose, owner, and reviewed finite custom fields in the V31 catalog.
4. Map each semantic field to exactly one Roblox slot: `CustomField01`, `CustomField02`, or `CustomField03`, which correspond to `Enum.AnalyticsCustomFieldKeys.<slot>.Name`.
5. Keep custom events within the documented experience limits: 100 event names, three custom fields, and 8,000 unique combinations across the three slots.
6. Use low-cardinality category labels. Never send player identifiers, personal data, raw chat, arbitrary text, or individual purchase histories as custom fields.
7. Keep AnalyticsService calls on authoritative server paths and verify the current API docs before use.
8. Run the V31 catalog validator and source audit; review every finding manually.
9. Verify delivery in an authorized published test experience, not by assuming that a source scan proves runtime behavior.

## Quality rules

- Do not emit analytics every frame or from uncontrolled loops.
- Avoid unique event names for each content variant when one stable event plus a bounded category field would work.
- Respect Roblox's rate limits and event-aggregation delay.
- Do not fabricate telemetry or report a static source scan as measured analytics.

## Safety

Only use aggregate, purpose-bound reporting. Do not build individual-spender profiles, hidden behavioral dossiers, paid chance systems, or manipulative engagement loops. Keep all V1-V30 safeguards.
