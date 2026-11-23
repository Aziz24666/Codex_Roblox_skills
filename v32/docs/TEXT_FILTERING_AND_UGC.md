# Text filtering and user-generated content safety

V32 adds an offline audit for common text-filtering hazards and strict validators for privacy-minimal moderation records. It does not contact Roblox, call TextService, inspect live messages, or modify source files.

## Use native Roblox text systems

Roblox recommends filtering all user-generated text that can be seen by other players, including signs, pet names, custom labels, and text-box submissions. For custom non-chat text, call TextService:FilterStringAsync() from a server Script after the player submits the value. Use the returned TextFilterResult and select the audience-appropriate output method.

- [TextService API](https://create.roblox.com/docs/reference/engine/classes/TextService)
- [Text filtering guide](https://create.roblox.com/docs/ui/text-filtering)
- [TextFilterResult API](https://create.roblox.com/docs/reference/engine/classes/TextFilterResult)

Important requirements:
- Filter text after submission, not on every keystroke.
- If FilterStringAsync() fails, do not display the submitted text to anyone.
- Do not retry the filtering request yourself; the method implements internal retry handling.
- Use GetNonChatStringForBroadcastAsync() for non-chat text intended for everyone, or GetNonChatStringForUserAsync() for one recipient.
- Keep original unfiltered values out of public output, persistent displays, analytics, logs, and Codex reports.

## Prefer TextChatService for chat

Roblox's native TextChatService manages chat filtering, moderation, and user permissions. When platform-integrated chat is enabled, custom chat must use native systems and message content is not accessible to game scripts. Do not scrape, mirror, or attempt to recover platform-integrated chat contents.

- [Text chat overview](https://create.roblox.com/docs/chat/in-experience-text-chat)
- [TextChatService API](https://create.roblox.com/docs/reference/engine/classes/TextChatService)

Do not replace native chat filtering with a home-grown filter or client-side relay. Keep custom chat commands limited to documented actions and validate their arguments on the server.

## Run the V32 audit

    python .\v32\tools\v32.py doctor --root C:\Path\To\YourGame
    python .\v32\tools\v32.py audit --root C:\Path\To\YourGame

The bounded static audit counts visible TextService:FilterStringAsync() calls, flags legacy Chat:FilterStringAsync(), flags likely client-context TextService calls, and identifies a small set of raw-input variable names assigned to Text properties. The report contains file paths, line numbers, and fixed messages only; it never copies source lines or text values.

## Review every finding manually

A static match cannot prove that the filtered result is the exact value displayed. It cannot understand arbitrary Luau data flow, modules, metatables, dynamic names, or every custom UI sink. Confirm the value path and audience manually, then test in an authorized published test experience. A missing pattern match is not proof that all custom text is safe.
