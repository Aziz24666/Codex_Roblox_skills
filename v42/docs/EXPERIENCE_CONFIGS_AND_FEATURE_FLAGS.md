# Experience Configs and feature flags

## Runtime

Roblox Experience Configs are read in game scripts through ConfigService. ConfigService is server-only and read-only at runtime. Use GetConfigAsync() for global configs and GetConfigForPlayerAsync(player) for conditional values. Do not try to call ConfigService from a LocalScript or write to the repository from a game server.

A ConfigSnapshot represents the values at the moment it was requested. Use UpdateAvailable with Refresh(), or refresh deliberately at a safe boundary. A published change does not mean every existing snapshot has already changed. For active matches or encounters, defer non-emergency tuning until a round/event boundary.

Wrap initial config loading in pcall and define a static fallback. For optional features, safe failure is usually disabled. Do not use a nil config as permission to turn on an experimental feature.

## Registry and limits

Maintain a config registry with key, value type, default, owner, purpose/category, targeting mode, fallback, and runtime apply policy.

Roblox documentation currently describes:
- InExperienceConfig Open Cloud repository: at most 100 keys; key names up to 256 characters.
- Experience Configs: up to 1,000 active configs.
- Conditional configs: up to 100 conditions per experience and up to 20 conditions per config key.
- String and JSON values: maximum 100,000 characters.
- Conditional rule ordering is global: first matching rule applies.

Always re-check current official limits before a large configuration migration. Keep targeted configs limited to documented attributes and legitimate game configuration needs. Never use experience configs to hold credentials, API keys, private player data, or hidden secrets.

## Feature flag design

Separate:
- Release flags: control exposure of a feature.
- Operational kill-switches: disable a feature when a known safety or reliability issue occurs.
- Balance tunables: change numeric or structured game parameters.
- Event-control flags: activate or disable a scheduled event.

Each key must have an owner, default value, missing-config behavior, and list of server-side consumers. Keep all important reward and progression mutations server-authoritative. A remote config value is an input to server logic, not an authorization token.
