# Analytics event governance and instrumentation

V31 introduces a small, reviewed event catalog and a bounded source audit for Roblox `AnalyticsService` use. The tools operate on local files only. They do not send events, connect to Roblox, run Studio, or collect any player data.

## Verify the current API before instrumentation

Roblox's current Creator Hub documentation states that custom events are sent from server scripts in published experiences, not from client scripts or Studio. Custom events unlock the Explore analytics page after events are tracked; new charts may take up to 24 hours to appear.

- [AnalyticsService API reference](https://create.roblox.com/docs/reference/engine/classes/AnalyticsService)
- [Custom events](https://create.roblox.com/docs/production/analytics/custom-events)
- [Event types and platform limits](https://create.roblox.com/docs/production/analytics/event-types)
- [Economy events](https://create.roblox.com/docs/production/analytics/economy-events)

The current Creator Hub documentation lists a maximum of 100 custom event names per experience, three custom fields, and 8,000 unique combinations across those three fields. It also documents a global AnalyticsService request limit of `120 + (20 × CCU)` per minute. These are platform limits, not recommended targets. Confirm the current docs when planning instrumentation because platform limits can change.

## Build the catalog before adding events

Copy `v31/examples/event-catalog.example.json` into the selected project at `.codex/analytics/event-catalog.json`. For each event, document:

- A stable name and a concrete product/quality question it answers.
- Why the event is necessary and who owns it.
- A completed privacy review.
- At most three custom fields with finite, short, non-identifying allowed values. Map each semantic field to exactly one slot: `CustomField01`, `CustomField02`, or `CustomField03`.
- A call budget estimate, where useful, tied to the expected peak concurrent-user count.

Avoid creating one event name per item, level, map, or cosmetic variant. Prefer a stable event name with a small, finite category field where that breakdown is useful. Do not put user IDs, player names, emails, IP addresses, device IDs, session IDs, raw chat, arbitrary text, or purchase histories in custom fields. Do not create individual-spender profiles or pressure-based targeting.

## Validate the catalog

```powershell
python ".\v31\tools\v31.py" validate-catalog --root "C:\Path\To\YourGame"
```

The validator checks event name uniqueness, the 100-event cap, the three-field cap, unique mappings to Roblox's `Enum.AnalyticsCustomFieldKeys.CustomField01.Name`, `CustomField02.Name`, or `CustomField03.Name` keys, finite allowed values, a conservative upper bound on custom-field combinations, an explicit privacy-review declaration, and the optional declared call budget. It is a contract linter, not Roblox runtime validation or a privacy certification.

## Audit existing Luau instrumentation

```powershell
python ".\v31\tools\v31.py" audit --root "C:\Path\To\YourGame" --catalog ".codex\analytics\event-catalog.json"
```

The audit inventories current AnalyticsService event methods (including journey events), flags deprecated methods, identifies likely client-context custom-event calls, compares static `LogCustomEvent` names with the approved catalog, and flags suspicious personal-data property access near an event call.

A static audit cannot resolve every dynamic event name, infer the actual execution context of shared modules, or understand arbitrary Luau dataflow. Treat findings as manual-review leads. Recheck the actual call site and customFields values before making changes. Never paste real player records into Codex to investigate an alert.

## Instrumentation review checklist

1. Confirm the event is emitted from the server and only in a published experience where the platform supports it.
2. Check whether Roblox's built-in engagement, retention, funnel, or economy analytics already answer the question.
3. Use a finite event name and only the custom fields needed for the stated purpose.
4. Do not send identifiers, free-text input, chat, support content, or unnecessary purchase details.
5. Avoid duplicate calls and uncontrolled per-frame/high-frequency events. Batch where the API and the semantic meaning permit it.
6. Test in an isolated test experience, then verify results in Creator Hub with an authorized role.
7. Revisit the catalog when a feature is removed or its purpose changes.

## Limits and safeguards

Custom-field slots in the catalog map to the only accepted Roblox keys: `Enum.AnalyticsCustomFieldKeys.CustomField01.Name`, `CustomField02.Name`, and `CustomField03.Name`. The combination check sums each event's Cartesian-product upper bound as a conservative catalog-level preflight; actual platform cardinality depends on values observed at runtime.

V31 does not add a runtime telemetry SDK, remote collector, DataStore, webhook, or automatic instrumentation rewrite. It does not verify dashboard permissions, event delivery, event aggregation, or actual API limits at runtime. Keep the event catalog minimal, aggregate-only in reports, and subordinate to platform rules and the project's privacy obligations.
