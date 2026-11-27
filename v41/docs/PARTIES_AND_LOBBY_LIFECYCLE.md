# Party and lobby lifecycle

## State model

Use a server-owned party record with a stable party ID, leader reference, member roster, capacity, membership version, current mode, queue ticket reference, and lifecycle state. Example lifecycle:

`forming -> ready -> queued -> assigned -> teleporting -> in_match`

Recovery or exit states include `cancelled`, `recovery_pending`, and `disbanded`. Every transition checks the expected prior state and version. The UI is only a projection of this server-owned model.

## Invitations

An invite is a short-lived server-side record with a random opaque reference, inviter, intended invitee, party version, expiry, and status. Acceptance must be explicit and revalidate:

- The inviting player is still authorized to invite.
- The invitee is the intended recipient and still eligible.
- The invite has not expired, been accepted, or been revoked.
- The party has capacity and its current version matches the invitation.
- The invitee is not already committed to an incompatible party or match.

Rate-limit sends/accepts. Do not trust a client to provide invitation expiry, sender, party membership, or capacity. Never expose invite references in cross-server public messages or TeleportData.

## Leadership

Pick a deterministic transfer policy for leader leave/disconnect (for example, the next eligible member by stable join order) or require explicit human confirmation. Re-check the leader on every privileged action. Do not let the UI or a client attribute decide who owns the party.

## Queue integration

A party is one indivisible matchmaking ticket. Freeze membership while queued/assigned, or require an explicit cancel-and-reissue operation that advances the membership version. A partial party must never be enqueued because one member's join/leave request raced another. Make queue/cancel operations idempotent so retries cannot create duplicate tickets or cancel a later queue session.

At each stage—enqueue, dequeue, match claim, teleport, and destination arrival—revalidate party roster and membership version. A party member's disconnect requires a documented grace/cancel policy for each stage. Once a party is assigned, do not let a client silently move one member to another match.

## Platform party APIs

When relevant, evaluate Roblox's `Player.PartyId` and `SocialService:GetPlayersByPartyId()` APIs. These can inform platform party grouping, but your experience should still validate its own eligibility, limits, membership rules, and current server/player state. Do not substitute platform metadata for your own authoritative match assignment.

## Minimum test matrix

- Invite expiry and duplicate accept.
- Two concurrent invitations consuming the final slot.
- Party full at acceptance time.
- Leader leaves/disconnects while party is queued.
- Member leaves while a queue request is in flight.
- Two simultaneous queue requests for the same party.
- Cancel racing with match assignment.
- Member reconnect during lobby grace period and after expiry.
- Destination rejects stale party membership version.

## Official Roblox references

- [SocialService API reference](https://create.roblox.com/docs/reference/engine/classes/SocialService).
- [Player API reference](https://create.roblox.com/docs/reference/engine/classes/Player) — review the current party-related properties and events before integrating platform party metadata.
