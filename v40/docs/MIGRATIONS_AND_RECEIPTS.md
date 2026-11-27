# V40 migrations and idempotent transactions

## Profile migrations
- Maintain an explicit integer schema version inside each profile.
- Migrate one version step at a time with a known, bounded transformation.
- Require each migration to be idempotent: if a process is interrupted and retried, it must not apply a destructive transformation twice.
- Preserve unknown fields unless an explicitly reviewed migration removes them.
- Back up or snapshot the source data before production migration; test against copied fixtures and a separate test experience first.
- Dry-run on representative old-schema fixtures and record test-case identifiers.
- Keep a recovery strategy: restore a verified backup, apply a forward fix, or stop and require human intervention. Never silently downgrade a partially migrated profile.
- Do not mark a profile as current until the migrated value has been persisted successfully.

The V40 CLI checks the declared migration chain from the minimum supported schema version to the current version. It cannot evaluate migration code or prove the backup exists.

## Developer-product receipts
Roblox can deliver unresolved developer-product receipts again, and a specific receipt callback can run on two servers at the same time. The current Roblox player-data sample demonstrates checking PurchaseId, applying the reward and marker to the in-memory profile, saving that profile, and acknowledging only after the save succeeds. Its approach depends on session locking to prevent two servers from acting concurrently on stale profile data; review and test the sample rather than assuming it is production-certified. Use PurchaseId as the idempotency key. The receipt decision must reflect durable completion.

Preferred transaction boundary: perform the reward grant and its deduplication marker in the same UpdateAsync update to the same profile key. The transform checks whether PurchaseId is already recorded; if it is, it does not grant again. Otherwise it applies the reward and stores the marker in the same resulting profile value. Acknowledge only after that write is confirmed durable. If the write outcome is uncertain, reload and reconcile by PurchaseId rather than applying the grant blindly.

A receipt-marker array can grow for the lifetime of a profile. Never silently truncate it or evict IDs merely because they are old: a receipt can remain unresolved and be delivered again. Track serialized profile size and define a durable capacity/reconciliation plan before approaching the per-key limit. A separate receipt key and profile key cannot be assumed to form a cross-key atomic transaction. If the design requires multiple keys or services, define a recoverable state machine, reconciliation job, and manual support path; do not claim distributed atomicity. V40 deliberately reports this as a human-review warning and does not pretend to solve unbounded ledger growth.

Keep receipt logic in server Scripts. Use one deliberate receipt-routing strategy: legacy ProcessReceipt or the newer BindReceiptHandler API, with explicit ownership and coverage for all products. Never acknowledge an unknown product as fulfilled. A receipt returning NotProcessedYet remains unresolved for later delivery.

## Other rewards and exchanges
For gameplay rewards and inventory exchanges, create a server-generated stable operation ID before attempting the commit. The same operation ID must be used for retries. Store the deduplication marker and state mutation in one UpdateAsync transform when they share a profile key. Validate eligibility, amount, ownership, and rate limits on the server.

## Roblox references
- [Implement player data and purchasing systems](https://create.roblox.com/docs/cloud-services/data-stores/player-data-purchasing)
- [MarketplaceService and BindReceiptHandler / ProcessReceipt](https://create.roblox.com/docs/reference/engine/classes/MarketplaceService)
- [ReceiptDecision](https://create.roblox.com/docs/reference/engine/enums/ReceiptDecision)
- [Data store best practices](https://create.roblox.com/docs/cloud-services/data-stores/best-practices)
