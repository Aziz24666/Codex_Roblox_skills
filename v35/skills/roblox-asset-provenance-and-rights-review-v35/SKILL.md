---
name: roblox-asset-provenance-and-rights-review-v35
description: Establish traceable asset provenance and human-reviewed ownership, license, Creator Store, and moderation evidence before Roblox content is shipped.
---

# Roblox Asset Provenance and Rights Review

Make the origin and review state of every shipped asset traceable. A catalog entry is not proof of ownership, a license, or permission to redistribute content.

Review each source:
- Team-created: identify the project/team source and keep creation evidence in approved project storage.
- Creator Store: review the applicable creator terms, asset permissions, attribution requirements, and restrictions for the specific asset.
- Third-party: record the actual license/permission basis and confirm it covers intended use and distribution.
- Studio-created: distinguish original work from imported or modified source content.

Use an opaque evidence reference and a project-maintained review state. Record ownership scope as group, account, third_party, or unknown; never put a real person's name, email, or private account identifier into the catalog. Mark rights as cleared only after an authorized human reviewer verifies the applicable source and usage rights. Track Roblox moderation review separately from ownership review.

Do not ship assets with unknown, pending, or restricted rights. Do not equate successful upload or Roblox moderation acceptance with legal rights clearance. Re-check permissions when source terms, ownership, license versions, or distribution plans change.

The V35 validator checks structure and supplied assertions. It cannot determine whether a license is valid, whether a Creator Store item permits a particular use, or whether an asset is currently approved by Roblox.
