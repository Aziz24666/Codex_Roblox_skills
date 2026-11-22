# V25.0.1 — Toolkit Audit and Reliability Fixes

V25.0.1 is a maintenance release that hardens the V25 continuity CLI, fixes V23 project-scanning boundaries, expands regression coverage, and refreshes Roblox platform guidance from current official documentation.

## Reliability fixes
- Bind every checkpoint/status/resume/recovery operation to the canonical project root recorded by the session.
- Validate checkpoint fields, list sizes, status, counters, and credential-like values when loading saved state.
- Make stale-lock handling process-aware so a live writer is not displaced solely because a lock is old.
- Validate complete event-journal record shapes, sequence numbers, hashes, and checkpoint references; detect checkpoints missing from the journal.
- Make recovery refresh the resume prompt and add a recovery event when the journal remains writable.
- Handle malformed complete journal records as a clear validation error rather than an uncaught attribute error.
- Reject unsafe session-file paths that resolve outside the selected project directory.

## V23 scanner fixes
- Exclude toolkit versions V18-V25, local .codex session data, generated reports, and build/cache directories from project scans.
- Skip symlinked files and files resolved outside the selected project root.
- Validate opportunity-catalogue field types, identifiers, and deterministic-outcome requirements before ranking.
- Validate routing-corpus entries and restrict generated report paths to the chosen project root.
- Preserve the V24 `exclude_paths` parameter contract so the updated scanner remains compatible with the V24 growth pipeline.
- Add regression tests for symlinks, excluded metadata, output traversal, and malformed catalogue entries.

## Documentation and validation
- Refresh product-intelligence API limits and current Creator Rewards eligibility details from official Roblox Creator Hub documentation.
- Replace outdated OpenAI skills/customization documentation links with current official references.
- Add a repository-wide package audit for Python syntax, JSON validity, Markdown links, and skill metadata.
- Expand cumulative CI regression checks while retaining prior V1-V24 quality gates.

## Compatibility
- This is a V25 maintenance release. Existing V1-V24 skills and fair-monetization/no-gambling requirements are preserved.
- Checkpoint schema remains version 1; existing V25.0.0 checkpoint files remain readable.
