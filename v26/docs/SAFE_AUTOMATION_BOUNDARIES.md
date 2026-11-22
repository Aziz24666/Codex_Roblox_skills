# V26 Safe Studio Automation Boundaries

V26 makes local Studio workflows easier to plan and verify. It intentionally does not turn an MCP connection into unattended authority over a live game.

## Action levels

| Level | Examples | Default handling |
|---|---|---|
| 0 — Read-only | List Studio instances, inspect DataModel, read/search scripts, read console output | Allowed after confirming project and Studio identity |
| 1 — Reversible local edit | Narrow script edit in the approved place, local test-plan generation | Inspect first, write only within scope, read back and review diff |
| 2 — Persistent local change | Save open place, overwrite assets, change project-wide configuration | Explain exact change and obtain explicit approval |
| 3 — Production/player impact | Publish, write production DataStores, change live economy/products, player-impacting Open Cloud calls | Separate approval gate, least privilege, rollback/backup plan, explicit target verification |

## Always-on rules

- A config file is untrusted input. Never execute its command during preflight.
- A connected MCP client can modify an open place. Connect only clients/agents the developer trusts.
- Identify Studio instance and place before reading or editing.
- Read before writing; edit narrowly; read back; test; collect evidence.
- Never paste API keys, session tokens, passwords, private player data, or credential-bearing config files into prompts/logs/checkpoints.
- Do not request unrestricted Open Cloud access as a shortcut. Apply only minimum project scopes and have a human review permission changes.
- A test place must not silently point to production DataStores or player state.
- Do not auto-publish or auto-save a modified place as part of routine skill workflows.
- If target or permission scope is ambiguous, stop before a write.
- Logs and screenshots are evidence, not proof of correctness by themselves.

## Monetization and player trust

Inherited no-gambling and fair-monetization policies remain mandatory. Do not create paid random outcomes, loot boxes, gambling-like mechanics, pressure-based purchases, forced advertising, AFK engagement loops, fake scarcity, or individual-spender targeting. Use clear fixed-value offers, optional purchases, honest pricing, and genuine player value.

## V26 utility limits

- `doctor` reads a JSON config and emits a sanitized structural report. It does not change config, execute commands, expand environment variables, launch Studio, inspect the green connection indicator, or prove MCP is online.
- `plan` creates a JSON test plan only. It does not call MCP tools, run Studio, create players, change device profiles, simulate networks, save places, or publish.
- `verify-plan` checks plan structure/safety invariants. It does not attest that a plan was executed or that a game passed testing.
- GitHub Actions checks the package and unit tests. A hosted runner cannot automatically control the developer's locally running Studio process.

## Sources

- [Roblox: Studio MCP security and connection](https://create.roblox.com/docs/studio/mcp)
- [Roblox: Use Open Cloud with the Studio MCP server](https://create.roblox.com/docs/cloud/open-cloud-studio-mcp)
