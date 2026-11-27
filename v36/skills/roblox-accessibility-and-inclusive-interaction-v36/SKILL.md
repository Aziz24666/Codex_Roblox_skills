---
name: roblox-accessibility-and-inclusive-interaction
description: Design and review Roblox gameplay and interface interactions for accessibility, input flexibility, readable feedback, and inclusive player experiences.
---
# Roblox accessibility and inclusive interaction

Use this skill when designing or auditing player-facing gameplay, menus, prompts, onboarding, settings, and interaction flows.

## Workflow
1. Inventory every player-facing surface and its purpose.
2. Identify supported devices and input methods; do not assume keyboard and mouse.
3. Provide clear focus/navigation behavior for keyboard and gamepad where relevant.
4. Never communicate important state through color alone; pair color with text, shape, icon, or animation.
5. Keep interaction targets understandable and provide clear success, error, and disabled states.
6. Offer readable text sizing and avoid relying on tiny text for essential instructions.
7. Provide alternatives for critical audio cues and avoid requiring audio-only information.
8. Respect player settings and provide reduced-motion alternatives when motion is nonessential.
9. Test with actual device classes and representative player journeys; record evidence and unresolved limitations.

## Output
Produce a surface inventory, device/input matrix, prioritized issue list, proposed fixes, and evidence-backed retest plan. Distinguish verified behavior from design intent.

## Boundaries
Do not claim a game is accessible from static inspection alone. Do not infer a player's disability or collect sensitive health information. Accessibility settings must not secretly change gameplay difficulty or disclose player preferences to others.
