# V45 CLI reference

The V45 tool is an offline structural validator for quest and dialogue metadata and uses only the Python standard library at runtime.

```powershell
python .\v45\tools\v45.py doctor --root C:\Path\To\YourGame
python .\v45\tools\v45.py validate --root C:\Path\To\YourGame --project .codex\narrative\narrative-project.json
python .\v45\tools\v45.py audit --root C:\Path\To\YourGame --project .codex\narrative\narrative-project.json --output .codex\reports\narrative-audit.json
```

Checks include strict fields and bounded collections; stable IDs; unique localization keys; supported locales; existing acyclic prerequisites; quest edge validity, reachability, acyclic progression, and completion paths; dialogue destination validity, reachability, and ending paths. Dialogue loops are permitted only when every node can still reach an ending.

Input is capped at 2 MiB. Duplicate JSON keys, non-standard constants, traversal, and symlink paths are rejected. Reports are written atomically.

The CLI does not inspect Luau, invoke Studio, contact Roblox, read profiles, validate translations, perform moderation, prove server authority, run playtests, or approve releases. Human review remains required.
