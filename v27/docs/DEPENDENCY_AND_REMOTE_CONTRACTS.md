# V27 Dependency and Remote Contract Governance

## Dependency graph

V27 resolves only simple, constant module references such as:

    require(script.Parent.Modules.InventoryService)

and:

    require(script.Parent:WaitForChild("Modules"):WaitForChild("InventoryService"))

It reports resolved edges, unresolved static references, dependency cycles, and possible unreferenced modules.

The graph is based on filesystem hierarchy. Rojo can map directories to different Roblox services or logical Instance paths, so the graph is an approximation when the filesystem tree does not match the Instance tree. Dynamic module registries, string-built names, asset IDs, aliases and custom loaders are not resolved. The report lists those limits instead of guessing.

### Review cycle findings

A cycle is a strongly connected group of source files where each file can reach another through the detected static require edges. Cycles can make initialization order difficult to reason about. Review whether the modules should depend on a smaller shared interface or whether responsibilities belong in a lower-level module. Do not automatically split, move, or rewrite a module based only on the report.

### Review unreferenced module candidates

The report labels unreferenced files as *possible* module candidates. They may still be used by runtime entrypoints, plugin code, reflection, generated names, Rojo mappings, or a dynamic registry. Check the actual DataModel and runtime paths before changing or removing them.

## Remote contracts

Roblox remotes are asynchronous client/server communication boundaries. Review every boundary in the context of the actual server implementation.

For each remote, document:

- Stable name and owning service/system.
- Direction and intended caller.
- Payload fields and Luau type definitions.
- Server-side validation of types, ranges, lengths, ownership, permissions, and current game state.
- Rate/volume limits and duplicate-request behavior.
- Expected response/acknowledgement semantics and failure handling.
- Whether the server derives player identity from the connection instead of trusting client-provided identity.

V27 inventories `FireServer`, `InvokeServer`, `OnServerEvent`, `OnServerInvoke`, `FireClient`, `FireAllClients`, `InvokeClient`, and `OnClientEvent`. It correlates names only when a local variable is assigned from a constant `WaitForChild`/`FindFirstChild` string. This is intentionally conservative: aliases and wrappers can hide valid implementations.

A potentially unpaired client call is a manual review item. It is not proof of an exploitable issue, and V27 does not generate exploit payloads or attempt to invoke game remotes.

## Safe review sequence

1. Identify the real project and place.
2. Read the remote declaration, client caller, server handler, related types and service code.
3. Confirm all state-changing decisions happen on the server.
4. Validate client inputs as untrusted data and use server-known player identity.
5. Add focused tests for valid, invalid, repeated, stale, and unauthorized requests.
6. Capture server/client logs and Studio test evidence.
7. Review the exact diff before saving or publishing.

## No automatic rewrites

V27 is report-only. It does not delete modules, rename scripts, rewrite remote payloads, auto-add `--!strict`, or modify project mappings. Those changes require explicit design and review.
