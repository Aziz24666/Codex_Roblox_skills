# V42 CLI reference

All paths are relative to the selected Roblox project root. Run with Python 3.10 or newer.

## Commands

~~~powershell
python .\v42\tools\v42.py doctor --root C:\Path\To\YourGame
python .\v42\tools\v42.py validate --root C:\Path\To\YourGame --model .codex\liveops\liveops-model.json
python .\v42\tools\v42.py audit --root C:\Path\To\YourGame --model .codex\liveops\liveops-model.json --output .codex\reports\liveops-audit.json
python .\v42\tools\v42.py compare --root C:\Path\To\YourGame --baseline .codex\liveops\baseline.json --candidate .codex\liveops\candidate.json --output .codex\reports\config-compatibility.json
~~~

## Results and exit codes

- validate: validates config key types and values, repository limits, conditional targeting counts, event schedule windows, config references, staging/publish gates, rollback behavior, and consumer contracts.
- audit: writes a deterministic design report with summary, warnings, and limitations.
- compare: writes a baseline/candidate report; removed keys and type changes are breaking. Default-value and event changes require review.
- 0: successful command and no blocking compatibility result.
- 1: model invalid or comparison found breaking config changes.
- 2: path, input, or runtime error.

## Safeguards

Input must be valid UTF-8 JSON no larger than 1 MiB. Duplicate keys and non-standard constants such as NaN are rejected. Input and output paths must be project-relative; absolute paths, parent traversal, backslashes, and symlink traversal are rejected. Reports are written atomically.

The tool is offline. It does not inspect Luau, call ConfigService or Open Cloud, stage/publish/restore config, schedule a live event, inspect telemetry, or prove a live rollback. A compatibility report cannot discover dynamic key names or string-built references. Do not treat a green audit as production approval.
