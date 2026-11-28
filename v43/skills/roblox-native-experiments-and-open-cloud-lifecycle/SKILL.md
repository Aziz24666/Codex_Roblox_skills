---
name: roblox-native-experiments-and-open-cloud-lifecycle
description: Use Roblox Creator Hub Experiments and the Open Cloud experimentation API safely, including scopes, async operation polling, immutable running plans, and human-approved completion.
---

# Roblox native experiments and Open Cloud lifecycle

## Prefer the native platform
Use Roblox Creator Hub Experiments for in-game config experiments. Roblox manages enrollment and variant assignment; do not invent a parallel client-side assignment system. An in-game experiment varies config values. Matchmaking experiments are a separate product type and are outside this skill's in-game plan validator. Roblox currently labels the Open Cloud experimentation endpoints Experimental; recheck the live API reference before automating production workflows.

In experience code, call `ConfigService:GetConfigForPlayerAsync(player)` to obtain the player-specific snapshot for an experiment key. `GetConfigAsync()` does not apply experiment assignments. Request the player-specific value only when needed, because the first `GetValue()` call enrolls the player. For experiments started after November 17, 2026, Roblox documents that an enrolled player's assignment persists across sessions and remains assigned even if the player later stops matching the targeting criteria.

## Open Cloud permissions and credentials
- Read/list/get/stats and calculateMde operations require the `universe:read` scope.
- Create/update/discard/start/schedule/complete operations require the `universe:write` scope.
- Keep API keys or OAuth credentials in a protected secret store or environment variable. Never commit them, paste them into a prompt, or put them in a config manifest.
- Separate read-only analysis from write operations. Require an authorized human to approve every write operation.

## Operation lifecycle
Mutating API operations are asynchronous. Capture the returned operationId and poll the operations endpoint until done is true. Handle structured operation errors and timeouts; do not assume a request succeeded merely because the initial POST returned successfully. Stats requests also resolve asynchronously.

A typical lifecycle is:
1. Create a draft experiment with a control and treatment value.
2. Verify the config key, variants, weights, exposure, duration, targeting, and goal metric.
3. Test the draft in the intended experience workflow.
4. Obtain explicit approval, then start or schedule.
5. Monitor stats and SRM state.
6. Complete only after the planned duration and a human decision. Omit the winning variantId to complete without selecting a winner.

After an experiment is scheduled, its configuration cannot be edited (it can be rescheduled). Once it is running, the config key and referenced global conditions are locked against changes until completion. Do not patch the running plan; create a new experiment for a new hypothesis.

## Results and roll-forward
- Fetch stats and check isSrmDetected.
- Review Creator Hub confidence intervals, sample counts, and metric movements.
- Complete with a treatment variantId only after review and approval; otherwise keep the control.
- Read back the resulting config and verify the intended permanent value.
- Record experiment ID, decision, reviewer, evidence, and date without copying player-level data.

## Boundaries
The V43 CLI is offline. It does not call Open Cloud, create operations, poll Roblox, start experiments, read results, complete experiments, or publish configs.
