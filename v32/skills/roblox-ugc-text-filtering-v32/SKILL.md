---
name: roblox-ugc-text-filtering-v32
description: Design and audit safe Roblox user-generated text flows using native filtering APIs, server-side validation, and fail-closed display rules.
---

# User-generated text filtering

## Workflow

1. Inventory every player-controlled text entry and every place another player can see or receive it.
2. Separate native chat from custom non-chat text such as signs, pet names, custom labels, and persistent displays.
3. Prefer Roblox TextChatService for chat; retain platform filtering, permissions, and supported behavior.
4. For custom non-chat text, submit the value to the server and call TextService:FilterStringAsync() from a server Script after submission.
5. Use the appropriate TextFilterResult output method for the intended audience.
6. If filtering fails, suppress the submitted text. Never fall back to the original value.
7. Avoid storing raw submitted text in logs, analytics, DataStores, case files, or Codex reports.
8. Run the V32 audit and manually trace each reported source-to-display path.

## Quality rules

- Do not filter per keystroke or create a client-side filtering bypass.
- Do not extract contents of platform-integrated chat.
- Treat static audit results as review leads, not proof of runtime filtering.
- Test the published test experience with authorized accounts and audience settings.

## Safety

Do not ask players to share personal information. Preserve V1-V31 privacy, server-authority, and fair-gameplay safeguards.
