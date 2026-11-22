---
name: roblox-remote-contract-and-rojo-validation-v27
description: Review Roblox RemoteEvent and RemoteFunction contracts, server-side validation boundaries, and Rojo project mapping integrity.
---

# Roblox Remote Contract and Rojo Validation

Use this skill when changing client/server remotes, shared payloads, DataModel mappings, or Rojo configuration.

## Remote contract inventory

- Identify each remote's owner, direction, caller, handler, and payload type.
- Read both client call sites and server handlers.
- Define payload shapes in shared Luau types where practical.
- Validate all client input as untrusted data on the server.
- Derive player identity from the server connection rather than client-supplied identity.
- Validate ownership, authorization, ranges, lengths, current game state, duplicate requests, and request rate.
- Keep server-owned progression, inventory, combat state, purchases, and rewards authoritative.
- Define response, acknowledgement, timeout, and failure semantics.

V27's static remote inventory only matches variable assignments from constant `WaitForChild`/`FindFirstChild` names. Treat unpaired calls as manual review candidates, not proof that a handler is absent or a vulnerability exists.

## Rojo validation

- Identify the exact project file.
- Validate the project JSON and each `$path` mapping.
- Review place IDs and allowed place IDs before live sync.
- Use an isolated test place.
- Run a local Rojo build before syncing.
- Inspect the generated model and Studio DataModel.

## Safety boundaries

- Do not use untrusted client input to make authoritative server decisions.
- Do not create automatic remote fuzzing, exploit invocation, or player-targeting workflows.
- Do not auto-edit remote definitions or project mappings.
- Saving, live-syncing to a persistent place, and publishing remain separate human-reviewed actions.

## Evidence

Record the actual target project file, validation output, analyzer results, test mode, client count, logs, screenshots, and anything not tested.
