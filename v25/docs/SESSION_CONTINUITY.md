# V25 Session Continuity and Recovery

V25 adds local, portable project checkpoints and concise handoff prompts. It addresses lost development context after a conversation reaches its length limit or a Codex connection is interrupted. It does not extend ChatGPT's conversation limit or recover unsaved work.

## Requirements

- Python 3.10 or newer (standard library only).
- A writable Roblox project directory.
- The V1-V25 cumulative toolkit installed or the v25/tools/v25.py script available.

## First-time setup

From PowerShell or a terminal, initialize the record in the actual game project directory:

    python "<toolkit-root>/v25/tools/v25.py" start --root "<game-project-root>" --goal "Build and ship the Roblox experience"

The tool creates .codex/session/ with:
- checkpoint.json: current compact structured state with a SHA-256 integrity digest;
- checkpoint.json.bak: the previous valid checkpoint;
- events.jsonl: an append-only, hash-chained event journal;
- RESUME_PROMPT.md: a ready-to-paste handoff prompt;
- .gitignore: keeps local checkpoint data out of normal commits.

Do not use the toolkit installation folder as --root unless that folder is also the actual game project.

## Save progress after each meaningful stage

Example:

    python "<toolkit-root>/v25/tools/v25.py" checkpoint --root "<game-project-root>" --stage "Data persistence tests" --completed "Added retry handling and verified serialization" --next "Run Studio integration tests" --test "python -m unittest: PASS" --file "src/Server/DataService.luau"

Arguments --completed, --next, --decision, --blocker, --test, and --file can be repeated. Completed, decisions, tests, and files add unique entries. --next replaces the next-action list. Use --clear-next to clear it. --blocker adds unresolved blockers; --clear-blockers clears them before any new blockers are applied.

Valid statuses: active, paused, blocked, and completed.

## Handoff before an interruption

The handoff command saves a checkpoint and refreshes RESUME_PROMPT.md in one step:

    python "<toolkit-root>/v25/tools/v25.py" handoff --root "<game-project-root>" --stage "Current implementation stage" --completed "Verified server validation tests" --next "Inspect the remaining integration test failures"

To resume, paste .codex/session/RESUME_PROMPT.md into the next Codex or ChatGPT conversation. The prompt instructs the next session to inspect Git and source files, verify previous claims, and continue the first unfinished action.

## Recovery commands

- status --root "<game-project-root>": show the saved state.
- verify --root "<game-project-root>": check state integrity and journal hash chain.
- resume --root "<game-project-root>": print the latest resume prompt and recover from the previous valid backup if the primary file is damaged.
- recover --root "<game-project-root>": explicitly restore the previous valid backup.

Writes use a same-directory temporary file followed by atomic replacement. A process-aware lock prevents overlapping writes and does not break a stale-looking lock owned by a live process. Checkpoints are bound to the original canonical project path: every command refuses to read or mutate a checkpoint when --root points at a different project.

The event journal validates each complete record's JSON shape, sequence number, digest, previous hash, and checkpoint reference. verify also confirms that the current checkpoint is represented in the verified journal. Only an unterminated final record is discarded during the next append; malformed complete records are reported as corruption and are never silently repaired. recover restores the previous valid backup, regenerates the resume prompt, and records a recovery event where the journal remains writable.

## Data and privacy

The tool stores only development metadata explicitly supplied through command-line arguments. It does not capture chats, screenshots, keystrokes, player records, or secrets. Credential-like strings are rejected. Never put raw logs containing private player information or tokens in a checkpoint. Checkpoint folders are ignored by Git by default; export or back them up securely when cross-device recovery is required.

## Recommended working rhythm

Keep implementation stages short enough that one stage can be safely repeated. Checkpoint after a testable stage, before long or risky operations, and when handing work to another person/session. Commit working code separately. A checkpoint cannot restore files lost from an erased workspace or replace source control.
