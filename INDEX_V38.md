# Roblox Codex Game Studio Kit — V38

V38.0.0 is the cumulative V1–V38 package with **256 native Codex skills**. Only this current cumulative release is required.

## V38 additions
- Production incident triage and severity assessment.
- Privacy-safe service health and aggregate impact analysis.
- Human-approved mitigation, rollback, and recovery gates.
- Player communication, verified closure, and blameless postmortem readiness.
- Offline incident-record validation and audit, strict JSON Schema, example, docs, and regression tests.

## Commands
```powershell
python .\v38\tools\v38.py doctor --root C:\Path\To\YourGame
python .\v38\tools\v38.py validate --root C:\Path\To\YourGame --incident .codex\incidents\incident.json
python .\v38\tools\v38.py audit --root C:\Path\To\YourGame --incident .codex\incidents\incident.json --output .codex\reports\incident-audit.json
```

## Boundaries
The CLI validates supplied metadata only. It does not inspect Roblox telemetry, authenticate references, perform mitigation or rollback, restore data, or send player notices. Privacy attestations are not PII detection. A successful audit is not approval to perform live operations.
