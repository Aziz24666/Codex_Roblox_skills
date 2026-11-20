# Package Integrity and Checksum Manifest Policy

## Current release manifests

The current cumulative package ships three active integrity manifests:

- `SHA256SUMS.txt` covers current package files except the three current manifest files.
- `V15_SHA256SUMS.txt` covers the package except itself and the V14 manifest; it includes the generic root manifest.
- `V14_SHA256SUMS.txt` covers every package file except itself, including the root and V15 manifests. This preserves the inherited V14 package-doctor contract.

This dependency order avoids circular checksums. Verify the current package from its root with:

```sh
sha256sum --check SHA256SUMS.txt
sha256sum --check V14_SHA256SUMS.txt
sha256sum --check V15_SHA256SUMS.txt
```

The package integration tool regenerates all three manifests in dependency order only after documentation, inventory, skills, schemas, and examples are finalized.

## Historical manifests

`V6_SHA256SUMS.txt` through `V13_SHA256SUMS.txt`, including the archived V10 snapshot, are historical version snapshots. They describe earlier package trees and are not expected to verify against a later cumulative release after files have been added or revised. Do not use them to verify the current V15 package.

## Continuous verification

The cumulative package audit checks manifest coverage, rejects missing or extra entries and hash mismatches, parses every installed skill's YAML frontmatter, validates all JSON and JSON Schemas, checks the V9 descriptor collection against its collection schema, parses Python/TOML/YAML/CSV source files, checks local Markdown targets, and rejects empty files and generated Python caches.

Archive integrity, Luau compilation, Rojo builds, and Roblox Studio runtime testing remain separate evidence classes. Passing the package audit does not prove that Roblox Studio playtests or live services were executed.
