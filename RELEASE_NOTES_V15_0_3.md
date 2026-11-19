# V15.0.3 — Roblox Codex Game Studio Kit

**Release:** `v15.0.3`  
**Type:** package-cleanliness and compatibility patch  
**License:** MIT

V15.0.3 fixes issues found during a file-by-file audit of the published V15.0.2 ZIP and TAR.XZ archives.

## Fixes
- Removes Python interpreter caches (`__pycache__`, `.pyc`, and `.pyo`) from the assembled package.
- Prevents generated Python bytecode from being included in release archives and fails CI if any cache remains.
- Verifies both V14 and V15 checksum manifests after the final test suite.
- Corrects the repository README skill count to the measured total of 143 native Codex skills.
- Adds the mandatory current-source research gate to all eight V15 native Codex skills.
- Extends V15 validation to reject skills missing the research gate.
- Runs the full inherited `tools/tests` suite, including V12/V13 compatibility checks, against the assembled cumulative package.

## Verification
The V15 workflow validates V15 JSON/schema examples and native skill metadata, runs V15 regression tests and the full inherited Python test suite, removes temporary bytecode, runs the inherited V14 package doctor, verifies both checksum manifests, and compares extracted ZIP/TAR.XZ trees.

The V14 workflow separately compiles inherited Lua/Luau sources and builds the sample experience, Content Factory plugin, V14 Studio Test Runner plugin, and disposable Studio test fixture.

## Runtime limitations
CI does not launch Roblox Studio. Studio playtests, multiplayer runtime behavior, physical-device behavior, live DataStore behavior, asset permissions, and production safety still require their respective authorized environments and evidence.

## Installation
1. Download the ZIP or TAR.XZ asset attached to the `v15.0.3` GitHub Release.
2. Extract the archive and open the package root in Codex.
3. Read `AGENTS.md` and `INDEX_V15.md`.
4. Use `$roblox-game-builder` as the primary orchestrator and load only relevant specialists.
