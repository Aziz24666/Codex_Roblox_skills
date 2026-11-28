---
name: roblox-live-event-lifecycle-and-scheduling
description: Plan timezone-safe Roblox live events with explicit lifecycle states, idempotent activation, preflight checks, and cleanup.
---

# Roblox live event lifecycle and scheduling

## Goal
Design events that start and end predictably across servers, survive server restarts, and can be disabled or recovered without duplicating rewards or leaving stale content active.

## Event manifest
- Give each event a stable lowercase event ID and a schedule group.
- Store start and end timestamps with an explicit UTC offset. Prefer UTC ISO 8601 in shared manifests; never use a naive local timestamp or assume every server has the same local timezone.
- Define the config keys that control the event, including one boolean enable flag.
- Define test cases for staged, scheduled, and active events.
- Prevent overlapping event windows in the same mutually exclusive schedule group unless a human deliberately changes the group design and reviews the overlap.
- Keep event content, rewards, and schedule separately versioned so a content update does not silently rewrite the event identity.

## Lifecycle state machine
Use an explicit server-authoritative lifecycle such as planned → staged → scheduled → active → completed, with cancelled and rollback paths. Every transition should be idempotent. Re-running a scheduler after a server restart must not double-grant participation rewards, reopen a completed event, or execute a start action twice.

## Runtime behavior
- Use experience configs to gate event availability; read them with server-side ConfigService.
- Compare the server's current UTC time to the event window and validate the current config snapshot before activating.
- Treat a missing config as disabled or apply the documented static fallback. Do not assume a config lookup always returns a value.
- Apply updates at a safe event boundary. Do not change encounter rules or reward multipliers halfway through an active round unless the design explicitly supports that behavior.
- Make start, tick, end, reward settlement, and cleanup operations independently idempotent.
- When a server starts mid-event, reconcile the authoritative event state before enabling event content.

## Failure and operations
Define behavior for config load failure, stale snapshots, delayed publication, server restarts, schedule overlap, event cancellation, expired content, and partial cleanup. Keep the last known good snapshot only when the runtime has a bounded and reviewed policy; otherwise use safe static defaults.

## Required deliverables
- Event manifest with timezone-aware timestamps.
- Lifecycle state transition diagram and idempotency keys.
- Schedule-conflict checks and test-case matrix.
- Start/end/restart/cancellation behavior.
- Human-reviewed rollout and cleanup plan.

## Non-negotiable safeguards
- Server-authoritative event state and reward grants.
- Explicit timezone-aware timestamps.
- Idempotent event transitions and reward settlement.
- Safe fallback when configuration is absent or unavailable.
- No unreviewed production schedule mutation.
