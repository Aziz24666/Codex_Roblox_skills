---
name: roblox-asset-catalog-and-dependency-governance-v35
description: Build and maintain a versioned Roblox asset catalog with stable keys, dependency validation, source mapping, and controlled lifecycle states.
---

# Roblox Asset Catalog and Dependency Governance

Create one reviewable inventory for game assets and relationships between them. Keep logical asset keys stable even when an uploaded asset ID or source file changes.

For each asset, record its stable key, content kind, source category, ownership scope (not a person's name), rights-review state, moderation-review state, lifecycle, semantic version, dependencies, target profiles, measured properties, and opaque evidence references.

Reject missing references, self-dependencies, duplicate edges, and cycles. Release a consumer only when each required dependency has an approved or released state. Review downstream consumers before removing or replacing a dependency. Prefer explicit version changes over silently reusing a key for different content.

Workflow:
1. Inventory experience assets and establish stable keys.
2. Classify assets by type and source.
3. Attach provenance and human review evidence references.
4. Map dependencies and target device profiles.
5. Run V35 validate-catalog and audit-catalog.
6. Compare the candidate catalog with the last release catalog.
7. Route blockers through the normal V30 release approval process.

V35 validates supplied metadata only. It does not enumerate live Roblox assets, infer dependencies from a binary model, or grant permissions. Keep private URLs, access tokens, player data, and personal reviewer details out of the manifest.
