# V35 Asset Release and Migration

## Compare a candidate catalog

Keep the last released catalog as an immutable baseline. Create a candidate catalog with versioned changes, then run:

    python .\v35\tools\v35.py compare-catalogs --root C:\Path\To\YourGame --baseline .codex/assets/catalog-v1.json --candidate .codex/assets/catalog-v2.json --output .codex/reports/v35-asset-diff.json

The comparison reports added, removed, and changed assets. It highlights regressions in rights state, moderation state, lifecycle, and removal of dependencies still referenced by candidate assets.

## Release process

1. Validate the catalog and run the policy audit.
2. Review every blocker and warning with the responsible asset owner.
3. Verify actual asset permissions and availability through authorized Roblox workflows.
4. Test content loading, rendering, audio, animation, streaming, and device tiers in Studio.
5. Add the asset diff and evidence references to the V30 release dossier.
6. Approve promotion and rollback explicitly; retain the previous references until migration is complete.

## Boundaries

The tool is fully offline. It does not upload, publish, delete, transfer, or alter assets; does not read Creator Store pages or private inventory; and does not establish copyright ownership or license scope. Do not infer production readiness from a passing JSON validator alone.
