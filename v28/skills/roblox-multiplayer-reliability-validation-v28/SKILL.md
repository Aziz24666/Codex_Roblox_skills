---
name: roblox-multiplayer-reliability-validation-v28
description: Build evidence-based Roblox Studio multiplayer, latency, duplicate-request, persistence, migration, and regression test plans.
---

# Roblox Multiplayer Reliability Validation

## Goal

Create repeatable, evidence-first test coverage for multiplayer game systems using private places and synthetic state.

## Workflow

1. Identify the system boundary, expected server-owned state, and measurable success/rejection outcomes.
2. Reuse V26 Studio MCP test planning and add V28 security cases: malformed arguments, ownership denial, wrong match phase, cooldown, simultaneous requests, and duplicate delivery.
3. Cover one, two, four, and up to eight clients where practical; include relevant desktop/mobile/controller profiles.
4. Vary latency, jitter, packet loss, disconnect, reconnect, and timing between request and acknowledgement.
5. Test persistence during rejoin, concurrent servers, transient failures, throttling, shutdown, and retry.
6. Run migration tests only with synthetic fixtures or a staging environment whose isolation has been confirmed.
7. Capture server/client logs, source revision, Studio place/version, test conditions, and expected versus actual state.
8. Repeat fixed scenarios after code changes and preserve regression evidence.
9. Clearly mark tests as planned, executed, passed, failed, blocked, or not applicable. Never report a plan as an executed test.

## Safety boundaries

Do not automate production DataStore writes, publishing, player-impacting cloud calls, or live-game manipulation. Require explicit human approval for irreversible actions and keep all ordinary automation read-only.
