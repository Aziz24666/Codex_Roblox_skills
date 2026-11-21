# Roblox Codex Game Studio Kit

[![V19 Quality](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v19-quality.yml/badge.svg)](https://github.com/Aziz24666/Codex_Roblox_skills/actions/workflows/v19-quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Current release: V19.0.0 — Testing Intelligence and Evidence Governance.** This is the complete cumulative V1–V19 Roblox game-development toolkit for Codex. You only need the current V19 release; earlier versions do not need separate downloads.

## Download

The complete package is attached to the [V19.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v19.0.0) as ZIP and TAR.XZ archives, with SHA-256 checksums.

## What's included

- **180 native Codex skills** across Roblox architecture, Luau, gameplay systems, characters and avatars, UI/input/accessibility, multiplayer/networking, security, persistence, economy, procedural content, NPCs, Studio plugins/MCP, performance, testing, research, and release engineering.
- **Five V19 verification specialists** for risk-based testing, Luau static analysis/type safety, Studio multi-client tests, deterministic routing benchmarks, and evidence auditing.
- A deterministic 12-case routing regression corpus with positive and negative selection expectations.
- A local Python CLI for risk-based test-plan generation, routing evaluation, and evidence validation.
- Structured evidence rules: PASS requires an executed command/scenario, environment, tool version, build identity, expected/actual result, and a non-empty artifact.
- All V18 workflow orchestration, shared contracts, approval gates, and mandatory no-gambling monetization policy.
- Versioned schemas, examples, documentation, regression tests, Studio workflows, and CI package audits.

## Requirements

- **Python 3.13** is the supported and CI-validated runtime. The inherited package uses \`tomllib\`, included in Python 3.11 and later.
- From the extracted package root, install validation dependencies:

  \`\`\`bash
  python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
  \`\`\`

The V19 routing and planning commands use the standard library. Schema and full package validation require the installed dependencies.

## Quick start with Codex

1. Download and extract the complete V19 ZIP.
2. Open the extracted package root in Codex.
3. Read \`AGENTS.md\` and \`INDEX_V19.md\`.
4. Start substantial work with \`$roblox-end-to-end-development-orchestrator\`.
5. Inspect the project with \`python v18/tools/v18.py doctor --root .\`.
6. Generate a risk-based verification plan:

   \`\`\`bash
   python v19/tools/v19.py plan-tests --root . --task "Build a multiplayer inventory trade system" --changed src/Server/Trading.luau
   \`\`\`

7. Run the applicable checks in their actual environments and record outcomes.
8. Validate an evidence packet with \`python v19/tools/v19.py validate-evidence --root . --file path/to/verification-evidence.json\`.

## V19 commands

\`\`\`bash
python v19/tools/v19.py evaluate-routing --root .
python v19/tools/v19.py plan-tests --root . --task "..."
python v19/tools/v19.py validate-evidence --root . --file path/to/verification-evidence.json
python v19/tools/v19.py verify --root .
\`\`\`

The routing benchmark evaluates deterministic skill selection only; it does not assess LLM reasoning quality or prove generated game code is correct. Test-plan generation is planning only: it does not execute Luau tools, launch Roblox Studio, or run multiplayer/device/live-service tests.

## Validation and evidence boundaries

GitHub Actions validates overlay metadata, Python regression tests, schemas, the routing corpus, cumulative package audits, SHA-256 manifests, and ZIP/TAR.XZ extraction integrity. It does **not** launch Roblox Studio. Studio playtests, multi-client runtime checks, physical-device testing, performance profiling, live DataStore behavior, asset permissions, live purchase fulfillment, and production operations must be executed in their real authorized environments and recorded separately. Unexecuted checks must remain \`NOT_RUN\` or \`BLOCKED\`, not \`PASS\`.

## Maintainer documentation

- [V19 index](INDEX_V19.md)
- [Testing and evidence strategy](v19/docs/TESTING_AND_EVIDENCE.md)
- [Studio and multiplayer automation](v19/docs/STUDIO_TEST_AUTOMATION.md)
- [Skill-routing benchmarks](v19/docs/SKILL_BENCHMARKS.md)
- [Research snapshot](v19/docs/RESEARCH_SNAPSHOT.md)
- [V19.0.0 release notes](RELEASE_NOTES_V19.md)
- [V18 no-gambling and fair monetization policy](v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md)
- [MIT License](LICENSE)

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
