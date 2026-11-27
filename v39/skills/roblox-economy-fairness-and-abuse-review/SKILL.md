---
name: roblox-economy-fairness-and-abuse-review
description: Review Roblox gameplay economies for fairness, repeatable-reward abuse, and server-authority weaknesses.
---

# Roblox economy fairness and abuse review

Review every source, sink, reward, and progression transition.

## Threat and fairness questions
- Can a client choose its own reward or currency amount?
- Can remotes be replayed to duplicate a reward?
- Are cooldowns and eligibility checked on the server?
- Are retries idempotent, including after a timeout?
- Can concurrent requests overspend the same balance?
- Does any repeatable action create unlimited currency with negligible effort?
- Can casual players access meaningful progression without purchasing?
- Are paid items clearly described, optional, and fixed in outcome?
- Are all random reward mechanisms excluded from paid flows?
- Are there pressure loops that punish breaks or require excessive play?

## Deliverable
A table of invariant, exploit scenario, server-side control, test case, residual risk, and owner. Prioritize data-integrity and transaction duplication issues.

## Limits
This is a design/security review guide. It does not scan production code, run exploit tests, access player data, or validate platform transactions. Do not provide exploit instructions; describe abuse cases at a defensive design level.
