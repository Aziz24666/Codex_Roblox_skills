# V26.0.0 — Roblox Studio MCP and Automated Testing

V26.0.0 extends the cumulative Roblox Codex Game Studio Kit from V1-V25 with a safer, evidence-first Studio MCP workflow and repeatable test planning.

## New capabilities

- Add three native Codex skills:
  - `roblox-studio-mcp-workflow`
  - `roblox-studio-multiplayer-device-testing`
  - `roblox-studio-safe-edit-review`
- Add a read-only `doctor` command to inspect an optional Roblox Studio MCP JSON configuration without running its configured command or exposing config values.
- Add `plan` to generate a structured, review-only Studio test-plan manifest within the selected project root.
- Add `verify-plan` to validate plan structure, 1-8 client limits, manual execution mode, and mandatory safety/approval invariants.
- Add guidance for Studio MCP instance targeting, DataModel/script inspection, bounded edits, read-back review, Studio console/screenshot evidence, and multi-agent write ownership.
- Add a test matrix for 1, 2, 4, and 8 simulated clients, device profiles, controller/orientation coverage, and degraded network conditions.

## Safety and reliability

- Keep local Studio MCP separate from GitHub Actions; hosted CI does not imply access to a developer's local Studio process.
- Distinguish a config check from a real connection and a test plan from an executed playtest.
- Require isolated test places and synthetic data for routine automation.
- Keep saving, publishing, production DataStore writes, and player-impacting Open Cloud calls behind explicit human approval.
- Preserve V1-V25 capabilities, the V25 project-root-bound checkpoint system, and all fair-monetization/no-gambling requirements.

## Validation

- V26 utility unit tests cover config parsing, secret-free diagnostics, plan generation, overwrite protection, path traversal/symlink rejection, and safety-invariant tampering.
- Cumulative package audit requires 210 native skills and all V26 deliverables.
- Repository-wide syntax, JSON, Markdown-link, and skill-metadata audit runs after V26 integration.
- All inherited V14-V25 workflow checks remain in the CI matrix.
- Release ZIP and TAR.XZ archives are independently tested, extracted, compared, and checksummed.

## Compatibility

- V26 adds files and CLI commands; it does not change the V25 checkpoint schema or existing V1-V25 commands.
- The Studio MCP configuration doctor is read-only. The test-plan generator does not execute Studio or MCP operations.
