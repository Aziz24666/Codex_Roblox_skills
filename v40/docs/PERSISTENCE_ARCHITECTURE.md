# V40 persistence architecture

V40 models a server-authoritative player-profile contract. Keep the number of stores and keys modest. When related state must change atomically, co-locate it in one profile key while the payload comfortably fits within Roblox's per-key limit. Use a fixed store name/scope and a deterministic user-key strategy; never put raw player data into the model file.

## Profile lifecycle
1. On join, acquire an exclusive session lease using an UpdateAsync transform and a unique server-session owner token.
2. If ownership is held elsewhere, wait or fail closed. Never load a second writable copy after an ambiguous load/lock error.
3. Keep the active profile in memory. Validate server-side requests and mutate in-memory state through one controlled profile service.
4. Periodically refresh the lease and autosave with per-player staggering to avoid synchronized write bursts.
5. Serialize writes for the same key. A delayed retry must not overwrite a newer save.
6. On player removal, save the latest state and release only the lock owned by that session.
7. On shutdown, flush bounded saves in parallel within the available shutdown window, then stop cleanly.

## UpdateAsync and retries
Use UpdateAsync where multiple servers can contend for the same key or where a mutation depends on its current value. Its callback must be pure and non-yielding. Protect network calls with pcall. Retry only transient failures, with bounded exponential backoff and jitter. Avoid retrying validation/permission errors. A failed client response can mean the server does not know whether the backend committed; reload and reconcile before replaying a mutation. Keep retry order per key.

UpdateAsync consumes both read and write budgets. Track request budgets and avoid avoidable read/write loops. Keep payload size and per-key throughput in mind. Do not pre-compress serialized profile data; Roblox data stores compress stored values automatically.

## Session locks
A lock is a lease, not an eternal boolean. Store a unique owner token and expiry/renewal information. Acquire, renew, and release through a concurrency-safe per-key update. A new server must not steal an unexpired lock. Release must verify the owner token so an old server cannot clear a newer server's lock. Define stale-lease recovery, clock assumptions, and failure handling explicitly. Never permit two active writers because data loading or lock acquisition returned an uncertain result.

## Shutdown
Use PlayerRemoving for normal departures and BindToClose for server shutdown. Roblox documents a 30-second wait for BindToClose callbacks, so reserve time for scheduling and network variability; V40 caps the declared persistence flush budget at 25 seconds. Save eligible profiles concurrently with bounded per-key queues. Do not start unbounded retries during shutdown.

## Payload and request budgets
Roblox currently documents a 4,194,304-character maximum for a DataStore key value. Keep a conservative application budget below this limit and measure serialized JSON size in Luau before writes. UpdateAsync counts against both read and write request budgets. Design autosave intervals, staggering, write coalescing, and payload size from observed aggregate usage rather than assuming the nominal limit is always available.

## Privacy and environment isolation
Persist only game state required for the experience. Do not store chat transcripts, contact details, credentials, or unnecessary personal data in player profiles. Studio DataStore API access can target the same stores as the live experience; use a separate test experience/store scope and test accounts for migration and failure testing.

## Official references
- [Data store best practices](https://create.roblox.com/docs/cloud-services/data-stores/best-practices)
- [Data store limits and errors](https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits)
- [Data stores overview](https://create.roblox.com/docs/cloud-services/data-stores)
- [DataModel:BindToClose](https://create.roblox.com/docs/reference/engine/classes/DataModel)
