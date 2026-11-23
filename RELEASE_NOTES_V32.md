# V32.0.0 — Player Safety and Moderation Readiness

V32 extends the cumulative V1-V31 Roblox Codex Game Studio Kit with UGC text-filtering review, privacy-minimal moderation records, human review/appeals safeguards, and safety-by-design guidance.

## New capabilities

- Four native Codex skills:
  - roblox-ugc-text-filtering-v32
  - roblox-player-report-triage-v32
  - roblox-moderation-review-and-appeals-v32
  - roblox-player-safety-by-design-v32
- v32/tools/v32.py commands:
  - doctor: inspect local Luau inventory and optional tools.
  - audit: detect common legacy/client text-filter calls and possible raw-input display assignments.
  - validate-policy: validate review SLAs, retention/appeal windows, second-review policy, and disabled automated enforcement.
  - validate-case: validate one case using opaque references, fixed codes, review roles, and appeal states.
  - validate-register: validate a batch of cases and reject duplicate opaque case IDs.
- Three schemas, three examples, three guides, regression tests, cumulative package patcher/auditor, and a V1-V32 quality workflow.
- Cumulative package target: **232 native Codex skills**.

## Safety and evidence boundaries

- Custom non-chat text must follow current Roblox server-side TextService filtering guidance; filtering failure must fail closed.
- Prefer native TextChatService. Platform-integrated chat content is not exposed to game scripts and must not be scraped or reimplemented.
- Static source findings are advisory and cannot prove the filtered value displayed at runtime.
- Case files reject player IDs, usernames, raw chat, free-text allegations, URLs, and evidence paths. Original identities and evidence remain in authorized Roblox moderation systems.
- Moderation decisions are human-reviewed and appealable. V32 never bans, kicks, mutes, removes content, or changes live configuration.
- High-impact cases can require an independent second reviewer.
- All V1-V31 features and safeguards remain cumulative, including server authority, privacy-safe aggregate analytics, fair monetization, fixed paid outcomes, and mandatory no-gambling requirements.

## Validation

The V32 workflow reconstructs the pinned V17 baseline, applies V18-V32 overlays, runs inherited regression suites plus V32 tests, audits the 232-skill package and repository, builds ZIP and TAR.XZ archives, compares extracted contents, and verifies SHA-256 checksums. Studio runtime behavior, published-experience filtering, Creator Dashboard reviews, and real moderation operations remain human-run validation tasks.
