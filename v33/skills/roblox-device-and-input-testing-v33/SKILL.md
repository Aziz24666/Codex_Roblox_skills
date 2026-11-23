---
name: roblox-device-and-input-testing-v33
description: Plan and execute Roblox Studio device, orientation, touch, keyboard, controller, and responsive UI checks using the supported Device Simulator, Controller Emulator, and VirtualInput boundaries.
---

# Roblox Device and Input Testing

## Goal

Verify that an experience remains usable across the devices and input methods it claims to support. Do not treat a desktop viewport resize as proof of a complete mobile or controller experience.

## Coverage matrix

Select actual supported targets and create separate test cases for:

- Phone portrait and landscape.
- Tablet portrait and landscape.
- Desktop window sizes and common aspect ratios.
- Console/controller navigation where supported.
- VR only when the project intentionally supports VR.
- Touch, mouse/keyboard, gamepad, and on-screen keyboard flows.
- Text-entry, dialogs, inventory, shop, settings, onboarding, and core gameplay UI.
- Camera behavior, safe-area placement, scrolling, focus, and readable feedback.

## StudioDeviceSimulatorService

The StudioDeviceSimulatorService provides scripted control over Studio's Device Simulator. Its methods are asynchronous. State-changing operations are not allowed in PlayServer mode; use edit mode or Play Client as documented. Built-in presets are immutable. Resolution and DPI overrides require an active device, are session-level, and are cleared when switching devices. Avoid creating permanent custom profiles for a one-off automated test unless the team explicitly wants that profile saved.

A test should select a supported profile, apply only the required orientation or resolution override, wait for the simulator operation to complete, run UI assertions, and restore or stop the simulation during cleanup. Record the exact device profile and orientation.

## VirtualInput

UserInputService:CreateVirtualInput can return nil when unavailable; always check before calling it. VirtualInput can simulate mouse, keyboard, pointer, and text input for test purposes. Its events are limited to the experience's own UI and cannot interact with Roblox CoreGui such as the top bar, chat window, or escape menu. Do not write automation that assumes it can control system UI.

Check focus, input consumption, accessibility of the primary action, and resulting UI state. A click being sent is not proof that the intended action succeeded; assert the resulting state.

## Device acceptance checks

- No essential controls are clipped, obscured, or too small to use.
- Orientation changes do not strand the player in a broken layout.
- Touch targets and scroll areas behave as intended.
- Keyboard appearance does not cover the active input or submit action.
- Controller focus is visible, logical, and recoverable after dialogs close.
- Back/cancel behavior is consistent.
- Loading, error, and empty states remain understandable.
- Layout and interaction tests cover each supported target, not only a sample desktop viewport.

## Reporting

Record test IDs, device profile, orientation, input type, Studio version, status, fixed outcome code, and opaque evidence reference. Do not claim coverage for a device or input mode that was not actually tested.
