# V38 source index

Version: 38.0.0

## Components
- Four production incident response Codex skills.
- `tools/v38.py`: offline incident validator and readiness auditor.
- `schemas/incident.schema.json`: JSON Schema contract.
- `examples/incident.example.json`: intentionally unresolved sample incident.
- `tests/test_v38.py`: adversarial validation and path-safety tests.
- `docs/`: triage, mitigation/rollback, communications/postmortem, CLI reference.

## Safety and trust boundaries
Use aggregate service health and impact data only. Do not record player names, user IDs, chat, support transcripts, contact details, credentials, or individual player histories. Do not infer severity from incomplete data. Require a human incident commander and explicit human approval for rollback/restore or other high-risk action. Never run a destructive action solely because the audit CLI returns success.
