# Roblox Codex Game Studio Kit — V21 Index

V21 is the current cumulative release. It extends V1–V20 with six game-aware monetization specialists and an evidence-based project scanner. See [V21 overlay index](v21/INDEX_V21.md) for the new skill set and commands.

## Start here

1. Read `AGENTS.md` and this index.
2. Start substantial development tasks with `$roblox-end-to-end-development-orchestrator`.
3. Inspect the project using `python v18/tools/v18.py doctor --root .`.
4. Generate a risk-based verification plan with `python v19/tools/v19.py plan-tests --root . --task "..."`.
5. Run game-aware monetization discovery with `python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json`.
6. Review the generated evidence with the six V21 monetization specialists. Fit scores are not revenue predictions.
7. Run required tests in real authorized Roblox environments and record results with V19 evidence rules.

## V21 scope

The cumulative package contains **191 native Codex skills**: 175 inherited skills, five V19 verification specialists, five V20 production specialists, and six V21 monetization specialists.

V21 preserves the mandatory no-gambling economy rule. It focuses on deterministic direct purchases, cosmetics, optional convenience, legitimate subscriptions, privacy-safe aggregate analytics, transparent storefront UX, and controlled pricing experiments.
