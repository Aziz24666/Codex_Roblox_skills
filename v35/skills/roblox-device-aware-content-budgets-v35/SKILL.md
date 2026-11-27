---
name: roblox-device-aware-content-budgets-v35
description: Define and enforce project-specific per-device asset budgets for textures, meshes, audio, animation data, and source-file size.
---

# Roblox Device-Aware Content Budgets

Prevent content-heavy updates from silently exceeding the experience's target-device budgets. A single global limit is rarely suitable for every device tier.

V35 evaluates source-file size, texture width multiplied by height, mesh triangle count, audio duration, and animation keyframe count. Define explicit budgets for the supported target profiles. Choose limits from actual device testing, streaming behavior, loading requirements, and project performance targets; example numbers are not universal Roblox platform limits.

Measurement workflow:
1. Measure imported source files or inspect content in the appropriate authoring tools.
2. Record the measurement source and evidence outside the manifest where detailed logs are stored.
3. Declare target profiles for each asset.
4. Run audit-catalog using a reviewed budget policy.
5. Investigate missing measurements and budget overruns before release.
6. Re-test representative low-end devices after content changes.

Use texture atlases only when they improve the project's measured memory and draw-call profile. Reduce unnecessary mesh detail, avoid oversized textures, compress or trim audio where appropriate, and preserve readability, accessibility, and gameplay clarity.

V35 checks numeric metadata against project policy; it does not inspect binary assets or benchmark device performance.
