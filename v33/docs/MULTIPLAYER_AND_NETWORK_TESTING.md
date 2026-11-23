# Multiplayer and Network Regression Testing

## Test the client-server model

Build the test matrix around the server's authority and the client's view. Use Server & Clients for multi-client behavior and run the same scenario under baseline and selected impaired-network profiles.

## Required scenarios

- Fresh join and initial replication.
- Late join while a round is active.
- Leave during a match, transition, trade, or save.
- Rejoin and respawn.
- Simultaneous valid requests from separate clients.
- Invalid, duplicate, stale, or out-of-order remote requests.
- Server-authoritative inventory, progression, rewards, and match state.
- Cleanup of reservations, locks, temporary objects, and active-session state.
- Retry and timeout behavior without duplicate effects.
- Network latency, jitter, and packet loss where relevant.

## Studio facilities

The Studio UI offers Server & Clients simulation with up to eight clients. StudioTestService provides programmatic multiplayer test orchestration from a plugin, also up to eight clients, with documented role and lifecycle constraints. The Network Simulator can add latency, jitter, and packet loss to reproduce difficult connection conditions.

Record the exact number of clients and network profile. A source-level check of RemoteEvent code is not a multiplayer simulation.

## Defect invariants

- Clients never set protected game state directly.
- Invalid remote requests do not mutate state.
- Duplicate requests do not duplicate rewards or trades.
- Every state transition has a clear server-side owner.
- A disconnected player does not leave the session stuck.
- Clients that join late receive the correct current state.
- A degraded connection does not create inconsistent UI promises or duplicate actions.

## Verification evidence

Use a stable suite ID, unique test IDs, opaque run/evidence references, timezone-aware timestamps, and fixed outcomes. The V33 report schema intentionally rejects free-form data fields. Store sensitive raw debugging evidence only in project-approved systems with appropriate access controls.
