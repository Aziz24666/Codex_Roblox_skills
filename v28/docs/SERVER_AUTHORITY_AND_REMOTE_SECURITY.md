# Server Authority and Remote Security Review

## Core rule

A client can request an action; it cannot certify that the action is allowed or that a claimed result is true. Treat every RemoteEvent and RemoteFunction argument as untrusted, even when the normal game client sends it.

The server should independently determine the player identity from the event parameter and verify relevant game state. For high-impact actions, validate argument types, finite numeric values, bounds, allowed enum values, instance class and ancestry, ownership, permissions, cooldowns, and whether the action is currently possible. Reject malformed requests without partially applying state changes.

## Server-authoritative state

The server owns currency balances, inventory, item ownership, damage, health changes, rewards, progression, purchases, match outcomes, and persistent data. Do not accept a client-provided balance, price, reward amount, damage result, ownership claim, or "purchase succeeded" flag as authoritative.

Prefer narrow remote contracts. Define the exact arguments, types, limits, and response behavior. Use server-owned identifiers and lookup tables rather than trusting arbitrary client-supplied Instances or names. Validate objects against the expected service/container and expected class; an object existing in the DataModel does not prove that a player may use it.

For combat and interactions, the server should verify distance, line-of-sight or other relevant conditions, equipped state, cooldown, match state, and target eligibility using server-observed information. Keep client-side prediction cosmetic and reconcile it with server-approved state.

## Frequency and duplicate handling

Rate-limit per player and per action on the server. Use bounded request windows or cooldowns appropriate to the mechanic; avoid unbounded tables and expensive work before throttling. A client-side debounce improves UX but is not a security boundary.

For operations that may be retried, time out, or be delivered more than once, define idempotency. Use a server-controlled request/receipt identity and persist the processed state atomically where needed. Do not trust a client-generated request identifier by itself as authorization. Ensure a duplicate request cannot grant a reward, spend currency twice, or apply an irreversible transition twice.

## Review checklist

- [ ] Every client-to-server remote has a documented contract and server handler.
- [ ] The handler derives the player from Roblox's server event parameter, not a client-supplied player argument.
- [ ] Types, numeric finiteness, bounds, enums, strings, Instances, and collection sizes are validated.
- [ ] Ownership, permissions, range, match state, and action preconditions are checked server-side.
- [ ] High-impact operations calculate the result on the server.
- [ ] Requests are rate-limited before expensive or stateful work.
- [ ] Retries and duplicate delivery cannot duplicate rewards, purchases, or state transitions.
- [ ] Errors do not leak sensitive server details and rejected requests do not partially mutate state.
- [ ] Studio tests cover valid, malformed, unauthorized, out-of-range, rapid, and repeated requests.

## V28 report interpretation

V28 identifies statically named remote calls and handlers and searches a bounded text window near each handler for token-level signals such as type checks, ownership checks, cooldowns, and idempotency. These signals can be missed or matched in unrelated nearby code. A reported signal is not proof of correctness; an absent signal is not proof of a vulnerability. Review the full handler and its call graph in Studio.
