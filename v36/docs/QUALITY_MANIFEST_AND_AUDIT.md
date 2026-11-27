# V36 Quality Manifest and Audit

Create a project-local manifest from `v36/examples/quality-manifest.example.json`.

Run:

```powershell
python .\v36\tools\v36.py doctor --root C:\Path\To\YourGame
python .\v36\tools\v36.py validate-manifest --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json
python .\v36\tools\v36.py audit --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json --output .codex\reports\v36-quality-audit.json
```

The manifest has a strict schema. Each surface records its target platforms, input methods, localization readiness, accessibility checks, and opaque evidence references. Unknown fields are rejected to reduce accidental data collection.

The audit reports missing capabilities as warnings and release-critical gaps as blockers. It is a review aid, not a Roblox platform certification or substitute for Studio/device testing.
