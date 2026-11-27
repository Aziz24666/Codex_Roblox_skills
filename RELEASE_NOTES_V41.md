# V41.0.0 — Matchmaking, Parties and Multiplayer Orchestration

## Added
- Four native Codex skills for skill-based matchmaking queues, party/lobby lifecycle, cross-server coordination, and teleport/reconnect/server handoff.
- Offline matchmaking contract validator, design auditor, and deterministic synthetic-ticket simulator.
- Strict JSON allowlists, duplicate-key and non-standard constant rejection, bounded input, safe project-relative paths, symlink rejection, and atomic reports.
- Explicit MemoryStore ephemeral-state boundaries, party-ticket atomicity, lease/version/fencing requirements, best-effort messaging, TeleportAsync reserved-server routing, safe TeleportData, and recovery policies.
- JSON Schema, example model, 41 unit tests, docs, cumulative package patcher/auditor, and V41 quality workflow.

## Cumulative package
V1–V41, 268 native Codex skills. Download only the V41 package.

## Limitations
The V41 CLI validates supplied JSON contracts and simulates supplied synthetic ticket metadata only. It does not connect to Roblox APIs, read real queues, run Studio, make reserved servers, teleport players, inspect Luau, or prove real concurrency/fairness. Perform multi-server testing and published-test-experience verification with human review before production use.
