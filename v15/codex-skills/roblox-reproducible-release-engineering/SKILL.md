---
name: roblox-reproducible-release-engineering
description: Audit Roblox toolkit or game-project release pipelines for pinned tools, deterministic builds, artifact integrity, least privilege, traceability, and truthful release notes.
---

# Roblox Reproducible Release Engineering

## When to use
Use when creating or changing CI, packaging project/plugin assets, producing release archives, calculating checksums, or preparing a versioned GitHub release.

## Procedure
1. Confirm the target commit, version source, release tag naming, package root, and expected release files.
2. Inspect workflow triggers, branch/path filters, permissions, third-party actions, secrets exposure, and publish conditions.
3. Keep pull-request validation read-only. Give write permissions only to the release job, gated on the intended branch, explicit marker, and successful validation/packaging jobs.
4. Pin third-party actions by full commit SHA and toolchain binaries by version plus verified digest.
5. Reconstruct from source inputs in a clean directory. Verify every compressed overlay/archive before extraction.
6. Build both supported archive formats from the same package tree.
7. Run archive integrity checks, compare extracted file paths and hashes between formats, and reject missing/extra files.
8. Generate a per-file SHA-256 manifest after package documentation and inventory are finalized. Verify every manifest entry.
9. Make release notes state exactly which checks ran and which did not. Never imply CI launched Studio unless it did.
10. Create a new release tag only after checks succeed. Never overwrite a published version; use a new patch version for corrections.
11. Preserve source/run identity and publish assets created by the same successful workflow run.

## Stop conditions
- Missing source archive, failed checksum, unpinned critical tool, missing package file, or failing test blocks release.
- Do not publish, deploy, or mutate an external project unless the user explicitly authorized it.
- Never store or print credentials, cookies, tokens, or live-service secrets.

## Output contract
Report commit/tag, workflow run, job results, package file count, archive sizes and digests, integrity checks, release links, and all runtime tests not performed.
