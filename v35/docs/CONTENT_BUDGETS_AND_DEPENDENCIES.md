# V35 Content Budgets and Dependency Validation

## Budget policy

Copy v35/examples/asset-budget-policy.example.json into the project and set limits based on measured performance on the devices your experience supports. The included example numbers are illustrative project-policy values, not Roblox platform requirements.

Supported measurements:
- file_size_bytes
- texture_width_px multiplied by texture_height_px
- mesh_triangles
- audio_duration_seconds
- animation_keyframes

Policies can set per-profile maximums for low-end mobile, mobile, desktop, console, VR, or server targets. For each catalog asset, the audit evaluates only the profiles assigned to that asset. Missing measurements are warnings; an over-budget measurement is a blocker.

## Dependency graph

Dependencies point from the consuming asset to each required asset. Missing dependencies, self-dependencies, duplicates, and cycles are invalid. If an approved or released asset depends on a draft/review asset, the audit flags that readiness mismatch.

## Run an audit

    python .\v35\tools\v35.py audit-catalog --root C:\Path\To\YourGame --catalog .codex/assets/catalog.json --policy .codex/assets/budget-policy.json --output .codex/reports/v35-asset-audit.json
    python .\v35\tools\v35.py audit-catalog --root C:\Path\To\YourGame --catalog .codex/assets/catalog.json --policy .codex/assets/budget-policy.json --release-ready

The release-ready flag returns a non-zero exit code when blockers remain, including unresolved rights/review/ownership states on assets intended for release. Use the report as a review queue, not an automatic publishing decision.
