---
name: roblox-experience-config-and-feature-flag-management
description: Implement Roblox Experience Configs with ConfigService, typed defaults, server-only reads, safe refresh boundaries, and feature-flag fallbacks.
---

# Roblox Experience Configs and feature flags

## Goal
Replace hard-coded tunables with documented, typed configuration while keeping gameplay authority on the server and avoiding unsafe mid-session changes.

## Roblox-native config architecture
- Use the InExperienceConfig repository for in-experience config keys.
- Read in game scripts through server-side ConfigService; it is not a client API. Production config values are not writable from the running experience. SetTestingValue() and ClearTestingValue() are test-only overrides for the current server instance, not a production config write path.
- Use ConfigService:GetConfigAsync() for global config snapshots and ConfigService:GetConfigForPlayerAsync(player) only when conditional config targeting is deliberately required.
- Treat ConfigSnapshot as a point-in-time snapshot, not a live mutable table.
- Use ConfigSnapshot.UpdateAvailable and ConfigSnapshot:Refresh() or a deliberate safe-boundary refresh strategy. After refresh, listen to GetValueChangedSignal() for keys whose runtime behavior can be safely updated.
- Use pcall around initial config acquisition and define explicit static fallbacks. Optional features should fail closed when the first snapshot cannot be loaded.

## Type and key governance
- Maintain a config registry with key, value type, default, owner, purpose, targeting mode, runtime apply policy, and fallback policy.
- Match every consumer's expected type to the registry type. Keep defaults within Roblox's documented type-specific limits.
- The Open Cloud InExperienceConfig repository supports at most 100 keys and key names up to 256 characters. Experience config guidance documents up to 1,000 active configs overall. Each config key supports up to 20 conditions and the experience supports up to 100 conditions.
- Review conditional rule order globally: Roblox applies the first matching rule. Never assume per-key rule order is independent.
- Use only attributes supported by the current Creator Hub documentation. Do not build custom player profiles or infer sensitive attributes for targeting.
- Never put API keys, credentials, session tokens, secrets, or private player data in config values.

## Feature flag design
- Use feature flags to gate optional functionality with a safe default.
- Keep monetization, currency, progression, and inventory mutation server-authoritative. A config change must not let a client grant itself currency, items, or entitlements.
- Use distinct flags for rollout exposure and operational kill-switches. Define who owns each flag and what happens if the config is missing or stale.
- Keep paid outcomes fixed and disclosed; do not introduce paid random outcomes, gambling, or pressure-based spending mechanics.

## Required deliverables
- Typed config registry and default values.
- Server-side ConfigService reader module.
- Snapshot refresh and fallback strategy.
- Feature flag inventory with owners, consumer references, and kill-switch semantics.
- Conditional targeting review where used.
