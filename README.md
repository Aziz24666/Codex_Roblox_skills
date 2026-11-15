# Codex Roblox Skills

[![CI](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A research-first, modular Roblox game-development toolkit for Codex. The cumulative V13 package provides specialist skills, reusable Luau patterns, data-driven NPC/gameplay architecture, schema-driven Studio editors, prefab factories, project templates, testing utilities, and CI quality gates.

## Complete V13 toolkit

The full toolkit archive is available as a release asset when published. The repository's CI expects the source tree at the repository root; see the linked V13 package documentation for the complete skills, docs, prompts, templates, schemas, examples, and tools.

## Quick start

1. Clone this repository and open its root in Codex.
2. Read `AGENTS.md` and `INDEX_V13.md`.
3. Audit an existing game's source of truth before merging the sample project.
4. Select only the specialist skills and reference documents relevant to the task.
5. Research current official Roblox documentation before substantive API/tooling decisions.

Suggested first instruction:

```text
Read AGENTS.md and INDEX_V13.md. Use $roblox-game-builder as the primary orchestrator. Audit this project and identify its source of truth before changing files. Research current official Roblox documentation before substantive API or tooling decisions. Create a prioritized roadmap, then implement one complete playable vertical slice at a time. Prefer reusable data-driven systems and clean, strictly typed Luau. Run available tests and builds, report actual evidence, and clearly identify Studio/runtime checks that were not available. Do not publish or modify live production data without explicit authorization.
```

## Core capabilities

- Research-first Roblox API and architecture decisions.
- Modular, data-driven NPCs, companions, weapons, gadgets, and gameplay systems.
- Schema-generated Roblox Studio content editors and prefab factories.
- Luau engineering, lifecycle management, streaming readiness, profiling, and analytics governance.
- Python validators, JSON Schemas, dependency audits, test matrices, and release gates.
- CI workflows for Python validation, Luau compilation, and Rojo builds.

## Continuous integration

The GitHub Actions workflow runs on pushes to `main`, pull requests, and manual dispatch. It is designed to run Python package checks, Luau compilation, and Rojo builds with pinned tool versions and verified checksums. CI does not publish to Roblox.

A green CI run does not replace Roblox Studio playtests, multiplayer tests, device tests, asset permission checks, or production verification.

## License

MIT. See [LICENSE](LICENSE). This is an independent community toolkit and is not affiliated with or endorsed by Roblox Corporation or OpenAI.
