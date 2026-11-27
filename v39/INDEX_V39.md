# V39 source index

Version: 39.0.0

## Components
- Four native Codex skills for economy architecture, simulation, progression design, and fairness review.
- `tools/v39.py`: offline deterministic economy/progression model validator and simulator.
- `schemas/economy-model.schema.json`: model contract.
- `examples/economy-model.example.json`: synthetic example.
- `tests/test_v39.py`: regression and path-safety tests.
- `docs/`: model design, interpreting results, and CLI reference.

## Use
Create a project-local model JSON, validate it, simulate it, then review warnings and assumptions with a human. Run the model across multiple parameter variants and compare the resulting reports.

## Safety and trust boundaries
Cohorts are synthetic archetypes, not individual player profiles. Do not import player IDs, chat, purchases, account histories, or other personal data. This tool does not estimate revenue/retention or access Roblox services. Do not add chance-based paid rewards, loot boxes, wagers, or gambling mechanics. A passing model validates structure, not game balance.
