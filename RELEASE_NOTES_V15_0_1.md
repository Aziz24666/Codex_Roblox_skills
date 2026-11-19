# V15.0.1 — Roblox Codex Game Studio Kit

**Release:** v15.0.1  
**Type:** corrective patch release  
**License:** MIT

V15.0.1 corrects discoverability and package metadata found during a post-release audit of V15.0.0. It retains the cumulative V1–V14 package and V15 development-system layer.

## Fixes and improvements
- Converts the eight V15 workflow specifications into native Codex skills with individual SKILL.md entry points and YAML name/description metadata.
- Copies the skills into the cumulative package's .agents/skills/ directory so Codex can discover them.
- Adds INDEX_V15.md and updates package-level AGENTS.md and README.md routing to V15.
- Synchronizes the V15 version marker and release metadata to 15.0.1.
- Adds a task-evaluation example and strengthens validation for malformed records, conflicting task results, required schema contracts, and native skill metadata.
- Regenerates the package inventory and creates a verified V15_SHA256SUMS.txt file manifest.
- Restricts the release job to marked pushes on main and derives the release tag from v15/VERSION.

## CI validation
The V15 Actions workflow validates JSON contracts and all eight native skill entry points, runs the V15 Python regression suite, compiles Python, reconstructs the cumulative V14 package, integrates the V15 overlay, verifies per-file checksums, and packages ZIP/TAR.XZ archives.

The V14 Actions workflow separately compiles all inherited Lua/Luau sources and builds the sample experience, Content Factory plugin, V14 Studio Test Runner plugin, and disposable test fixture.

## Important limitations
Neither workflow launches Roblox Studio. These results do not prove Studio runtime behavior, multiplayer correctness, physical-device behavior, live DataStore behavior, asset permissions, or production safety. Those checks require their own authorized environments and evidence.

## Installation
1. Download the ZIP or TAR.XZ asset attached to the v15.0.1 GitHub Release.
2. Extract the archive and open the package root in Codex.
3. Read AGENTS.md and INDEX_V15.md.
4. Use $roblox-game-builder as the primary orchestrator and load only relevant specialists.
