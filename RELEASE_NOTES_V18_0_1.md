# V18.0.1 — Package Audit and Setup Maintenance

**Release:** `v18.0.1`  
**Type:** patch release; cumulative V1–V18 package retained  
**License:** MIT

V18.0.1 corrects maintenance issues discovered during an independent audit of the V18.0.0 release archives. It does not remove or replace V18.0.0.

## Fixes

- Corrects the inherited V17 cumulative audit migration to expect the correct 175 installed skills.
- Preserves the historical V17 source checks while comparing the four intentionally upgraded economy specialists against their V18 overlay sources.
- Runs the inherited V17 cumulative audit as part of V18 cumulative verification, after active SHA-256 manifests are regenerated.
- Documents the pinned Python 3.13 dependency installation command for the packaged CLI.
- Lazily imports optional validation libraries so basic read-only project inspection and routing work without installing them.
- Adds regression tests for the inherited audit migration and dependency-light routing.
- Replaces the unfinished remote-request validation teaching example with a bounded server-authoritative example demonstrating type/tag/world/distance checks, cooldowns, rate limiting, request-ID replay protection, fixed server-side rewards, and player cleanup. The example clearly marks its in-memory currency as non-persistent demonstration state.
- Documents that paid access and private servers cannot be enabled together for the same experience, with links to current official Roblox Creator Hub guidance.

## Verification

The release workflow reconstructs the package from the pinned V17 baseline, applies V18.0.1, runs versioned validators and regression tests, runs the inherited V17 audit plus V13/V14 package doctors, regenerates current manifests, performs the cumulative V18 audit, and compares the ZIP and TAR.XZ extraction trees.

Roblox Studio playtests, multiplayer runtime behavior, DataStore persistence, live purchase fulfillment, device testing, and production operations remain separate environment-specific checks and are not claimed as completed by package CI.
