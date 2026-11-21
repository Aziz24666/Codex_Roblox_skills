# V20.0.0 — Production Reliability and Live Operations

**Release:** `v20.0.0`  
**Type:** feature release  
**Base:** V19.0.0  
**License:** MIT

V20 extends the cumulative V1–V19 Roblox Codex Game Studio Kit with production-oriented architecture contracts, five specialist skills, a static contract validator, and routing regressions. It focuses on preventing high-impact failures after a feature is built: authority mistakes, lost player data, duplicate grants, unsafe rollout, and poor incident visibility.

## What's new

### Five V20 specialists

- **Server authority and remote boundaries:** explicit client-to-server operation contracts, server validation, ownership/context checks, rate limits, bounded payloads, and idempotency.
- **Player data resilience and migrations:** UpdateAsync-safe transforms, bounded retry/backoff, load-failure policy, session ownership, adjacent deterministic/idempotent migrations, and recovery planning.
- **Idempotent economy transactions:** verified receipt processing, fixed grants, durable receipt identifiers, duplicate-delivery handling, and reconciliation.
- **Live operations and safe rollouts:** development/staging/canary/production promotion, feature flags, kill switches, compatibility windows, and rollback/forward recovery.
- **Production observability and incident response:** actionable service metrics, privacy-safe logs, controlled dashboards, owned alerts, incident runbooks, and recovery evidence.

### New local tooling

- `python v20/tools/v20.py validate-contract` validates a versioned production-readiness declaration against JSON Schema and cross-field constraints.
- `python v20/tools/v20.py evaluate-routing` evaluates five additional production-focused routing cases.
- `python v20/tools/v20.py verify` runs inherited V19 verification, V20 routing evaluation, production contract validation, and the cumulative V20 audit.
- Five hierarchical checksum manifests protect the final cumulative package.

## Mandatory policy

V18's no-gambling economy policy remains mandatory. V20 does not permit paid random rewards, wagers, paid rerolls, or Robux-funded chance outcomes. Product grants must be deterministic, fixed, server-owned, and idempotent.

## Verification

The release workflow reconstructs the pinned V17 baseline, integrates and verifies V18, integrates and verifies V19, adds V20, runs the V20 regression suite and audits, verifies the contract example, and compares ZIP/TAR.XZ extraction contents before publishing.

The production contract is a static declaration validator. GitHub Actions does not launch Roblox Studio or prove live DataStore behavior, actual ProcessReceipt fulfillment, remote implementation correctness, production dashboards/alerts, deployments, or rollback execution. Those checks must be run in real authorized environments and recorded under V19 evidence rules.

## Installation

Download the complete V1–V20 package from the [V20.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v20.0.0) after publication, extract it, open the package root in Codex, and start with `AGENTS.md` and `INDEX_V20.md`.
