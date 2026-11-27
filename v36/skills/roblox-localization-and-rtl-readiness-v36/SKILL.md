---
name: roblox-localization-and-rtl-readiness
description: Prepare Roblox experiences for localization, text expansion, pluralization, right-to-left review, and language-aware UI testing.
---
# Roblox localization and RTL readiness

Use this skill when preparing UI, dialogue, tutorials, notifications, item descriptions, and player-facing system messages for multiple languages.

## Workflow
1. Inventory all player-visible strings, including text assembled in code and error messages.
2. Move strings into a localization-friendly source; avoid concatenating translated fragments.
3. Use stable string keys and provide translator context for ambiguous terms.
4. Design for text expansion, wrapping, plural forms, variables, and missing translations.
5. Review right-to-left languages for alignment, ordering, punctuation, icons, and mixed-direction text.
6. Keep identifiers, code values, and player data separate from translated display strings.
7. Define a fallback locale and a safe missing-translation behavior.
8. Test representative long strings and RTL samples in Studio on target viewport classes.

## Output
Produce a string inventory, localization architecture, locale coverage matrix, RTL review checklist, and test evidence.

## Boundaries
Do not claim machine translation is publication-ready without human review. Do not translate player-generated content by bypassing Roblox text-filtering requirements. Avoid storing personal information in translation files.
