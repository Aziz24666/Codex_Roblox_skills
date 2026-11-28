---
name: roblox-quest-state-and-dialogue-integration
description: Integrate quests and dialogue with server-owned player state, versioned IDs, safe transitions, and recoverable persistence.
---

# Roblox quest state and dialogue integration

Keep authored definitions immutable and versioned separately from per-player state. Persist stable quest IDs, lifecycle status, bounded typed objective progress, completed IDs, and only the story flags needed to resume. Do not persist UI objects, localized strings, Instance paths, arbitrary client payloads, or copies of the catalog.

Define schema versions and deterministic migrations for renamed, removed, or split quest IDs. For changed active quests, preserve compatible progress, map it through an explicit migration, or retire it with a reviewed explanation. Never infer migrations from display titles.

Expose narrow server operations such as ActivateQuest, UpdateObjective, SelectDialogueChoice, and CompleteQuest. Each verifies ownership, current state, allowed transition, prerequisites, and content version. Clients send intent with stable IDs; servers resolve definitions and destinations.

Make transitions idempotent. Duplicate objective signals, reconnect retries, remote requests, and recovery must not duplicate completion effects or rewards. Use stable transition/receipt identifiers and V40 profile/reward patterns. Batch meaningful writes rather than saving every frame.

Document disconnect during a choice, shutdown, missing IDs, stale UI, removed NPCs, and unavailable objectives. Reject stale choices and refresh current state; never redirect them to a different reward or story outcome.

Test concurrent selections, duplicate requests, disconnect/rejoin, content migration, unavailable objectives, and reward retries. Review remotes, server handlers, profile writes, migration code, and Studio traces. Never place credentials or player identifiers in fixtures.
