# V38.0.0 — Production Incident Response and Recovery

## Added
- Four native Codex skills for incident triage, privacy-safe impact analysis, approved mitigation/recovery, and player communication/postmortem.
- Offline incident-record validator and readiness auditor.
- Strict allowlists, bounded input, duplicate-key rejection, chronological event checks, severity/role validation, privacy attestations, explicit approval gates, and verified closure criteria.
- JSON Schema, representative incident example, docs, 31 unit tests, cumulative package patcher/auditor, and GitHub Actions release workflow.

## Cumulative package
V1–V38, 256 native Codex skills. Download only the V38 package.

## Limitations
V38 validates supplied metadata only. It does not query Roblox services, inspect live telemetry, determine real player impact, authenticate opaque references, execute mitigations, roll back releases, restore data, or send communications. Human approvals remain external to the CLI. Privacy fields are attestations, not automated PII scanning.
