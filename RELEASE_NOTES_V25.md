# V25.0.0 — Session Continuity and Interruption Recovery

V25 adds a small standard-library-only Python CLI and two Codex skills to make long Roblox development tasks recoverable across conversation limits, connection interruptions, and session handoffs.

## What's new

- Create and update structured local project checkpoints.
- Generate a ready-to-paste handoff prompt in one command.
- Restore the previous valid checkpoint when the primary file is damaged.
- Write state atomically, keep a previous checkpoint backup, serialize concurrent writes, and maintain a hash-chained event journal.
- Track current stage, completed and next actions, decisions, blockers, validation results, changed files, branch, and commit.
- Add bounded-stage execution guidance to AGENTS.md.
- Add automated tests and cumulative package audits.

## Privacy and safety

V25 stores only explicitly supplied development metadata. It does not collect chat transcripts, keystrokes, screenshots, or player records. Credential-like strings are rejected and session files are Git-ignored by default. Existing V18-V24 fair-monetization, no-gambling, server-authority, and Roblox platform-compliance rules remain in force.

## Limits

V25 cannot change ChatGPT's conversation limit, prevent network outages, or recover unsaved work from a deleted workspace. Git commits and secure external backups remain necessary. Checkpoint records must be verified against the actual source tree and test evidence before continuing.
