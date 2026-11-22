---
name: roblox-studio-mcp-workflow
description: Plan and carry out scoped Roblox Studio work through the connected local Studio MCP server, with instance identity checks, read-before-write inspection, and evidence-based completion.
---

# Roblox Studio MCP Workflow

Use this skill when a task requires inspecting or modifying an open Roblox Studio place through Studio MCP.

## Preconditions

1. Confirm the actual game project root and intended place/test environment.
2. Confirm Roblox Studio is open and its built-in MCP server is enabled.
3. Discover connected Studio instances. Select the intended `studio_id`; do not infer the target from list order.
4. Discover the live tool list and schemas. Availability varies by Studio version; never assume a tool exists because a guide mentions it.
5. Confirm the target is isolated from production DataStores and player state.

If Studio MCP is unavailable, explain the missing precondition and continue with offline source review/tests only. Do not pretend connected Studio tools are available.

## Read-only first

- Check Studio state and inspect the DataModel hierarchy around the target.
- Search existing scripts before creating new instances.
- Read the target script and its directly related dependencies and event contracts.
- Record a narrow allowlist of scripts/instances in scope.
- Avoid unrelated player data, personal data, secrets, and broad project dumps.

Useful tool groups, only when present in the live server:

- Studio discovery: `list_roblox_studios`, `get_studio_state`.
- DataModel inspection: `search_game_tree`, `inspect_instance`.
- Script reading/search: `script_read`, `script_search`, `script_grep`.
- Local code edit: `multi_edit`.
- Playtest/evidence: `start_stop_play`, `get_console_output`, `screen_capture`.

## Edit loop

1. State expected behaviour and acceptance criteria.
2. Read relevant current code and identify the smallest safe change.
3. Apply one bounded edit batch to approved paths only.
4. Read changed code back and inspect the actual diff.
5. Run static/unit validation before launching a Studio test.
6. If the result is ambiguous, stop and report what remains unverified.

Do not create duplicate scripts when an existing service/module should be extended. Do not overwrite concurrent human/agent edits. Never mark a task complete solely because a tool returned a success-shaped response.

## Testing and persistence

- Start with one-client smoke testing, then expand to multi-client/device/network scenarios when relevant.
- Capture console output and focused screenshots for relevant defects or UI changes.
- Record selected Studio instance, place, test mode, scenario, and evidence.
- Request explicit approval before saving the open place or taking production-impacting action.
- Publishing, production DataStore writes, and player-impacting Open Cloud calls are separate approval-gated operations.

## Security

- Connect only trusted MCP clients. Studio MCP runs locally and can read/modify the open place.
- Do not request broad Open Cloud scopes as a shortcut.
- Do not expose credentials, private player data, or secrets in prompts or logs.
- Keep inherited no-gambling and fair-monetization rules in force.
- If the connected instance, target place, or permission scope is uncertain, stop before writing.
