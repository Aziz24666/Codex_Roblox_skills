# Branching dialogue design

Conversations are graphs of line and ending nodes. Every line has one to four choices; each choice has a stable ID, localization key, label, and destination. End nodes have no choices.

All nodes must be reachable from the start and have a route to an ending. Loops are permitted only if every node in the loop retains a path out. Review loops for comprehension and provide close/cancel behavior.

A client submits only a choice ID. The server verifies conversation context, current node, availability, prerequisites, and story-flag transition. Never accept client-provided destination or reward.

Use stable text keys, avoid concatenation, and design for translation expansion, RTL layouts, readable timing, and touch/keyboard/gamepad navigation.
