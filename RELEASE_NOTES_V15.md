# V15 — Roblox Codex Game Studio Kit

**Release:** `v15.0.0`  
**License:** MIT

V15 is a cumulative V14 package with an additive project-aware development and verification overlay.

## Highlights
- Project intelligence and architecture discovery workflow.
- Skill selection and orchestration guidance.
- Acceptance-driven implementation pipeline.
- Defensive remote-security review guidance.
- Persistence and migration testing guidance.
- Performance regression testing guidance.
- Runtime evidence and failure triage contract.
- Reproducible release engineering guidance.
- Project manifest, task evaluation, and runtime evidence JSON schemas.
- Benchmark task examples, validator, regression tests, and dedicated CI workflow.

## Validation
The V15 workflow validates the manifest and benchmark contracts, validates example evidence, runs Python regression tests, compiles the Python validator, and checks all V15 JSON files. It also reconstructs the cumulative V14 source, applies the V15 overlay, and creates full ZIP and TAR.XZ archives.

## Important limitations
V15's Python tests and packaging workflow do not execute Roblox Studio. They do not prove runtime behavior, multiplayer correctness, physical-device behavior, live DataStore behavior, asset permissions, or production safety. Those require their respective authorized Roblox environments and evidence.

## Installation
1. Download the ZIP or TAR.XZ asset.
2. Extract the archive.
3. Open the package root in Codex.
4. Read `AGENTS.md`, `INDEX_V14.md`, and `v15/README.md`.
5. Follow `v15/docs/IMPLEMENTATION_PIPELINE.md` and load the relevant V15 workflow specifications.

V15 is cumulative; separate V1–V14 downloads are not required.
