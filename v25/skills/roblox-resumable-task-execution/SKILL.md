---
name: roblox-resumable-task-execution
description: Structure Roblox development work into independently testable stages that can be resumed safely after Codex interruptions.
---

# Roblox Resumable Task Execution

Use this skill for multi-step Roblox engineering, tool-building, refactors, debugging, and release work.

## Stage contract

Before editing, define the current stage with:
- one concrete deliverable;
- the files or systems allowed to change;
- a test or observable acceptance criterion;
- dependencies and known blockers;
- the next stage to run after success.

Prefer one feature, subsystem, or tightly related group of changes per stage. Avoid giant all-at-once edits. Do not split trivial related edits merely to create paperwork.

## Execution loop

1. Inspect current source and existing tests.
2. State the stage objective and acceptance checks.
3. Make the smallest coherent implementation.
4. Run targeted tests and relevant static checks.
5. Review the diff for regressions, security issues, platform compliance, and accidental unrelated edits.
6. Save a V25 checkpoint with completed results, tests, changed files, decisions, blockers, and the next action.
7. Continue only when the stage is verified or clearly mark it blocked.

Use .codex/session/checkpoint.json as a compact recovery record. Keep Git history and actual test output as the evidence source. Never mark a stage complete just because code was written.

## Interruption rules

- Before a long-running task or a risky command, record the intended action and safe recovery point.
- After a command returns, record its actual exit status and the useful result, not an optimistic summary.
- If the conversation or tool connection drops, resume from the checkpoint and repository state. Inspect uncommitted work before changing it.
- Never claim asynchronous or background progress unless a real automation system is configured and verified.
- When the context is nearly full, use the handoff command and finish with the resume file location.
- If no checkpoint can be written, state that limitation plainly and provide a concise manual handoff prompt.

## Roblox-specific safeguards

Preserve server authority for currency, inventory, purchases, progression, and permissions. Validate all client input on the server, rate-limit remote calls, and test exploit-resistant failure paths. Keep player data collection minimal and transparent.

Maintain the inherited V18-V24 monetization constraints: no gambling, paid random outcomes, manipulative engagement loops, fake scarcity, forced advertising, or spender profiling. Do not bypass Roblox platform rules. Test changes in Studio and use human approval before live operations.
