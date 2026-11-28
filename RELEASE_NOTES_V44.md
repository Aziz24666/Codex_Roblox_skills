# V44.0.0 — Player Feedback and Research Operations

V44 extends the cumulative Roblox Codex Game Studio Kit from 276 to **280 native Codex skills**.

## New skills

- Feedback study design and non-leading playtest prompts.
- Privacy-conscious collection, notice, data minimization, access, and retention.
- Qualitative feedback coding and theme synthesis with uncertainty and sampling caveats.
- Human-owned feedback triage, evidence traceability, testable actions, and player follow-up.

## Offline V44 CLI

- validate-study: validates study scope, build/window, sampling target, notices, retention, and structured prompts.
- validate-data: validates study-scoped coded feedback, unique opaque references, controlled categories, timestamps, and allowed fields.
- audit: creates a readiness report and flags potentially leading prompts.
- summarize: emits descriptive coded-submission count bands and suppresses groups below the predeclared small-cell threshold.
- doctor: verifies the selected project root and reports offline tool/runtime details.

## Safeguards and limitations

V44 is offline. It does not collect feedback, inspect raw text, detect PII, verify consent or deletion, connect to Roblox, authenticate evidence references, infer population sentiment, calculate statistical significance, create external backlog tasks, or approve a release. It rejects unknown fields but cannot detect sensitive content hidden inside otherwise permitted values. Human verification and approved source-system controls remain necessary.

## Verification

The V44 workflow runs schema/example validation and unit tests on Windows and Ubuntu, then reconstructs and audits the cumulative V1–V44 package from the published V41 baseline with V42/V43/V44 overlays, regression suites, archive equivalence, and SHA-256 verification.

V44 is proposed on its pull request; the GitHub release is published only after the release branch is merged to main and the release-gated workflow succeeds.
