---
name: roblox-idempotent-rewards-and-receipt-processing
description: Design deduplicated server-side rewards and developer-product receipt handling that is safe under retries and concurrent delivery.
---

# Roblox idempotent rewards and receipt processing

## Developer-product receipts
- Use PurchaseId as the durable idempotency key.
- Expect unresolved receipts to be delivered again and a receipt callback to overlap across servers.
- Check and write the deduplication marker inside the same UpdateAsync operation that applies the profile reward whenever both belong to one profile key.
- Acknowledge only after the durable profile update is confirmed.
- If the outcome is uncertain, reload and reconcile by PurchaseId. Never blindly grant again.
- Select and document a single intentional receipt routing strategy: ProcessReceipt or BindReceiptHandler. Ensure every developer product is handled and unknown products are not acknowledged as fulfilled.

## Gameplay rewards and exchanges
- Generate an operation ID server-side before attempting the mutation.
- Reuse the exact ID on retries.
- Validate eligibility, quantities, ownership, and cooldowns on the server.
- Keep the state mutation and deduplication marker in one UpdateAsync transform when they share a key.
- Define recovery when a transaction spans multiple keys; DataStore operations do not provide assumed cross-key atomicity.

## Test matrix
Cover duplicate callbacks, callbacks on two servers, duplicate remotes, retries after ambiguous writes, invalid products, out-of-order receipts, player disconnects, and shutdown during commit.

## Guardrails
Keep the outcome fixed and disclosed. Do not create paid random outcomes, gambling, loot boxes, or wagering systems. This skill is about reliable transaction processing, not purchase pressure.
