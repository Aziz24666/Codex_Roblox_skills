# V36 — Accessibility, Responsive UI, and Localization Readiness

V36 adds four native Codex skills, an offline quality-manifest validator/auditor, three engineering guides, a JSON example, and regression tests.

## New capabilities
- Inventory player-facing surfaces and map platforms/input methods.
- Review focus navigation, text scaling, non-color cues, contrast, critical audio alternatives, and reduced-motion behavior.
- Track localization externalization, text expansion, and right-to-left review.
- Validate strict manifest fields and opaque evidence references.
- Generate a structured audit with blocker/warning counts.

## Commands
```powershell
python .\v36\tools\v36.py doctor --root C:\Path\To\YourGame
python .\v36\tools\v36.py validate-manifest --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json
python .\v36\tools\v36.py audit --root C:\Path\To\YourGame --manifest .codex\quality\manifest.json --output .codex\reports\v36-quality-audit.json
```

## Verification boundaries
Offline metadata validation only. The tool does not inspect Studio UI, evaluate screenshots, execute Luau, test real devices, or certify accessibility. Actual Studio/device testing and human review are required. No player health information or personal accessibility profiles are collected.
