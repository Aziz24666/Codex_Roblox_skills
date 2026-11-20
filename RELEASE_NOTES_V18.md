# V18.0.0 — Connected Automation and Cross-Skill Orchestration

**Release:** `v18.0.0`  
**Type:** cumulative workflow automation and interoperability upgrade  
**License:** MIT

V18 upgrades the cumulative Roblox Codex Game Studio Kit from a large collection of specialist skills into a coordinated development workflow. It retains V1–V17 and adds 12 V18 skills, shared cross-skill contracts, structured task state, dependency-aware planning, local automation tools, and stronger validation/approval boundaries.

## Highlights

- Adds 12 specialist skills for end-to-end orchestration, task intake, project reconnaissance, impact-aware skill routing, cross-system contract governance, dependency-aware planning, bounded autonomous implementation, agent delegation, continuous validation/repair, risk and approval gating, context handoff, and evidence-first completion.
- Applies the V18 shared handoff contract to the cumulative installed skill library so older specialists report scope, interfaces, changed files, checks, evidence, risks, blockers, and next ownership consistently.
- Adds a task lifecycle and schemas for work items, project profiles, skill registry, and workflow evidence.
- Adds deterministic routing configuration connecting existing skills across 14 domains.
- Adds a local Python CLI for read-only project discovery, skill routing, task planning, task graph validation, registry generation, and cumulative verification.
- Adds workstream DAG validation for missing dependencies, cycles, duplicate IDs, and overlapping owned paths.
- Improves CI reconstruction from a pinned V17 baseline, package integrity, archive comparison, and release artifact generation.

## Automation and safety

The V18 CLI is read-only by default. Explicit task scaffolding writes only a new task artifact and refuses to overwrite existing tasks. The orchestrator may automate normal reversible workspace tasks when the current Codex runtime provides the required tools. Delegation and Studio MCP are conditional on actual runtime connectivity.

Publishing, deployment, production DataStore changes, public asset uploads, permissions changes, destructive actions, credential handling, and spending remain approval-gated. Skills do not grant tools or permissions.

## Validation

The V18 workflow reconstructs the cumulative package from the pinned V17 baseline, installs V18, runs V15–V18 validators and regression tests, runs inherited package doctors/tests, regenerates current package metadata and SHA-256 manifests, performs a full cumulative audit, and compares extracted ZIP/TAR.XZ contents.

CI does not launch Roblox Studio. Studio playtests, multiplayer runtime behavior, device testing, live DataStore behavior, asset permissions, live purchase fulfillment, and production operations require separate execution and evidence.

## Installation

Download the complete ZIP or TAR.XZ release asset, extract it, open the package root in Codex, and read `AGENTS.md` and `INDEX_V18.md`. Start substantial tasks with `$roblox-end-to-end-development-orchestrator`.
