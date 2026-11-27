# Economy model design

V39 describes gameplay currencies using explicit sources, sinks, starting balances, and healthy balance ceilings. Each source/sink amount is an integer granted or requested on an active day. Synthetic cohorts define active days per week and a basis-point activity multiplier (10,000 = 1.0x).

## Suggested modeling steps
1. List each gameplay currency and its purpose. Avoid overlapping currencies that make the economy hard to explain.
2. Identify each source: quests, round rewards, milestones, crafting refunds, or other transparent gameplay events.
3. Identify each sink: cosmetic purchases, crafting, upgrades, or convenience items that do not invalidate fair play.
4. Estimate conservative and generous daily amounts from observed aggregate data or explicit design assumptions.
5. Define a healthy balance ceiling to highlight potential accumulation; it is a review threshold, not a universal truth.
6. Simulate multiple synthetic activity archetypes over the same horizon.
7. Investigate persistent sink shortfalls, runaway balances, and large progression gaps.
8. Change one assumption at a time and compare reports. Preserve model versions and rationale.

## Formula
For each active day, a source/sink amount is scaled by the cohort multiplier using integer floor arithmetic: `amount * activity_multiplier_bps // 10000`. Sources are added before sinks. A sink spends only available balance; the unmet remainder is reported as a shortfall. No negative balances are created. Progression XP is accumulated independently and rewards are granted once when an XP threshold is crossed.

## Scope
Only supplied assumptions are simulated. The tool does not detect actual events, measure real players, or determine the correct currency economy. Calibrate assumptions using human-reviewed, privacy-safe aggregate observations and real playtests.
