# Device, Orientation, and Input Testing

## Choose supported targets

List the actual platforms and input methods the experience supports. Do not test a VR path if the experience does not support VR, and do not claim a mobile pass from a desktop-only test.

## Studio device simulation

Studio's Device Simulator previews device screen dimensions, pixel density, on-screen keyboard, and touch input. Controller Emulator covers gamepad and related device inputs. StudioDeviceSimulatorService can automate device preset selection and selected simulation properties from a plugin or authorized Studio tool.

Important API boundaries:

- Service methods are asynchronous and yield.
- State-changing simulation methods are blocked in PlayServer mode; use Edit mode or Play Client as documented.
- Built-in presets are immutable.
- Resolution/DPI overrides require an active device and are session-level.
- Switching devices clears session overrides; restore or stop the simulation during cleanup.

## Virtual input

UserInputService:CreateVirtualInput may return nil; check availability before use. VirtualInput can send mouse, keyboard, pointer, and text input for test purposes. Its events are limited to the experience's own UI and cannot interact with Roblox CoreGui such as the top bar, chat window, or escape menu.

Do not treat a successful input injection as a successful feature action. Assert the resulting game/UI state.

## Acceptance checklist

- Essential actions are visible and reachable.
- No important controls overlap or clip at supported sizes.
- Portrait/landscape transitions preserve UI state.
- Touch controls, scroll regions, and text entry behave as designed.
- On-screen keyboard does not conceal the field or required action.
- Controller focus order is logical and recoverable after dialogs.
- Loading, error, empty, and success states remain clear.
- Layout changes do not break the core gameplay loop.

## Links

- Studio testing modes: https://create.roblox.com/docs/studio/testing-modes
- StudioDeviceSimulatorService: https://create.roblox.com/docs/reference/engine/classes/StudioDeviceSimulatorService
- VirtualInput: https://create.roblox.com/docs/reference/engine/classes/VirtualInput
- UserInputService: https://create.roblox.com/docs/reference/engine/classes/UserInputService
