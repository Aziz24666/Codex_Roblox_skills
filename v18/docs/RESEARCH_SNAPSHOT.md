# V18 Research Snapshot — 2026-11-22

This snapshot records the official documentation checked for V18's workflow architecture. Re-open sources before future tasks because platform capabilities and tools change.

| Area | Source | V18 consequence |
|---|---|---|
| Codex repo workflows | https://developers.openai.com/blog/skills-agents-sdk | OpenAI's Codex repo examples use `AGENTS.md`, repo-local `.agents/skills/`, optional skill scripts/resources, and CI for repeatable workflows. |
| Codex prompts and instructions | https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra | Keep skill descriptions and repository instructions concise, scoped, and useful; revisit inherited prompt scaffolding as models improve. |
| Skill package structure | https://developers.openai.com/plugins/build/skills | A skill uses a `SKILL.md` manifest with `name` and `description`, plus optional references, scripts, and assets. |
| Responses API multi-agent | https://developers.openai.com/api/docs/guides/responses-multi-agent | The Responses API multi-agent guide is API-specific and beta; it is not evidence that a local Codex client exposes subagents. |
| Roblox Studio MCP | https://create.roblox.com/docs/studio/mcp | Studio MCP is built into Studio; client connection and per-instance targeting are required. |
| Studio TestService | https://create.roblox.com/docs/reference/engine/classes/StudioTestService | Scripted playtest methods have Studio/plugin security and are not ordinary game-script APIs. |
| DataStores | https://create.roblox.com/docs/cloud-services/data-stores | Studio test DataStore access can affect live experience data; isolated test data is mandatory. |

## Known limitations

- Documentation snapshots do not prove the installed Codex runtime exposes subagents, MCP, or any particular model/tool. The Responses API multi-agent guide describes an API capability and must not be treated as a Codex CLI feature guarantee.
- The V18 CLI only provides deterministic local discovery, routing suggestions, scaffolding, and validation. It does not operate Codex itself.
- Studio, multi-client, device, live-service, and production checks require their actual environments.
