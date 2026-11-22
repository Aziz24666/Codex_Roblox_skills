# Session checkpoint examples

Replace the toolkit and game project paths with the actual local paths.

## Initialize

    python "<toolkit-root>/v25/tools/v25.py" start --root "<game-project-root>" --goal "Build my Roblox game"

## After one verified stage

    python "<toolkit-root>/v25/tools/v25.py" checkpoint --root "<game-project-root>" --stage "Inventory persistence" --completed "Added schema validation and migration test" --next "Test reconnect and retry behavior" --test "Persistence unit tests: PASS" --file "src/Server/InventoryService.luau"

## Before ending a session

    python "<toolkit-root>/v25/tools/v25.py" handoff --root "<game-project-root>" --stage "Inventory persistence" --completed "Migration tests pass" --next "Run a Roblox Studio reconnect test"

## In a new session

    python "<toolkit-root>/v25/tools/v25.py" resume --root "<game-project-root>"

Paste the contents of .codex/session/RESUME_PROMPT.md into the new Codex conversation, then verify the source tree and Git state before proceeding.
