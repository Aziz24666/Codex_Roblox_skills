# Roblox Codex Game Studio Kit — V41

V41.0.0 is the cumulative V1–V41 package with **268 native Codex skills**. Download only the current release.

## V41 — Matchmaking, Parties and Multiplayer Orchestration

Four new native Codex skills:

1. **Skill-based matchmaking queue design** — MemoryStore queue contracts, server-derived skill matching, expanding rating windows, fairness, ticket idempotency, and queue failure recovery.
2. **Party and lobby lifecycle** — server-owned membership/invitations, leader transfer, party versioning, lobby state, and all-or-none party queueing.
3. **Cross-server matchmaking coordination** — ephemeral MemoryStore assignment records, lease ownership, fencing tokens, reconciliation, and best-effort MessagingService notifications.
4. **Teleport, reconnect and server handoff** — server-side TeleportAsync routing, reserved server IDs, safe TeleportData references, partial-party recovery, and reconnect policy.

## V41 tool

`v41/tools/v41.py` provides:

- `doctor`: confirm the tool and selected project root.
- `validate`: validate matchmaking, party, coordination, teleport, recovery, and synthetic ticket contracts.
- `audit`: produce design warnings and explicit capability boundaries.
- `simulate`: deterministically model one match using the synthetic tickets in the model, without splitting parties.

See `v41/docs/V41_CLI.md` for commands and constraints.

## Design reference

- `v41/docs/MATCHMAKING_ARCHITECTURE.md`
- `v41/docs/PARTIES_AND_LOBBY_LIFECYCLE.md`
- `v41/docs/TELEPORT_AND_RECOVERY.md`

## Important boundaries

V41's local CLI is offline. It does not call MemoryStoreService, DataStoreService, MessagingService, or TeleportService; it does not launch Roblox Studio, create reserved servers, teleport players, or verify production concurrency. Simulation results use synthetic ticket metadata and are not predictions of player wait time or queue outcomes. Validate runtime behavior with multi-server tests and a published test experience before production rollout.

All V1–V40 capabilities and safeguards remain included.
