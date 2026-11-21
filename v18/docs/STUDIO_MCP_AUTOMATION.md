# V18 Roblox Studio MCP Automation

Roblox Studio includes a built-in MCP server in current Studio releases. When a compatible Codex client is connected and the developer enables the server, the agent can inspect the DataModel, read/search/edit scripts, run Luau commands, and interact with playtests using the tools actually exposed by that Studio version. Always discover the connected Studio instance first and target it explicitly.

## Setup overview

1. Update Roblox Studio through the official supported channel.
2. In Studio Assistant settings, open MCP Servers and enable Studio as an MCP server.
3. Use Studio's Quick Connect option for Codex CLI where offered, or follow the currently documented Windows configuration.
4. Restart/refresh the Codex client if required, then verify that the MCP server and target Studio instance are visible.
5. Read the current Studio MCP tool list and permissions before using any action. Tool names and capabilities can change.

## Safe workflow

- Start with read-only script/DataModel inspection and a task-scoped map.
- Confirm the correct Studio instance/place before edits.
- Keep edits limited to approved workstream paths.
- Use test-only fixtures and isolated data. Never connect a test workflow to production DataStores by assumption.
- Use Studio test automation and multi-client playtests only when a real Studio session and current plugin permissions support them.
- Save only after inspecting the diff. Publishing remains a separate approval-gated action.

## Capability limits

An installed skill or configuration example does not mean Studio MCP is connected. The utility does not silently configure a client's global MCP settings. Do not claim playtest success unless Studio actually ran the scenario and supplied evidence.
