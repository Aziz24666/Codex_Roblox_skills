# V20 — Production Reliability and Live Operations

V20 extends the V1–V19 cumulative toolkit with five production-focused specialists, a versioned production contract, static cross-field validation, and routing regressions.

## Read first
- `INDEX_V20.md` — current cumulative package map.
- `docs/PRODUCTION_RELIABILITY.md` — server authority, persistence, economy, rollout, and observability invariants.
- `docs/REMOTE_AUTHORITY_AND_DATA.md` — remote contracts, data lifecycle, and migration guidance.
- `docs/OPERATIONS_AND_ROLLOUTS.md` — promotion, kill-switch, rollback, and incident workflow.
- `schemas/production-contract.schema.json` and `examples/production-contract.example.json` — machine-readable contract.

## Commands

```bash
python v20/tools/v20.py evaluate-routing --root .
python v20/tools/v20.py validate-contract --root . --file v20/examples/production-contract.example.json
python v20/tools/v20.py verify --root .
```

Install inherited validation dependencies from the package root with `python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt`. Python 3.13 is the CI-validated runtime.

The production contract validator checks declarations and cross-field consistency. It does not connect to Roblox or prove that remote handlers, DataStores, receipt processing, feature flags, alerts, deployments, or rollback procedures work. Use V19 test planning/evidence and perform Studio/live-service checks only in authorized, isolated environments.

V18's no-gambling monetization policy remains mandatory. Paid random rewards, wagers, paid rerolls, and Robux-funded chance outcomes are prohibited.
