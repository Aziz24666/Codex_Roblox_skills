# AnalyticsService instrumentation for experiments

## Event source and availability

Roblox custom events are sent from the server in published experiences. They cannot be sent from the client or Studio. New custom events are aggregated daily and may take up to 24 hours to appear in Creator Hub analytics.

Use the current AnalyticsService methods such as LogCustomEvent, LogFunnelStepEvent, and the supported progression/economy event APIs. Do not introduce new code using deprecated Fire* APIs.

## Event design

- Use a stable event name for a meaningful action, not for each player, item, or arbitrary parameter combination.
- Prefer custom-field breakdowns to multiplying event names, and use only supported field keys/values.
- Keep names, value units, funnel step numbers, and session IDs consistent.
- Use a counter for a discrete action and a value event for a measured quantity.
- Keep raw text, player identifiers, credentials, and unnecessary personal data out of custom fields.
- Roblox documents a maximum of 100 custom event names per experience.

## Funnel and custom metric planning

Use a funnel for ordered steps such as onboarding. Keep funnel names and steps consistent. Recurring funnels need a stable funnel-session identifier so a repeat attempt is not mixed with a previous one.

Build custom metrics only from events that already have data. Roblox in-game experiments support up to three custom metrics. Select the source and calculation before starting the experiment; the definition cannot be changed after start.

## Validation checklist

1. Confirm every event fires on the server only.
2. Confirm the test is performed in a published test experience, not Studio.
3. Check the event appears in Creator Hub after processing.
4. Confirm event names and field cardinality stay within documented limits.
5. Verify all variants use the same event definition and unit.
6. Freeze instrumentation during the experiment unless a critical bug must be corrected; document any correction and its impact.
