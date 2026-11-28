---
name: roblox-branching-dialogue-and-choice-design
description: Build Roblox dialogue graphs with stable localization keys, clear choice semantics, reachable endings, and server-validated consequences.
---

# Roblox branching dialogue and choice design

Store authored dialogue separately from UI and runtime state. Use stable conversation, node, choice, and localization-key IDs; display text is presentation, never identity. Keep speaker, text keys, labels, and destinations explicit for writer and engineer review.

Every line node has one to four choices. Each choice has a stable ID, localization key, visible label, and valid destination. Ending nodes have no choices. Do not promise an outcome the game does not deliver.

A client may display a conversation and submit a choice ID. The server verifies conversation context, current node, and choice availability under server-owned state. Re-check quest prerequisites and story flags before changing progression. Never accept an arbitrary destination or client-provided reward.

Keep side effects explicit: a choice requests a named outcome rather than embedding arbitrary code or a client-controlled function name. Apply durable outcomes idempotently using V40 persistence guidance.

Every node must be reachable from the start and have a route to an ending. Loops are allowed only when every node retains a valid route out. Define cancel, skip, timeout, respawn, and reconnect behavior. Provide a neutral exit for optional conversations. Never use deceptive urgency or dialogue to pressure players into spending or disclosing personal information.

Keep text keys separate from translations, preserve placeholders, avoid concatenated fragments, and allow text expansion. Support touch, keyboard, gamepad, readable timing, captions, and dismiss/advance controls.

The V45 validator checks graph structure and key uniqueness only. It does not translate text, inspect voice assets, test UI focus, or prove server validation. Review in Studio on target devices and languages.
