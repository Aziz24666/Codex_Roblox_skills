---
name: roblox-party-and-lobby-lifecycle
description: Design server-authoritative Roblox party invitations, membership, leadership transfer, lobby state, and atomic party queueing.
---

# Party and lobby lifecycle

## Goal
Create a party system whose membership, invitations, leader, queue ticket, and lobby transitions remain consistent through joins, leaves, disconnects, and server changes.

## State model
Model party lifecycle explicitly, for example: `forming -> ready -> queued -> assigned -> teleporting -> in_match`, with terminal or recovery states such as `disbanded`, `cancelled`, and `recovery_pending`. Every transition must be validated by one server authority and carry a monotonically increasing version. Reject transitions from stale versions.

Keep a clear distinction between:
- Party membership: which players belong to the party.
- Queue ticket: the atomic matchmaking unit representing the party.
- Match assignment: the server-claimed destination and match identity.
- Roblox platform party metadata: platform-provided party information where available; it is useful context, not a replacement for game-side authorization and consistency checks.

Where relevant, review Roblox's `Player.PartyId` and `SocialService:GetPlayersByPartyId()` APIs. Revalidate returned players, current server presence, experience rules, and party capacity before acting.

## Membership and invitation rules
- The server owns the party ID, roster, leader, capacity, membership version, and queue status.
- Validate that inviter and invitee are eligible, that the invitee is not already committed to another incompatible party, and that capacity is available.
- Use short-lived, opaque, one-use invitation references. Store invitation state server-side with an expiry; do not trust client-provided inviter, invitee, party ID, expiry, or acceptance status.
- Require explicit acceptance. Expire or revoke invitations on party disband, inviter permission change, membership conflict, or expiry.
- Rate-limit invitation creation and acceptance. Avoid revealing whether a player is online or otherwise exposing unnecessary account information.
- Keep membership mutations serialized. A concurrent accept/leave must not overfill a party or produce two leaders.

## Leader lifecycle
Define how the party leader can invite, kick (only where appropriate), queue, cancel, change mode, and transfer leadership. A leader leaving or disconnecting must trigger a deterministic transfer policy, such as the next eligible member by stable join order, or require explicit approval. If no eligible member remains, disband cleanly.

Do not make leadership depend on a client-side attribute, UI visibility, or a RemoteEvent argument. Every leader-only action rechecks current server-side leader identity and party version.

## Lobby and queue integration
- Represent a party queue entry as one indivisible ticket. Queue all currently eligible members or queue none.
- Lock or version-check party membership while a ticket is active. A member leaving during queueing must cause a server-side reconcile/cancel/update, never a partially updated ticket.
- Use idempotent queue/cancel operation IDs so retries do not duplicate tickets or remove a newer queue session.
- Before assignment, revalidate all members are still eligible and present/connected according to the product's join policy.
- On match assignment, freeze party roster changes or transition them through an explicit cancellation/recovery path.
- Keep UI as a projection of server state. Clients may optimistically show a pending action, but should reconcile to server-confirmed state.

## Disconnect and reconnect
Define grace-period behavior for a party member disconnecting in the lobby, while queued, during assignment, and during teleport. The policy may wait for rejoin, cancel the whole ticket, or remove that player before a new ticket is created. Never leave a stale member counted as present after the policy's grace period. Reconnect must verify a server-issued session/party reference and current membership version; client-supplied state is not authoritative.

## Required deliverables
- Party state machine, transitions, and version/fencing strategy.
- Server-owned party record and privacy-minimal invitation schema.
- Invitation acceptance, expiration, revocation, rate limiting, and capacity rules.
- Leader departure/transfer behavior.
- Atomic join/leave/queue/cancel/assignment behavior.
- Disconnect/rejoin policy for each lifecycle phase.
- Test matrix for concurrent invitations, simultaneous accept, leader departure, duplicate requests, full party, party disband, and queue-time disconnects.

## Non-negotiable safeguards
- Membership and invitations are checked server-side.
- Party queue tickets remain all-or-none; do not silently split groups.
- Repeated requests are idempotent and version checked.
- Do not expose private party state or invitation tokens through public messages or TeleportData.
- A party UI that looks correct is not evidence that server membership is correct.
