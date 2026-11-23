# V30.0.0 — Production Release Readiness and Evidence Validation

V30 extends the cumulative V1-V29 Roblox Codex Game Studio Kit with a candidate-specific production release dossier, environment-aware gates, evidence reference validation, rollback/backup readiness, and local configuration hygiene.

## New capabilities

- Four native Codex skills:
  - `roblox-production-release-readiness-v30`
  - `roblox-release-evidence-management-v30`
  - `roblox-rollback-and-incident-response-v30`
  - `roblox-environment-configuration-hygiene-v30`
- `v30/tools/v30.py` commands:
  - `doctor`: inspect project inventory and optional local tools without executing configured commands.
  - `plan`: create a review-only release plan; all gates begin as `not_run`.
  - `validate`: enforce environment-specific gates, candidate version/revision fields, project-local evidence paths, optional SHA-256 integrity, rollback/backup references, and production approval records.
  - `audit`: perform a bounded read-only check for credential-like text, local environment files, and Rojo path mapping problems.
- Release plan and report schemas, a staging example, documentation, unit tests, cumulative package patching and auditing.
- Cumulative package target: **224 native Codex skills**.

## Release policy

- Development requires functional-test evidence.
- Staging requires functional, server-authority, persistence, security, and Studio smoke-test evidence.
- Production requires all nine standard V30 gates, staged rollout, rollback and backup references, plus release-owner, QA-lead, and security-reviewer approval records.
- A DataStore migration adds migration validation; production also requires data-owner approval.
- Passed gates must reference existing project-local evidence. Optional SHA-256 values are checked against the referenced file.
- Publishing mode is fixed to manual. This toolkit never publishes, migrates, writes a DataStore, or changes live configuration.

## Boundaries and safeguards

- Evidence paths and optional hashes are checked, but the tool does not authenticate people, prove that tests ran, or certify Roblox dashboard state.
- Static credential/configuration findings may be false positives or incomplete. Reports never copy matched secret values.
- Use isolated test places and synthetic data. Human approval is required for production and player-impacting operations.
- All V1-V29 capabilities remain cumulative, including fair monetization and the mandatory no-gambling requirements.

## Validation

The V30 workflow reconstructs the pinned V17 baseline, applies V18-V30 overlays, runs inherited regression suites plus V30 tests, audits the 224-skill cumulative package, checks repository syntax/data/Markdown/skill metadata, builds ZIP and TAR.XZ archives, compares extracted contents, and verifies SHA-256 checksums. Studio tests, physical-device checks, dashboard review, and rollback rehearsals remain human-run evidence tasks.
