# V18 Luau Teaching Examples

These examples demonstrate bounded implementation patterns. They are not drop-in production services. Adapt them to the existing project's contracts, persistent data layer, and current Roblox APIs; run Luau analysis and Roblox Studio tests before shipping.

## Remote request validation

`RemoteRequestValidation.server.luau` demonstrates a server-authoritative collectible request:

- The client sends an action ID, a unique request ID, and a target instance. It does not send a reward amount.
- The server applies a per-player request rate limit and a bounded request-ID replay guard.
- The server checks the target's type, Workspace ancestry, CollectionService tag, availability attribute, living character, and distance.
- The server checks per-player collection state and cooldown, then calculates a fixed reward locally.
- Player request state is cleaned up when the player leaves.

### Setup

1. Create `ReplicatedStorage/Remotes` as a Folder.
2. Add RemoteEvents named `RequestAction` and `ActionResult`.
3. Tag the collectible BaseParts with the `SampleCollectible` CollectionService tag.
4. Place the server script in `ServerScriptService`.
5. Have the client create a fresh 8–64 character request ID for each request and listen to `ActionResult`.

The example's `leaderstats.SampleCoins` value is in-memory demonstration state and is not persisted. Replace it with the project's existing server-owned, idempotent persistence/economy service before using it in a live experience. Do not trust a client-supplied amount, reward, ownership flag, or completion claim.
