# Roblox Codex Game Studio Kit — V25 Index

V25 is the current cumulative release candidate. It builds on V1-V24 and adds recoverable session continuity for long-running Roblox development work.

## V25 additions

- Durable local checkpoints in .codex/session/checkpoint.json.
- Atomic checkpoint writes, previous-checkpoint backup, short-lived write locks, and a hash-chained event journal.
- start, checkpoint, handoff, resume, status, verify, and recover CLI commands.
- A ready-to-paste RESUME_PROMPT.md containing the project goal, current stage, completed evidence, decisions, blockers, tests, changed files, and next actions.
- Two Codex skills for session continuity and bounded, independently testable task execution.
- Checkpoint privacy safeguards: no raw chat capture; credential-like strings are rejected; session data is Git-ignored by default.

## Quick start

Initialize once from the actual Roblox game project directory:

    python "<toolkit-root>/v25/tools/v25.py" start --root "<game-project-root>" --goal "Build and ship the Roblox experience"

After a verified stage:

    python "<toolkit-root>/v25/tools/v25.py" checkpoint --root "<game-project-root>" --stage "Server validation" --completed "Added server-side validation" --next "Run Studio integration tests" --test "Unit tests: PASS"

Before a conversation ends or a connection is interrupted:

    python "<toolkit-root>/v25/tools/v25.py" handoff --root "<game-project-root>" --stage "Server validation" --next "Run Studio integration tests"

To continue in a new conversation, paste the generated .codex/session/RESUME_PROMPT.md prompt and verify its claims against the working tree.

## Cumulative scope

V25 includes **207 native skills** and preserves the prior V1-V24 Roblox engineering, production, monetization, and platform-compliance guidance. No gambling, paid random outcomes, manipulative engagement loops, forced advertising, or spender profiling.

## Important limits

V25 cannot raise ChatGPT's conversation limit or prevent network interruptions. It cannot recover work that was never saved, uncommitted file changes from a deleted workspace, or remote state that was never synced. Use Git commits and secure backups in addition to checkpoints. The checkpoint is a concise aid to resume work, not a transcript or a replacement for testing.
