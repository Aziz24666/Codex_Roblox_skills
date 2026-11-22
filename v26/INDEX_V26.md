# Roblox Codex Game Studio Kit — V26 Index

V26.0.0 is the current cumulative release. It contains V1-V25 plus Studio MCP workflow tooling and a reviewable Studio test-planning layer.

## V26 additions

- Three Codex skills for Studio MCP orchestration, multiplayer/device testing, and safe edit/evidence review.
- A read-only `doctor` command that checks a project root and an optional Roblox Studio MCP JSON configuration without executing commands, changing client settings, or claiming a connection is active.
- A `plan` command that creates a bounded Studio test-plan manifest inside the selected project root.
- A `verify-plan` command that rejects malformed plans and plans that remove manual-review and production-safety boundaries.
- A 1/2/4/8-client test matrix, device coverage guidance, network-condition coverage, and evidence checklist.
- Explicit limits between local Studio MCP work, GitHub Actions CI, unpublished test experiences, and production operations.

## Quick start

Read-only project and MCP configuration check:

    python "<toolkit-root>/v26/tools/v26.py" doctor --root "<game-project-root>" --config "<path-to-your-mcp.json>"

Generate a reviewable Studio test plan:

    python "<toolkit-root>/v26/tools/v26.py" plan --root "<game-project-root>"

Verify it later:

    python "<toolkit-root>/v26/tools/v26.py" verify-plan --path "<game-project-root>/.codex/testing/studio-mcp-test-plan.json"

The planner writes only the plan file. It does not connect to Studio, invoke MCP tools, run a playtest, edit game scripts, publish a place, or access live player data.

## Studio workflow

1. Use Roblox Studio's built-in MCP enablement and client Quick Connect where available.
2. Confirm the target open Studio instance and place before edits.
3. Start with read-only DataModel and script inspection.
4. Make one narrow, reviewable change at a time.
5. Run an appropriate Studio playtest and collect logs/screenshots.
6. Record test limitations and unresolved failures; never turn an unrun scenario into a pass.

StudioTestService supports up to eight simulated clients per multiplayer test session. Device Simulator and Network Simulator are Studio testing features; they do not change a published experience or replace real-world player validation.

## Cumulative scope

V26 includes **210 native Codex skills** and preserves prior Roblox engineering, quality, production, and fair-monetization guidance. Paid random rewards, gambling-like mechanics, manipulative engagement loops, forced ads, and spender profiling remain prohibited.

## Limits and approvals

- A valid config is not proof that Studio MCP is connected or that the expected Studio instance is available.
- GitHub Actions runners do not automatically have access to a developer's local Studio MCP process.
- Keep tests isolated from production DataStores and production player state.
- Review generated or edited scripts before saving the place.
- Saving a place, publishing, production DataStore writes, and player-impacting Open Cloud operations require explicit human review and approval.
- Use least-privilege Open Cloud permissions; never assume broad permissions are safe.

See [Studio MCP workflow](docs/STUDIO_MCP_WORKFLOW.md), [multiplayer and device testing](docs/MULTIPLAYER_DEVICE_TESTING.md), and [safe automation boundaries](docs/SAFE_AUTOMATION_BOUNDARIES.md).
