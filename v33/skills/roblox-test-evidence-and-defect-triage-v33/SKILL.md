---
name: roblox-test-evidence-and-defect-triage-v33
description: Produce privacy-minimal, reproducible Roblox QA reports, validate complete test coverage, compare baselines, and triage defects by player impact and reproducibility.
---

# Roblox Test Evidence and Defect Triage

## Purpose

Turn test execution into a trustworthy engineering decision. A report must distinguish passed, failed, blocked, and not-run cases and preserve enough context to reproduce a defect without collecting unnecessary player information.

## Required report fields

Use the V33 test-report schema and CLI. A report contains a suite ID, opaque run reference, timezone-aware timestamps, a bounded environment snapshot, and exactly one result for each test in the plan. Each result contains a test ID, fixed status/outcome code, optional opaque evidence reference, and execution timestamp where applicable.

Allowed report data is intentionally narrow. Do not add user IDs, usernames, raw chat, voice recordings, purchase details, session tokens, private server identifiers, credentials, screenshots of player conversations, arbitrary notes, or full log dumps. Keep original evidence in an authorized project system and point to it only by an opaque reference.

## Defect triage

Prioritize by:

1. Player impact and whether game-critical state can be lost or corrupted.
2. Reproducibility and frequency across supported environments.
3. Whether the issue crosses a trust boundary, affects player safety, or exposes private data.
4. Whether the defect blocks core progression or prevents a player from joining, playing, saving, or leaving cleanly.
5. Whether a recent change introduced the issue compared with a known passing baseline.

Treat security, data integrity, and player-safety regressions as release blockers until reviewed. Do not use report counts as automatic moderation decisions or as a reason to punish users.

## Baseline comparison

Compare only reports from the same suite ID and plan. A baseline-pass/current-fail case is a regression. A baseline-pass/current-blocked case is newly blocked and needs re-execution. A baseline-pass/current-not_run case is a coverage gap, not a passing test. A non-passing baseline that now passes is an improvement, but it does not prove all other tests pass.

Fix the root cause and add a regression test before closing a reproducible defect. Re-run the affected scenario and the relevant surrounding flows.

## Honest verification labels

Use explicit labels such as static audit, Python unit tests, Studio solo playtest, Studio multiplayer simulation, device/input simulation, network simulation, or authorized published-experience test. A GitHub Actions pass verifies only the checks that actually ran in CI. It does not launch Studio or prove live Roblox behavior.

## Release decision

Do not ship while a P0/P1 regression remains unresolved, required tests are blocked without an accepted mitigation, or evidence is incomplete. A human owner must review release risk and approve any documented exception. Preserve the toolkit's no-gambling policy, transparent monetization, privacy restrictions, and player-safety rules.
