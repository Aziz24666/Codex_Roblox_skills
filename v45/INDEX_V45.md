# Roblox Codex Game Studio Kit — V45

V45.0.0 adds **4 native Codex skills**, bringing the cumulative package to **284 native skills**. V44 remains the latest published release until V45 is reviewed and merged.

## V45 — Quest, Dialogue, and Narrative Systems

- Quest graph architecture, objective contracts, prerequisites, completion paths, and server-authoritative progression.
- Branching dialogue, stable choice IDs, ending reachability, localization keys, and server-validated outcomes.
- Quest/dialogue state integration with safe persistence, idempotent transitions, and content migration.
- Narrative QA, accessibility, localization readiness, and writer/engineer handoffs.

## Offline CLI

The V45 CLI validates quest/dialogue manifests. It detects duplicate IDs, unsupported fields, missing references, unreachable nodes, quest/prerequisite cycles, missing completion paths, duplicate localization keys, and dialogue nodes without a route to an ending.

## Limitations

V45 checks declared metadata only. It does not inspect Luau, run Studio, access Roblox services, inspect profiles, execute migrations, validate translations, or prove server authorization. Keep progression server-owned and require real Studio/device testing and human review.

All V1–V44 capabilities remain included.
