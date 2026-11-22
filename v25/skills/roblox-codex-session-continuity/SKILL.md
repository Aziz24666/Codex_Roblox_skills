---
name: roblox-codex-session-continuity
description: Preserve Roblox project progress across interrupted Codex conversations and tool sessions with small durable checkpoints and verified handoffs.
---

# Roblox Codex Session Continuity

Use this skill whenever work may span multiple conversations, tool calls, or long implementation sessions.

## Before doing work

1. Identify the actual Roblox project root. Do not assume the toolkit installation directory is the game project.
2. Check whether .codex/session/checkpoint.json exists in the project root.
3. When it exists, run the V25 verify, status, and resume commands using the path to the installed toolkit's v25/tools/v25.py file.
4. Inspect Git branch, working tree, recent commits, and actual changed files. Verify completed checkpoint claims against the repository and tests.
5. Do not ask the user to repeat goals, decisions, or constraints already stored in a valid checkpoint.

When no checkpoint exists, initialize one after the project goal is known:

    python "<toolkit-root>/v25/tools/v25.py" start --root "<project-root>" --goal "<durable project goal>"

## During implementation

- Work in small, bounded stages with a clear deliverable and acceptance check.
- Before a risky refactor, major dependency change, long-running build, or tool operation, save a checkpoint.
- After each independently verified stage, record the completed item, test result, changed files, current stage, and next action.
- Preserve important architectural decisions and blockers. Do not paste chat transcripts into the checkpoint.
- Never record credentials, API keys, passwords, tokens, private user details, or data not needed to resume the development task.
- Keep Git commits as the source of truth for code. A checkpoint does not replace commits, backups, or tests.
- Do not claim a test, build, push, release, Studio run, or Marketplace action passed without current evidence.
- Before destructive operations or live publishing, require the user's explicit approval and preserve a recoverable Git state.

Example checkpoint:

    python "<toolkit-root>/v25/tools/v25.py" checkpoint --root "<project-root>" --stage "Server validation" --completed "Added server-side purchase receipt tests" --next "Run the test suite and inspect failures" --test "python -m unittest: PASS" --file "src/Server/PurchaseService.luau"

## When handing off or nearing a context limit

Run one command to save progress and create the handoff:

    python "<toolkit-root>/v25/tools/v25.py" handoff --root "<project-root>" --stage "<current stage>" --completed "<verified result>" --next "<first unfinished action>"

Then tell the user where .codex/session/RESUME_PROMPT.md was written. The prompt is designed to be pasted into a new conversation or Codex session.

## When resuming after interruption

- Read the generated handoff prompt and re-verify all important claims.
- If the primary checkpoint is damaged, resume can fall back to the last valid .bak checkpoint. Explain that the fallback may be one checkpoint behind.
- If needed, run recover to explicitly restore the previous valid backup.
- If work was interrupted before the latest checkpoint, inspect uncommitted changes and tests; do not overwrite or discard them automatically.
- Continue the first unfinished next action, checkpoint again, and keep the user informed.
- If no checkpoint can be written, state that limitation plainly and provide a concise manual handoff prompt.

## Limits

This tool cannot prevent ChatGPT's own conversation-length or network limits, and it cannot reconstruct unsaved thoughts or uncommitted work after a machine or workspace is lost. It makes saved project state, verified decisions, next steps, and test evidence portable across sessions. Save checkpoints frequently enough that losing the last small stage is acceptable.
