# V41 CLI reference

The V41 CLI runs offline. It validates a matchmaking model, audits design warnings, and simulates one deterministic match using only the synthetic tickets supplied in a JSON file.

## Commands

Run from the V41 package root:

```powershell
python .\v41\tools\v41.py doctor --root C:\Path\To\YourGame
python .\v41\tools\v41.py validate --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json
python .\v41\tools\v41.py audit --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json --output .codex\reports\matchmaking-audit.json
python .\v41\tools\v41.py simulate --root C:\Path\To\YourGame --model .codex\matchmaking\matchmaking-model.json --output .codex\reports\matchmaking-simulation.json
```

`doctor` checks the chosen project root and reports the CLI version. `validate` enforces strict model structure and conservative design invariants. `audit` writes design warnings and explicit capability limits. `simulate` sorts the provided synthetic tickets, selects complete party tickets without splitting them, calculates the skill window for the anchor ticket, and writes one deterministic match result.

## Model layout

The model contains `queue`, `matching`, `party`, `coordination`, `teleport`, `recovery`, and `simulation_tickets` sections. The full allowed fields and types are in `schemas/matchmaking-model.schema.json`; start with `examples/matchmaking-model.example.json`.

The validator checks (among other rules):
- MemoryStore is an ephemeral queue/state layer, not durable player storage.
- Queue operations are protected and queue entries are removed only after the assignment is confirmed.
- Match/player bounds and party-size constraints are consistent; parties are indivisible tickets.
- Cross-server records use leases, versions, fencing tokens, and server identity.
- MessagingService is best effort and not authoritative.
- Teleports use server-side `TeleportAsync`, reserved-server ID routing, a 50-player maximum, failure handling, and non-sensitive TeleportData references.
- Recovery is idempotent and client state is not authoritative.

## Exit codes

- `0`: command completed and the model passed structural validation.
- `1`: model validation failed.
- `2`: a path, input, or runtime error prevented processing.

## Path and input safeguards

Input files and reports must be project-relative. Absolute paths, parent traversal, backslashes, symlink traversal, duplicate JSON keys, non-standard JSON constants such as NaN, and JSON inputs larger than 1 MiB are rejected. Reports are written atomically.

## Simulation limits

The simulator is a deterministic single-match planning aid. It does not contact Roblox, dequeue actual MemoryStore items, model concurrent workers, capture latency, generate reserved servers, teleport players, or model retention/wait-time distributions. It uses a small synthetic ticket sample and a greedy anchor-based skill-window policy; it is not a production matchmaker implementation and not a prediction of real queue outcomes.

A passing validation/audit is not permission to alter production queues or teleport live players. Implement the server runtime separately, run multi-server and published-test-experience verification, and require human review for production rollout.
