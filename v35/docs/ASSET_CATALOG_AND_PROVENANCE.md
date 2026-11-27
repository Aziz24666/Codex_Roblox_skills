# V35 Asset Catalog and Provenance

## What V35 adds

V35 introduces a bounded, versioned asset catalog for content used by a Roblox experience. It connects stable internal asset keys to content kind, source category, ownership scope, human-reviewed rights and moderation states, lifecycle, version, dependencies, target devices, measurements, and opaque evidence references.

The catalog is a project-maintained inventory. It is not a live query of Roblox inventory or Creator Store state.

## Create a catalog

Copy v35/examples/asset-catalog.example.json into the game project, then replace the demonstration values with reviewed records. Unknown fields are rejected so private player data, tokens, notes, or accidental personal information cannot silently enter the catalog.

Each asset needs a unique stable key and an opaque provenance reference. A local source asset additionally needs a safe, project-relative source path. The CLI rejects absolute paths, parent-directory traversal, symlink traversal, and non-file paths. Where a file-size measurement is supplied for a local file, it must match the file's actual byte size.

## Provenance and review

Use source_kind to distinguish local source files, Studio-created assets, Creator Store content, and other external sources. Record only the ownership scope (group, account, third_party, or unknown), not personal names or account IDs.

Rights clearance and Roblox moderation review are separate human-reviewed states. Cleared is an assertion that an authorized reviewer checked the specific applicable permission basis; it is not something the validator can determine. Keep review documents in authorized storage and use opaque ev- references in the catalog.

Run:

    python .\v35\tools\v35.py validate-catalog --root C:\Path\To\YourGame --catalog .codex/assets/catalog.json

The validator checks metadata shape, unique keys, enumerations, bounded values, local path safety, dependency references, and dependency cycles. It does not inspect binary FBX/PNG/OGG/RBXM content or contact Roblox services.
