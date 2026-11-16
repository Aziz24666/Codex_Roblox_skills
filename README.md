# Roblox Codex Game Studio Kit

[![CI](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A research-first, modular Roblox game-development toolkit for Codex. **The current cumulative release is V14**: 136 specialist skills, reusable Luau systems, data-driven gameplay architecture, schema-driven Studio content tools, and a scripted Studio testing harness.

You do not need to download V1–V13 separately. V14 is cumulative and includes the earlier releases.

## What's new in V14

- **136 specialist Codex skills**, including ten new skills for Studio scripted tests, multiplayer scenario engineering, device simulation, remote-contract testing, deterministic fixtures, test isolation, network-condition verification, failure replay, test-plugin engineering, and runtime evidence.
- A separate **Studio Test Runner plugin** that orchestrates synthetic test scenarios through Studio's test APIs.
- A **disposable Studio test fixture** with one-client and two-client server/client handshake examples.
- JSON scenario and report schemas, deterministic catalog generation, scenario/report linters, evidence checks, and a package doctor.
- CI now validates the cumulative package, compiles Luau, builds the sample experience and three Studio/test assets, and packages V14.

## Get the full V14 package

A complete V14 ZIP and TAR.XZ archive are produced by the **V14 Roblox toolkit CI** workflow after the repository update. Open [Actions](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/ci.yml), select the latest successful run on `main`, and download the artifact named **`roblox-codex-game-studio-kit-v14`**.

The repository stores the V14 change set as a compact overlay on the existing V13 source archive, avoiding a second copy of the entire project in Git history. The workflow verifies the overlay checksum, reconstructs the cumulative V14 source tree, and uploads the full archives as an Actions artifact.

To reconstruct the package locally from a clone:

```bash
mkdir -p /tmp/roblox-v14
tar -xJf dist/roblox-codex-game-studio-kit-v13.tar.xz -C /tmp/roblox-v14
mv /tmp/roblox-v14/roblox-codex-game-studio-kit-v13 /tmp/roblox-v14/roblox-codex-game-studio-kit-v14
cat dist/v14-overlay-b64parts/part-*.b64 | base64 --decode > /tmp/roblox-v14/overlay.tar.xz
echo "8ac5adfe3aaa54e33c674e979cf2814fc8f311933176f1890fadf0fa84b79158  /tmp/roblox-v14/overlay.tar.xz" | sha256sum --check
tar -xJf /tmp/roblox-v14/overlay.tar.xz -C /tmp/roblox-v14/roblox-codex-game-studio-kit-v14
```

## Quick start with Codex

1. Extract the full V14 archive.
2. Open the extracted package root in Codex.
3. Read `AGENTS.md` and `INDEX_V14.md`.
4. Ask Codex to audit the existing game's architecture and source of truth before changing files.
5. Use `$roblox-game-builder` as the main orchestrator and load specialist skills only as needed.

Suggested first instruction:

```text
Read AGENTS.md and INDEX_V14.md. Use $roblox-game-builder as the primary orchestrator.
Audit this project's source of truth before modifying files. Research current official Roblox
documentation before substantive API decisions. Create a prioritized roadmap, then implement
one complete playable vertical slice at a time. Prefer reusable, data-driven systems and
strictly typed Luau. Run available tests and builds, report actual evidence, and clearly mark
Studio/runtime checks that were not executed. Do not publish or modify live production data
without explicit authorization.
```

## V14 Studio test harness

The plugin and disposable fixture are built as separate assets. See `docs/V14_STUDIO_TEST_PLUGIN_RUNBOOK.md` and `docs/V14_STUDIO_TEST_HARNESS_ARCHITECTURE.md` for setup and limitations.

A CI build does **not** execute Roblox Studio playtests. Install the plugin in a local Studio profile and run the disposable fixture to collect Studio-runtime evidence. Physical-device checks, published-service behavior, asset permissions, and production deployment still require their respective environments and approvals.

## CI

Every push to `main`, pull request, and manual workflow dispatch runs:

- Cumulative V13/V14 Python package preflight and regression tests.
- V14 scenario/report validation and generated-catalog drift checks.
- Pinned Luau CLI compilation with a SHA-256-verified binary.
- Pinned Rojo builds for the sample experience, Content Factory plugin, V14 Test Runner plugin, and disposable test fixture.
- Upload of build outputs and the complete V14 ZIP/TAR.XZ package as downloadable workflow artifacts.

The workflow uses read-only repository permissions and does not publish anything to Roblox.

## Repository documentation

- [V14 index](INDEX_V14.md)
- [Cumulative README](README.md in the full package)
- [V14 validation report](V14_TEST_RESULTS.md in the full package)
- [Repository metadata suggestions](GITHUB_REPOSITORY_METADATA.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
