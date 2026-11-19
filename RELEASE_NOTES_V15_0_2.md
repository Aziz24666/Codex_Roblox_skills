# V15.0.2 — Roblox Codex Game Studio Kit

**Release:** v15.0.2  
**Type:** corrective patch release  
**License:** MIT

V15.0.2 is a follow-up compatibility correction after running the inherited V14 package doctor against the complete V15.0.1 archive.

## Fixes and improvements
- Shortens four V15 skill descriptions to comply with the inherited 160-character Codex skill metadata limit.
- Makes the V15 validator enforce that same description limit so future skills cannot silently regress.
- Regenerates both the inherited V14 and new V15 file checksum manifests using a non-circular arrangement; verifies every manifest entry.
- Runs the inherited V14 package doctor against the final cumulative V15 package as a release gate.
- Runs the V15 validator and regression tests against the assembled package, not only the source overlay.
- Corrects the public skill total to the measured package inventory: 143 native SKILL.md files.

## CI validation
The V15 workflow checks JSON contracts and native skill metadata, runs regression tests, compiles Python, assembles the cumulative package, runs the inherited V14 package doctor, verifies both checksum manifests, and compares ZIP/TAR.XZ extracted contents.

The V14 workflow separately compiles inherited Lua/Luau sources and builds the sample experience, Content Factory plugin, V14 Studio Test Runner plugin, and disposable test fixture.

## Important limitations
Neither workflow launches Roblox Studio. These results do not prove Studio runtime behavior, multiplayer correctness, physical-device behavior, live DataStore behavior, asset permissions, or production safety. Those checks require separate authorized environments and evidence.

## Installation
1. Download the ZIP or TAR.XZ asset attached to the v15.0.2 GitHub Release.
2. Extract the archive and open the package root in Codex.
3. Read AGENTS.md and INDEX_V15.md.
4. Use $roblox-game-builder as the primary orchestrator and load only relevant specialists.
