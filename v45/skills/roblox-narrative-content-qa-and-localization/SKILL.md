---
name: roblox-narrative-content-qa-and-localization
description: Review Roblox quest and dialogue content for graph coverage, writing consistency, localization, accessibility, and release evidence.
---

# Roblox narrative content QA and localization

Cover each quest start, prerequisite, objective type, branch, completion path, and repeat policy. Cover each conversation start, line, choice, loop, and ending. Add negative cases for missing references, unavailable actors, stale content versions, disconnects, and invalid choices. Link issues to stable IDs, not movable line numbers.

Review graph structure and prose. Confirm required objectives are reachable and completable, each dialogue node can reach an ending, and prerequisite cycles do not block availability. Structural validity does not prove story quality.

Ensure objective text describes an observable action, progress feedback explains what changed, and completion text makes the next step clear. Choice labels must be distinct and consistent with their outcomes. Keep optional dialogue optional and provide clear close/continue actions.

Review age-appropriate tone, player safety, accessibility, and moderation using existing toolkit guidance. Do not ask players to disclose personal information through narrative content.

Use stable text keys, a declared default locale, and supported-locale list. Review placeholders, formatting, right-to-left layout, text expansion, line breaks, font coverage, and speaker attribution. Provide translator context. Check touch, keyboard, gamepad, text scaling, reading time, captions, and reduced-motion alternatives.

Version content with its consuming code. Require content-owner, engineering, localization, accessibility, and safety review plus private-experience playtesting. Offline validation cannot verify translations, moderation, runtime rendering, comprehension, or rollout.
