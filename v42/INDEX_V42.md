# Roblox Codex Game Studio Kit — V42

V42.0.0 is the cumulative V1–V42 package with **272 native Codex skills**. Download only the current release.

## V42 — LiveOps, Events and Configuration Management

Four new native Codex skills:

1. **Live event lifecycle and scheduling** — explicit event state, timezone-aware windows, schedule conflicts, idempotent start/end, restart reconciliation, and cleanup.
2. **Experience config and feature-flag management** — Roblox ConfigService, typed config contracts, server-only readers, snapshot refresh boundaries, safe defaults, and flag ownership.
3. **Safe live config rollouts** — staged drafts, draftHash concurrency, test gates, human approval, Immediate/GradualRollout planning, and published readback.
4. **LiveOps config compatibility and rollback** — consumer registry, baseline comparison, additive key migration, revision history, staged restore, republish, and verification.

## V42 tool

v42/tools/v42.py provides:

- doctor: confirm the tool and selected project root.
- validate: validate config contracts, key types and limits, event windows, deployment gates, rollback rules, and runtime consumers.
- audit: generate an offline design report with unused config and operational warnings.
- compare: compare baseline/candidate manifests and detect removed config keys, type changes, default-value changes, and event additions/removals.

See v42/docs/V42_CLI.md for commands and trust boundaries.

## Roblox platform alignment

The design uses Roblox Experience Configs and the InExperienceConfig Open Cloud repository. ConfigService is server-only and read-only in game scripts; draft/publish/restore operations are Cloud API workflows with approved permissions. Existing ConfigSnapshot objects require refresh, ideally at a safe gameplay boundary. The documented Open Cloud repository supports 100 keys and key names up to 256 characters; the Experience Configs page documents up to 1,000 active configs, 100 conditions per experience, and up to 20 conditions per key.

## Important boundaries

V42 tools process local JSON contracts only. They do not call Roblox Open Cloud, stage or publish configs, inspect Luau references, read live telemetry, schedule events, or roll back a live experience. A compatibility report is a manifest comparison, not a whole-project static reference proof. Production changes require authorized human approval, staged tests, published readback, and a separately reviewed rollback plan.

All V1–V41 capabilities and safeguards remain included.
