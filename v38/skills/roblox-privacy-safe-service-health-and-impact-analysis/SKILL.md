---
name: roblox-privacy-safe-service-health-and-impact-analysis
description: Assess Roblox experience service health and user impact using aggregate, purpose-limited evidence.
---

# Privacy-safe service health and impact analysis

## Required practice
- Use aggregate service-level signals: availability, error-rate bands, latency percentiles, queue depth, failed operation counts, and time windows.
- State numerator, denominator, sample window, source, and confidence where available.
- Separate service symptoms from root-cause hypotheses.
- Compare against a documented healthy baseline and note rollout/environment differences.
- Record affected service categories and coarse audience scope only where justified.
- Report unknown or insufficient data honestly; never fill gaps with invented numbers.

## Privacy boundary
Never collect or paste player names, Roblox user IDs, IP addresses, device identifiers, chat, support conversations, payment details, credentials, or per-player histories into incident records. Avoid small cohorts that could identify an individual. Use an authorized, privacy-reviewed aggregate source and retain only the minimum necessary summary.

## Roblox systems to consider
DataStore operations and consistency, matchmaking/teleports, remote/network performance, core gameplay services, purchase/economy flows, content delivery, moderation, publishing, and platform status. Treat platform status pages as one signal, not a substitute for experience-specific evidence.

## Deliverable
A concise impact summary with affected service categories, time window, aggregate scope, confidence, evidence references, privacy-review attestation, and explicit unknowns.

## Limits
This skill cannot query Creator Dashboard, Roblox services, or live telemetry. Privacy attestations are human assertions and do not perform PII detection.
