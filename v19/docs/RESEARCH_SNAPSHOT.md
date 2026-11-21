# V19 Research Snapshot

Reviewed against Roblox Creator Hub documentation on 2026-11-21. These links are living documentation; re-check the current page before implementing against an API.

| Area | Verified guidance | Official reference |
|---|---|---|
| Luau type checking | Luau supports gradual typing and the \`--!nocheck\`, \`--!nonstrict\`, and \`--!strict\` modes. Prefer gradual migration, with strict checks at well-owned boundaries before widening scope. | https://create.roblox.com/docs/luau/type-checking |
| StudioTestService | Studio plugins can automate Test/Run modes, including multi-client scenarios and player lifecycle operations. | https://create.roblox.com/docs/reference/engine/classes/StudioTestService |
| Studio MCP | Studio's built-in MCP server exposes local-session tools; clients must explicitly discover and target a connected Studio instance. | https://create.roblox.com/docs/studio/mcp |
| Studio testing modes | Playtest modes exercise the client/server model inside Studio; select the mode that matches the scenario. | https://create.roblox.com/docs/studio/testing-modes |
| Performance diagnostics | Use Developer Console, MicroProfiler, performance stats, network simulation, and performance dashboard according to the environment and question being measured. | https://create.roblox.com/docs/performance-optimization/identify |

This snapshot records source locations and a summary, not a permanent API guarantee. The docs may change.
