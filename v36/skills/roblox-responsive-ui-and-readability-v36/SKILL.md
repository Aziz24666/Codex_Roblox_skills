---
name: roblox-responsive-ui-and-readability
description: Plan and review Roblox UI layouts for readable text, safe areas, scaling, device variation, and resilient responsive behavior.
---
# Roblox responsive UI and readability

Use this skill for HUDs, menus, inventory, shop interfaces, dialogue, notifications, and onboarding.

## Workflow
1. List each screen, its hierarchy, primary action, and critical information.
2. Define supported viewport classes and orientation assumptions.
3. Use constraints, layouts, anchors, and scale/offset deliberately; avoid fixed pixel assumptions.
4. Protect important content from device safe areas, notches, and platform UI.
5. Define minimum readable text sizes and test long strings, localization expansion, and large text settings.
6. Establish overflow behavior for narrow screens: wrap, scroll, collapse, or move secondary content.
7. Keep primary actions visible and reachable; do not let decorative UI cover essential controls.
8. Test minimum and maximum supported viewport sizes and record screenshots or Studio evidence.

## Output
Provide a screen inventory, responsive rules, edge-case matrix, implementation plan, and concrete retest cases.

## Boundaries
Do not state that a layout works on all devices without testing. Avoid universal pixel-size claims; tune and verify against the game's actual target devices.
