# Roblox Codex Game Studio Kit

[![V14 CI](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml)
[![V15 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v15-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v15-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A research-first, cumulative Roblox game-development toolkit for Codex. **The current release is V15.0.1**, which includes the complete V1–V14 package plus eight native Codex skills and a project-aware implementation/verification layer.

## Get the package

**[Download V15.0.1 ZIP and TAR.XZ from GitHub Releases](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v15.0.1)**

V15 is cumulative. You do not need to download earlier versions separately.

## What's included

- **144 native Codex skills**: 136 existing specialist skills plus eight V15 skills installed under .agents/skills/.
- **Project intelligence**: inspect the existing project's source of truth, entry points, architecture, dependencies, and toolchain before editing.
- **Skill orchestration**: select the smallest relevant set of specialists instead of loading the entire library.
- **Acceptance-driven implementation**: deliver complete vertical slices with observable acceptance criteria and explicit failure paths.
- **Security and persistence review**: validate server-side trust boundaries, schema migrations, retry behavior, and test isolation.
- **Performance and runtime evidence**: compare measured baselines and clearly separate build checks from Studio/device/service evidence.
- **V14 Studio testing toolkit**: Studio Test Runner plugin, disposable multi-client fixture, JSON scenarios/reports, and supporting tooling.
- Reusable Luau patterns, data-driven gameplay systems, Studio Content Factory tooling, templates, examples, schemas, and automated quality workflows.

## Quick start with Codex

1. Download and extract the V15.0.1 package.
2. Open the extracted package root in Codex.
3. Read AGENTS.md and INDEX_V15.md.
4. Use $roblox-game-builder as the main orchestrator.
5. Before substantial changes to an existing game, use $roblox-project-intelligence to map the project and source of truth.
6. Load only the specialist skills relevant to the task.

## V15 validation

From the extracted package root:

    python v15/tools/v15_validate.py --root v15
    python -m unittest discover -s v15/tests -v
    sha256sum --check V15_SHA256SUMS.txt

## What CI proves — and what it does not

The V15 workflow checks JSON contracts, Codex skill metadata, Python regression tests, Python compilation, cumulative package reconstruction, archive creation, inventory, and SHA-256 integrity.

The separate V14 workflow compiles inherited Lua/Luau sources and builds the sample experience, Content Factory plugin, V14 Test Runner plugin, and disposable fixture. **CI does not launch Roblox Studio.** Studio playtests, multiplayer runtime checks, physical-device testing, live DataStore behavior, asset permissions, and production operations require their own environments and evidence.

## Repository documentation

- [V15 index](v15/INDEX_V15.md)
- [V15 layer overview](v15/README.md)
- [V15 implementation pipeline](v15/docs/IMPLEMENTATION_PIPELINE.md)
- [V15 quality gates](v15/docs/QUALITY_GATES.md)
- [V15 corrective release notes](RELEASE_NOTES_V15_0_1.md)
- [V14 index](INDEX_V14.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
