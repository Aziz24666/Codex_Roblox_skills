# V19 — Testing Intelligence, Static Analysis, and Evidence

V19 extends the V1–V18 cumulative toolkit with a measurable verification layer. It adds five specialist skills, risk-based test planning, Luau static-analysis guidance, Studio multiplayer testing workflows, deterministic skill-routing benchmarks, and evidence validation.

V19 does **not** claim to run Roblox Studio, multiplayer sessions, device tests, or live services inside ordinary GitHub Actions. It helps the developer plan these checks and record results without treating an unavailable test as a pass.

## Start here

- \`INDEX_V19.md\` — current cumulative index and skill routing.
- \`docs/TESTING_AND_EVIDENCE.md\` — test levels, risk matrix, and evidence rules.
- \`docs/STUDIO_TEST_AUTOMATION.md\` — StudioTestService and Studio MCP workflow.
- \`docs/SKILL_BENCHMARKS.md\` — deterministic routing-evaluation methodology.
- \`tools/v19.py\` — routing benchmark, test-plan generator, and evidence validator.

## Requirements

Use Python 3.13 (CI runtime). Install the inherited validation dependencies from the package root:

\`\`\`bash
python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
\`\`\`

The V19 CLI uses the standard library for planning and routing evaluation. JSON Schema validation requires the inherited \`jsonschema\` dependency.

## Commands

\`\`\`bash
python v19/tools/v19.py evaluate-routing --root .
python v19/tools/v19.py plan-tests --root . --task "Add multiplayer inventory trading" --changed src/Server/Trading.luau
python v19/tools/v19.py validate-evidence --root . --file .codex/workflows/tasks/example/verification-evidence.json
python v19/tools/v19.py verify --root .
\`\`\`

Planning and benchmark commands do not execute project code. The test-plan generator creates recommendations marked \`NOT_RUN\`; evidence validation only checks the supplied record and referenced local artifacts.

## Verification boundary

Static analysis is not a Studio playtest. A Studio playtest is not a multi-client test. A multi-client test is not a device matrix or a live-service test. Keep each result tied to its actual environment, tool version, build identity, command, expected outcome, observed outcome, and evidence artifact.

Roblox references used by this release:
- https://create.roblox.com/docs/luau/type-checking
- https://create.roblox.com/docs/reference/engine/classes/StudioTestService
- https://create.roblox.com/docs/studio/mcp
- https://create.roblox.com/docs/studio/testing-modes
- https://create.roblox.com/docs/performance-optimization/identify
