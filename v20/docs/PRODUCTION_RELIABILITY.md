# V20 Production Reliability Contract

V20 adds a production-readiness layer to the cumulative V1–V19 toolkit. It makes important operational assumptions explicit before a feature is treated as release-ready. The contract is a review artifact, not proof that the design exists in a live Roblox place.

## Core invariants

1. **Server authority:** the server owns currency, inventory, progression, purchases, character-critical state, and other consequential state. Treat client input as a request, not an instruction.
2. **Explicit remote contracts:** keep an allowlist of client-to-server operations. Validate input shape and size, player ownership, context, distance where relevant, cooldowns, and per-player rate limits on the server. Unknown operations fail closed.
3. **Resilient persistence:** use an UpdateAsync-based write path, bounded retries with jitter, explicit load-failure behavior, schema versions, deterministic/idempotent migrations, and an owner-reviewed recovery procedure.
4. **Idempotent economy:** fulfill paid products from server-verified receipts, grant the exact configured product once, and preserve receipt/grant identifiers so duplicate delivery is harmless. The inherited V18 no-gambling policy remains mandatory.
5. **Safe rollout:** promote through development, staging, canary, and production. Use feature flags for reversible behavior changes, retain a kill switch, monitor promotion, and document a rollback that does not overwrite newer player data.
6. **Operational visibility:** track server errors, remote rejections, save failures, transaction failures, and latency. Alert on meaningful deviations, restrict dashboard access, and redact personal data and secrets from logs.

## Production contract file

Start with v20/examples/production-contract.example.json, copy it into the project's workflow/evidence area, and replace every placeholder with the real project values. Validate it with:

```bash
python v20/tools/v20.py validate-contract --root . --file path/to/production-contract.json
```

The validator checks JSON Schema and cross-field invariants: environment isolation, remote-operation uniqueness and server checks, idempotency for side effects, adjacent migration versions, the no-paid-random-rewards rule, fixed-grant identifiers, promotion order, kill-switch/rollback declarations, and minimum operational metrics.

The output is only a static contract-validation result. It does not connect to Roblox, inspect live configuration, test DataStore budgets, execute ProcessReceipt, verify a remote implementation, confirm a feature flag, or prove that an alert fired.

## Data and migration workflow

- Define the current profile schema and every supported migration edge.
- Migrations must be deterministic and idempotent. Run them against isolated fixtures, including a repeated execution, partial failures, and rollback/restore rehearsals.
- Use UpdateAsync transforms that tolerate retry/re-entry and avoid side effects inside a transform callback.
- Bound retries, use backoff and jitter, observe request budgets, and distinguish transient failure from invalid/corrupt data.
- Never replace an unavailable or unreadable profile with a fresh default and then save it over the existing key.
- Keep production data separate from Studio and CI test fixtures. Do not point tests at live stores by assumption.

## Economy and authority boundaries

- The client may display a price or request a purchase; the server owns eligibility, price/grant definitions, receipt state, and fulfillment.
- Never trust client-supplied currency deltas, inventory items, product prices, receipt status, or ownership assertions.
- Make each value-changing operation idempotent with a stable transaction/receipt identifier.
- Keep paid rewards deterministic and fixed. No paid random rewards, wagers, paid rerolls, or chance outcomes.
- Use server-side allowlists, schema checks, ownership/context checks, bounded payload sizes, and rate limits.

## Operational release checklist

- Confirm staging and canary use isolated test data.
- Confirm data-schema compatibility across the rollout window.
- Confirm feature flag owner and kill-switch operation.
- Capture baseline error, latency, save, transaction, and remote rejection metrics.
- Define promotion stop conditions and a rollback that preserves newer player writes.
- Record the release identity, approval, tested scenarios, and residual risks in V19 evidence packets.

## Official references

- DataStoreService: https://create.roblox.com/docs/cloud-services/data-stores
- DataStoreService API: https://create.roblox.com/docs/reference/engine/classes/DataStoreService
- UpdateAsync: https://create.roblox.com/docs/reference/engine/classes/GlobalDataStore#UpdateAsync
- MarketplaceService: https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
- ProcessReceipt: https://create.roblox.com/docs/reference/engine/classes/MarketplaceService#ProcessReceipt
- Remote events and callbacks: https://create.roblox.com/docs/scripting/events/remote
- Security tactics: https://create.roblox.com/docs/scripting/security/security-tactics
