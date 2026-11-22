# Roblox Codex Game Studio Kit — V22 Index

V22 is the current cumulative release. It extends V1–V21 with five platform-monetization specialists, pricing-readiness scanning, and subscription-contract validation. See [V22 overlay index](v22/INDEX_V22.md) for details.

## Start here
1. Read `AGENTS.md` and this index.
2. Start substantial tasks with `$roblox-end-to-end-development-orchestrator`.
3. Inspect the project using `python v18/tools/v18.py doctor --root .`.
4. Generate a risk-based test plan using `python v19/tools/v19.py plan-tests --root . --task "..."`.
5. Run V21 game-aware discovery using `python v21/tools/v21.py discover --root . --output reports/monetization-discovery.json`.
6. Audit price handling using `python v22/tools/v22.py audit-pricing --root .`.
7. Validate subscription declarations using `python v22/tools/v22.py validate-subscription-contract --root . --file <path>`.
8. Complete the V22 launch gate and test all live platform flows in an authorized Roblox environment.

## V22 scope
The package contains **196 native Codex skills**, including Creator Rewards, Managed Pricing, subscription operations, creator-revenue portfolio planning, and monetization release readiness. All V18–V21 safety, evidence, and reliability requirements remain in force.
