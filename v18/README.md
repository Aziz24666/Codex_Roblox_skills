# V18 — Connected Automation, Economy Safety, and Fair Monetization

V18 connects the cumulative Roblox Codex skill library through one task lifecycle, shared artifacts, deterministic routing, dependency-aware workstreams, and evidence-driven gates. It includes 12 new workflow/orchestration skills plus four upgraded economy specialists already present in V17. That gives V18 16 skill definitions and 175 installed native skills in the cumulative package.

The V18 economy layer enforces a strict **no-gambling** rule: no paid random rewards, wagers, paid rerolls, or Robux-funded chance outcomes. It adds deterministic fixed-price shops, tier progression that requires ownership of every item in all earlier tiers, gameplay-earned currency, and fair monetization guidance for cosmetics, passes, guaranteed developer products, subscriptions, paid access, and private servers.

## CLI requirements

Use Python 3.13, the runtime used by CI. The inherited package uses `tomllib`, available in Python 3.11 and later. From the cumulative package root, install the pinned dependencies with:

```bash
python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt
```

The `doctor` and `route` subcommands are standard-library-only. Skill/schema validation and the full `verify` command require these dependencies.

Start with `INDEX_V18.md`. The mandatory policy is `docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md`. Workflow references: `docs/AUTOMATED_WORKFLOW.md` and `docs/SKILL_INTEROPERABILITY.md`.
