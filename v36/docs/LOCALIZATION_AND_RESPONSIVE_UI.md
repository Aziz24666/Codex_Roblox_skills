# V36 Localization and Responsive UI

## Localization readiness
Inventory all player-visible strings and externalize them behind stable keys. Provide translator context, locale fallback behavior, and review for pluralization, variables, long text, and right-to-left layouts. Do not assemble translated sentences from fragments.

## Responsive UI
Use layout constraints and deliberate scale/offset behavior. Check safe areas, viewport extremes, text expansion, scrolling, and reachability of primary actions. Do not rely on one desktop screenshot as proof of mobile readiness.

## Evidence
Capture representative Studio screenshots and device results for each supported viewport class. Keep the manifest free of personal data, credentials, private URLs, and unrestricted free-form notes.
