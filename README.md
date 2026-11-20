# Roblox Codex Game Studio Kit

[![V18 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v18-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v18-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V18.0.0 — Connected Automation and Cross-Skill Orchestration.** This is the complete cumulative V1–V18 Roblox game-development toolkit for Codex. You only need the current V18 release; earlier versions do not need separate downloads.

## Download

The complete package will be attached to the [V18.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v18.0.0) as ZIP and TAR.XZ archives, with SHA-256 checksums.

## What's included

- **175 native Codex skills** spanning Roblox architecture, Luau, gameplay systems, characters and avatars, UI/input/accessibility, multiplayer/networking, security, persistence, economy, procedural content, NPCs, Studio plugins/MCP, performance, testing, research, and release engineering.
- **12 V18 orchestration skills** for task intake, end-to-end coordination, project reconnaissance, impact-aware routing, shared contracts, dependency planning, bounded autonomous implementation, delegation, continuous validation/repair, approval gates, context handoff, and evidence-first completion.
- A shared handoff contract connecting the specialist skill library through one task lifecycle.
- A generated machine-readable registry connecting skills by domain and related capability.
- A local Python CLI for project inspection, task routing, work-item scaffolding, dependency validation, and package verification.
- Versioned work-item, project-profile, skill-registry, and workflow-evidence schemas with examples.
- Reusable Luau patterns, Studio tooling, templates, sample projects, quality gates, and historical migration guides from V1–V17.

## Quick start with Codex

1. Download and extract the complete V18 ZIP.
2. Open the extracted package root in Codex.
3. Read `AGENTS.md` and `INDEX_V18.md`.
4. Start substantial work with `$roblox-end-to-end-development-orchestrator`.
5. Let the orchestrator inspect the project, define acceptance criteria, select relevant specialists, coordinate implementation, and require evidence for completion.
6. For command-line assistance, run `python v18/tools/v18.py --help` from the extracted package root.

## V18 automation commands

```bash
python v18/tools/v18.py doctor --root .
python v18/tools/v18.py route --root . --task "Build an R15 character customization system"
python v18/tools/v18.py plan --root . --task "Build an R15 character customization system" --write
python v18/tools/v18.py verify --root .
```

The CLI provides deterministic local planning and validation. It does not itself grant Codex subagents, MCP connections, Roblox Studio access, permissions, or production credentials; those depend on the actual environment and connected tools.

## Validation and evidence boundaries

GitHub Actions reconstructs the cumulative package from the pinned V17 baseline, applies V18, runs source and cumulative validators, regression tests, inherited package checks, full-package audits, checksum verification, and ZIP/TAR.XZ extraction comparisons. Only a validated package is attached to the release.

CI does **not** launch Roblox Studio. Studio playtests, multiplayer runtime checks, physical-device testing, live DataStore behavior, asset permissions, live purchase fulfillment, and production operations must be executed in their real authorized environments and recorded separately. Unexecuted checks must remain `NOT_RUN` or `BLOCKED`, not `PASS`.

## Maintainer documentation

- [V18 index](v18/INDEX_V18.md)
- [Automated workflow](v18/docs/AUTOMATED_WORKFLOW.md)
- [Skill interoperability](v18/docs/SKILL_INTEROPERABILITY.md)
- [Task contract and state machine](v18/docs/TASK_CONTRACT_AND_STATE_MACHINE.md)
- [Approval boundaries](v18/docs/APPROVAL_BOUNDARIES.md)
- [V18 release notes](RELEASE_NOTES_V18.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
