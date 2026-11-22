# V26 Studio MCP Workflow

Updated 2026-11-22 against the official Roblox Creator Hub Studio MCP documentation.

## What Studio MCP does

Roblox Studio includes a local MCP server. After the developer enables it and connects a compatible MCP client, an agent can interact with the open Studio session through the tools exposed by that Studio version. Depending on the installed Studio build, available tool groups may include:

- Studio discovery and state: `list_roblox_studios`, `get_studio_state`.
- DataModel navigation: `search_game_tree`, `inspect_instance`.
- Script inspection and search: `script_read`, `script_search`, `script_grep`.
- Narrow script changes: `multi_edit`.
- Runtime and evidence: `start_stop_play`, `get_console_output`, `screen_capture`.
- Controlled input/navigation: `character_navigation`, `user_keyboard_input`, `user_mouse_input`.

Tool availability changes over time. Discover the actual tools and schemas from the connected server before planning work. Do not invent tool names or parameters.

## Connection preflight

1. Update Roblox Studio through its normal supported update process.
2. In Studio Assistant, open **Manage MCP Servers** and enable **Studio as MCP server**.
3. Prefer Studio's Quick Connect option for Codex when available.
4. Otherwise follow the official JSON configuration displayed by Studio. Roblox's documented Windows example is:

       {
         "mcpServers": {
           "Roblox_Studio": {
             "command": "cmd.exe",
             "args": ["/c", "%LOCALAPPDATA%\\Roblox\\mcp.bat"]
           }
         }
       }

5. Merge the Roblox_Studio entry into an existing config; do not overwrite unrelated server entries.
6. Restart/refresh the MCP client when instructed by Studio.
7. Confirm the green connected indicator in Studio and discover the connected Studio instances.

The V26 `doctor` command checks a provided JSON configuration's structure. It does not execute the configured command, modify client settings, inspect environment variables, or prove a client is connected.

## Mandatory task sequence

### 1. Identify the correct project and Studio instance

- Confirm the intended place/project, universe, and test environment.
- Discover connected Studio instances and select the intended `studio_id`; do not infer the target from list order.
- If more than one instance is open, verify the place identity before every write.
- If the place or identity is ambiguous, stop before editing.

### 2. Inspect before editing

- Inspect the relevant DataModel hierarchy and script contents.
- Search existing implementations before creating a new script.
- Read caller/callee scripts, RemoteEvent contracts, data schemas, and related tests before changing a shared boundary.
- Record exact target instance paths and why each needs a change.
- Avoid unrelated player data, personal data, secrets, and broad project dumps.

### 3. Plan the smallest safe change

- Define expected behaviour and acceptance checks.
- Separate read-only inspection, local edits, playtesting, local saving, and publishing into different actions.
- Keep edits scoped to approved files and instances.
- Preserve the current architecture unless a migration is explicitly part of the task.

### 4. Edit and review

- Use the current live MCP schema for each edit tool.
- Apply one bounded edit batch, then read changed scripts back.
- Inspect the diff/before-after content and run static checks.
- Do not claim a write succeeded until the tool confirms it.
- Do not overwrite concurrent human/agent changes silently.

### 5. Test and capture evidence

- Run the smallest relevant Studio test first, then broaden to multiplayer/device/network scenarios when justified.
- Capture console output and focused screenshots for meaningful visual/runtime changes.
- Record Studio instance, place, test mode, client count, device profile, network settings, and observed result.
- Distinguish static checks, unit tests, Studio playtests, and live production verification.

### 6. Save and release separately

- Saving the open place is persistent. Review the final diff and get explicit approval before invoking a save operation.
- Publishing is a separate production-impacting operation and always requires explicit user approval.
- Use an isolated test place and test DataStores. Never assume an open Studio session is safe for production data.
- A successful playtest does not prove publishing, live APIs, or production player state were tested.

## Multi-agent coordination

- Assign a single owner to each Studio instance and write scope.
- Parallel agents may research/review separate scripts but must not concurrently edit the same place or script.
- Give each workstream a concrete allowlist, acceptance tests, and evidence contract.
- Re-read shared contracts after integrating work from other agents.

## Sources

- [Roblox: Connect to the Roblox Studio MCP server](https://create.roblox.com/docs/studio/mcp)
- [Roblox: Studio testing modes](https://create.roblox.com/docs/studio/testing-modes)
