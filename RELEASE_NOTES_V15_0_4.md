# V15.0.4 — Roblox Codex Game Studio Kit

**Release:** `v15.0.4`  
**Type:** cumulative package audit and correctness patch  
**License:** MIT

V15.0.4 fixes defects identified by a full file-level audit of the published V15.0.3 archives and adds a repeatable audit to CI.

## Fixes

- Quotes the three installed V14 skill descriptions that had invalid YAML frontmatter.
- Adds a CI audit that parses all 143 installed Codex skill frontmatters, checks unique names and folder agreement, validates description length, and compares all eight V15 source skills with their installed copies.
- Regenerates the unversioned root `SHA256SUMS.txt` as a complete current-package manifest.
- Defines a non-circular checksum policy: the root manifest covers package content except the three current manifests; V15 excludes itself and V14 but includes the root manifest; V14 excludes only itself and therefore includes the root and V15 manifests.
- Documents V6–V13 manifests as historical snapshots, not current integrity manifests.
- Adds a V9 editor-field collection schema referencing the existing single-field schema and validates the existing collection example against it.
- Adds cumulative-package checks for JSON, JSON Schema, YAML, Python, TOML, CSV, Markdown local paths, zero-byte files, generated caches, and all current checksums.

## Verification

CI runs the V15 validator and unit tests, the full inherited V12–V14 tools test suite, the inherited package doctor, and the new cumulative package audit. The package audit runs after the last cache cleanup and checksum generation. ZIP and TAR.XZ archives are then integrity-tested, extracted, and compared.

The separate V14 workflow compiles inherited Luau sources and builds the sample experience, Content Factory plugin, V14 Studio Test Runner plugin, and disposable Studio test fixture.

## Runtime limitations

CI does not launch Roblox Studio. Studio playtests, multiplayer runtime behavior, physical-device behavior, live DataStore behavior, asset permissions, and production safety require execution in their respective authorized environments.

## Installation

1. Download the ZIP or TAR.XZ asset attached to the `v15.0.4` GitHub Release.
2. Extract the archive and open the package root in Codex.
3. Read `AGENTS.md` and `INDEX_V15.md`.
4. Use `$roblox-game-builder` as the primary orchestrator and load only relevant specialists.
