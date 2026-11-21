# V18 Research Snapshot — 2026-11-20

This snapshot records the official documentation checked for V18's workflow architecture. Re-open sources before future tasks because platform capabilities and tools change.

| Area | Source | V18 consequence |
|---|---|---|
| Codex skills | https://learn.chatgpt.com/docs/build-skills | Skills use `SKILL.md` frontmatter and can include scripts/resources; discovery relies on concise metadata and progressive disclosure. |
| Codex customization | https://learn.chatgpt.com/docs/customization/overview | Durable project instructions, skills, MCP, and subagents serve different roles; avoid duplicating them. |
| Codex subagents | https://developers.openai.com/api/docs/guides/responses-multi-agent | Delegate independent bounded work; avoid shared-file contention and unnecessary agent overhead. |
| Roblox Studio MCP | https://create.roblox.com/docs/studio/mcp | Studio MCP is built into Studio; client connection and per-instance targeting are required. |
| Studio TestService | https://create.roblox.com/docs/reference/engine/classes/StudioTestService | Scripted playtest methods have Studio/plugin security and are not ordinary game-script APIs. |
| DataStores | https://create.roblox.com/docs/cloud-services/data-stores | Studio test DataStore access can affect live experience data; isolated test data is mandatory. |

## Known limitations

- Documentation snapshots do not prove the installed Codex runtime exposes subagents, MCP, or any particular model/tool.
- The V18 CLI only provides deterministic local discovery, routing suggestions, scaffolding, and validation. It does not operate Codex itself.
- Studio, multi-client, device, live-service, and production checks require their actual environments.
