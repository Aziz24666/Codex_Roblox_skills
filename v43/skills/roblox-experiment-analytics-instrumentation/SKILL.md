---
name: roblox-experiment-analytics-instrumentation
description: Instrument Roblox experiments with stable server-side AnalyticsService events, funnels, privacy review, and bounded custom metric cardinality.
---

# Roblox experiment analytics instrumentation

## Use Roblox-supported analytics
Use the current server-side AnalyticsService logging methods for progression, custom events, and funnel steps. Check the current Creator Hub API reference and event limits before implementation; do not use deprecated Fire* methods in new code.

## Custom events
- Log custom events from server scripts in published experiences. Custom events cannot be sent from the client or Studio.
- Choose stable event names for meaningful player actions, such as OnboardingStarted or FirstQuestCompleted.
- Prefer a small stable event-name set with reviewed custom-field values rather than creating a new event name for every item, player, level, or content variation.
- Roblox documents a maximum of 100 custom event names per experience. Each economy, funnel, or custom event supports up to three custom fields; after 8,000 combined unique values across those fields, values are grouped as Other. Custom-event aggregations are daily and may take up to 24 hours to appear.
- Use counters for one-time actions and value events for a measured quantity. Keep value units consistent.
- Do not log raw user text, account identifiers, secrets, or unnecessary personal data in custom fields.

## Funnels and custom metrics
- Use funnel steps for ordered progress such as onboarding. Roblox supports up to 10 unique funnels per experience and 100 steps per funnel. Use the same funnel name and session identifier for steps in a recurring funnel.
- Register and validate events before starting the experiment; newly created events may not yet be available in the metric selector.
- Roblox in-game experiments support up to three custom metrics. Select source, calculation, denominator, and filters before start.
- Keep the event schema stable throughout the experiment. Changing event names, definitions, or funnel behavior mid-test can invalidate comparisons.

## Required review
- Server-only event source and published-experience check.
- Event naming and cardinality audit.
- Privacy and custom-field review.
- Stable value units and funnel step definitions.
- Pre-start test evidence and confirmation that the events are available in Creator Hub.

## Safeguards
- Analytics instrumentation must not be used to identify or profile individual players unnecessarily.
- Do not record raw chat, private messages, credentials, or sensitive personal attributes.
- Do not collect extra data simply because it is technically available.
