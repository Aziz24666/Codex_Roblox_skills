# V14 — Roblox Codex Game Studio Kit

**Release date:** November 16, 2026  
**Tag:** `v14.0.0`  
**License:** MIT

V14 is the cumulative release of the Roblox Codex Game Studio Kit. It includes the capabilities of V1–V13 plus a new scripted Roblox Studio testing and verification toolchain.

## Highlights

- **136 cumulative specialist Codex skills**, including ten new skills focused on Studio automation and test engineering.
- **Studio Test Runner plugin** to orchestrate scripted Studio test scenarios.
- **Disposable Studio test fixture** with server/client synthetic-data handshakes and one-client/two-client examples.
- **Schema-driven test scenarios and reports**, with validation to prevent unsupported PASS claims.
- **Deterministic test catalog generation**, report/scenario linters, package doctor, CI preflight, and regression tests.
- **Four Rojo build targets:** sample Roblox experience, Content Factory plugin, V14 Studio Test Runner plugin, and the disposable V14 test fixture.

## New V14 specialist skills

- `roblox-studio-scripted-test-orchestration`
- `roblox-multiplayer-scenario-engineering`
- `roblox-device-simulator-automation`
- `roblox-client-server-contract-testing`
- `roblox-deterministic-test-fixtures`
- `roblox-test-data-isolation`
- `roblox-network-condition-verification`
- `roblox-failure-reproduction-and-replay`
- `roblox-studio-test-plugin-engineering`
- `roblox-runtime-test-evidence`

## Validation

The V14 GitHub Actions workflow completed successfully:

- V14 Python preflight and regression suite: passed.
- Luau source compilation: passed.
- Rojo builds for all four targets: passed.
- Complete V14 ZIP and TAR.XZ package creation: passed.

The local package validation also recorded **47 passing Python unit tests**, successful skill metadata and scenario checks, and a clean package doctor.

## Important runtime limitations

CI compilation and Rojo builds do not run Roblox Studio. The Studio Test Runner plugin and test fixture have been built, but Studio-runtime playtests, physical-device checks, network simulation inside Studio, published-service behavior, asset permissions, and production deployment checks must still be performed in their relevant Roblox environments. The sample tests use synthetic data and are not evidence of a live production game's behavior.

## Installation

1. Download either `roblox-codex-game-studio-kit-v14.zip` or `roblox-codex-game-studio-kit-v14.tar.xz` below.
2. Extract the archive.
3. Open the extracted package root in Codex.
4. Read `AGENTS.md` and `INDEX_V14.md`.
5. Follow `docs/V14_STUDIO_TEST_PLUGIN_RUNBOOK.md` to install and run the Studio test plugin in a disposable Studio environment.

V14 is cumulative. You do not need separate V1–V13 downloads.

## Checksums

The source package includes `V14_SHA256SUMS.txt`, a checksum manifest for the packaged files. Verify files against that manifest after extraction.

## Acknowledgements

Built as an independent community toolkit using Roblox Studio, Luau, Rojo, and Codex-oriented workflows. This project is not affiliated with or endorsed by Roblox Corporation or OpenAI.
