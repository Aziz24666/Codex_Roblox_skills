# V18 Package Integrity

V18 uses three current manifests to preserve the inherited V14 package-doctor contract:

- `SHA256SUMS.txt` excludes itself, `V14_SHA256SUMS.txt`, and `V18_SHA256SUMS.txt`.
- `V18_SHA256SUMS.txt` includes the root manifest and excludes itself plus `V14_SHA256SUMS.txt`.
- `V14_SHA256SUMS.txt` covers every package file except itself, including root and V18 manifests.

Generate in order: root, V18, V14. V15, V16, and V17 manifests remain historical release snapshots. Verify: `sha256sum --check SHA256SUMS.txt`, then `V18_SHA256SUMS.txt`, then `V14_SHA256SUMS.txt`.

Run all source validators and tests before finalizing manifests. Remove generated caches, regenerate inventory/manifests, run the cumulative audit, and only then create archives.
