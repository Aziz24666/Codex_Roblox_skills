# V15.0.3 — Roblox Codex Game Studio Kit

**Release:** `v15.0.3`  
**Type:** package-cleanliness and integrity patch  
**License:** MIT

V15.0.3 fixes a packaging defect found during a file-by-file audit of the published V15.0.2 ZIP and TAR.XZ archives.

## Fixes
- Removes Python interpreter caches (`__pycache__`, `.pyc`, and `.pyo`) from the assembled package before inventory and checksum generation.
- Prevents Python unit tests in the package job from writing bytecode into the release tree.
- Adds a regression test proving the package patcher removes stale Python caches.
- Adds a hard CI failure if any cache/bytecode reappears before or after archive creation.
- Verifies both V14 and V15 checksum manifests after the package tests.
- Corrects the repository README skill count to the measured total of 143 native Codex skills.

## Verification
The V15 workflow validates V15 JSON/schema examples and all eight V15 skill definitions, runs the regression suite, compiles Python, runs the inherited V14 package doctor, verifies both checksum manifests, and compares the extracted ZIP and TAR.XZ trees. It also rejects accidental Python cache files in the package.

The separate V14 workflow compiles inherited Lua/Luau sources and builds the sample experience, Content Factory plugin, V14 Studio Test Runner plugin, and disposable Studio test fixture.

## Runtime limitations
CI does not launch Roblox Studio. No claim is made that Studio playtests, multiplayer runtime behavior, physical-device behavior, live DataStore behavior, asset permissions, or production safety were tested. Those checks require their respective authorized environments and evidence.

## Installation
1. Download the ZIP or TAR.XZ asset attached to the `v15.0.3` GitHub Release.
2. Extract the archive and open the package root in Codex.
3. Read `AGENTS.md` and `INDEX_V15.md`.
4. Use `$roblox-game-builder` as the primary orchestrator and load only relevant specialists.
