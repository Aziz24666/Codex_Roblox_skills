# Codex Roblox Skills

[![CI](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A research-first, modular Roblox game-development toolkit for Codex. The cumulative V13 release includes specialist skills, reusable Luau patterns, data-driven NPC and gameplay architecture, schema-driven Roblox Studio editors, prefab factories, project templates, testing utilities, and GitHub Actions quality gates.

## Download the complete toolkit

**Download the complete V13 source archive:** [roblox-codex-game-studio-kit-v13.tar.xz](dist/roblox-codex-game-studio-kit-v13.tar.xz)

The archive contains all specialist skills, instructions, documentation, prompts, templates, schemas, examples, Studio plugin source, sample Rojo project, and validation tools. Extract it and open the extracted `roblox-codex-game-studio-kit-v13/` directory in Codex.

You do not need older V1–V12 downloads. V13 is cumulative.

## Quick start

1. Download and extract the V13 source archive.
2. Open the extracted folder in Codex.
3. Read `AGENTS.md` and `INDEX_V13.md`.
4. For an existing Roblox game, ask Codex to audit the current source of truth before copying or merging the sample project.
5. Ask Codex to use `$roblox-game-builder` as the primary orchestrator.

Suggested first instruction:

```text
Read AGENTS.md and INDEX_V13.md. Use $roblox-game-builder as the primary orchestrator.
Audit this project and identify its source of truth before changing files. Research current official Roblox documentation before substantive API or tooling decisions. Create a prioritized roadmap, then implement one complete playable vertical slice at a time. Prefer reusable data-driven systems and clean, strictly typed Luau. Run available tests and builds, report actual evidence, and clearly identify Studio/runtime checks that were not available. Do not publish or modify live production data without explicit authorization.
```

## Highlights

- **126 specialist skills** with progressive disclosure and task-specific routing.
- **Research-first engineering:** check current official Roblox documentation and compare reputable approaches before substantive technical implementation.
- **Modular/data-driven architecture:** reusable NPCs, components, behaviors, inventories, progression, UI, and gameplay systems.
- **Schema-generated Studio editors:** dynamic fields, validation, preview, and prefab generation.
- **Engineering utilities:** Python audits, JSON Schemas, Luau examples, dependency checks, evidence reports, and release gates.
- **CI:** Python quality checks, Luau source compilation, and Rojo builds for the sample experience and Studio plugin.

## Repository contents

The repository stores the complete V13 source in the versioned archive under `dist/`. The archive is the canonical source bundle for this release. The root contains repository-level documentation and CI configuration.

## GitHub Actions

On pushes to `main`, pull requests, and manual dispatch, CI:

1. Extracts the full V13 source archive.
2. Runs package preflight, skill metadata validation, schema checks, workflow audits, and the Python regression suite.
3. Downloads the pinned official Luau CLI and verifies its SHA-256 checksum.
4. Compiles the Lua/Luau source files.
5. Downloads the pinned Rojo CLI and verifies its SHA-256 checksum.
6. Builds the sample Roblox experience and Content Factory Studio plugin.
7. Uploads the `.rbxlx` and `.rbxmx` artifacts.

The workflow uses least-privilege read-only repository permissions and does not publish to Roblox.

## What CI does not prove

A green CI run does not replace Roblox Studio playtests, multiplayer testing, physical-device validation, asset permission checks, published-experience analytics validation, or production deployment checks. Those require their appropriate environments and explicit evidence.

## Documentation

- [MIT License](LICENSE)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Repository metadata and topics](GITHUB_REPOSITORY_METADATA.md)

## License and affiliation

Released under the [MIT License](LICENSE). Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This is an independent community toolkit and is not affiliated with or endorsed by Roblox Corporation or OpenAI.
