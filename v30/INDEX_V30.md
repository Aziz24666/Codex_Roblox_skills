# Roblox Codex Game Studio Kit — V30

V30.0.0 is the cumulative V1-V30 release. It adds production release-readiness planning, evidence validation, rollback/backup gates, and a bounded local configuration and credential-hygiene audit.

## V30 additions

- Four native Codex skills for production release readiness, evidence management, rollback/incident response, and environment configuration hygiene.
- `v30/tools/v30.py` provides:
  - `doctor`: local project/tool inventory without executing configured commands.
  - `plan`: create a review-only release-plan template with all gates set to `not_run`.
  - `validate`: validate environment-specific gates, evidence paths and optional SHA-256 values, rollback/backup references, and production approval records.
  - `audit`: bounded read-only scan for credential-like patterns, environment files, and invalid Rojo path mappings.
- Release-plan and validation-report JSON schemas, a staging example, documentation, regression tests, and cumulative package patch/audit.
- Cumulative package target: **224 native Codex skills**.

## Quick start

From the extracted V30 package root:

```powershell
python ".\v30\tools\v30.py" doctor --root "C:\Path\To\YourGame"
python ".\v30\tools\v30.py" audit --root "C:\Path\To\YourGame"
python ".\v30\tools\v30.py" plan --root "C:\Path\To\YourGame" --version "1.2.3" --environment staging --source-revision "0123456789abcdef0123456789abcdef01234567"
python ".\v30\tools\v30.py" validate --root "C:\Path\To\YourGame"
```

The example release plan is at `v30/examples/release-plan.staging.example.json`. The generated plan is a template. Collect real evidence and update the appropriate gate records before validation.

## Release gate behavior

- Development requires the functional-test gate.
- Staging requires functional tests, server-authority review, persistence review, security review, and a Studio smoke-test record.
- Production requires all nine standard gates, a staged rollout, rollback-plan and backup references, and explicit release-owner, QA-lead, and security-reviewer approval records.
- A DataStore migration adds a migration-validation gate; production migrations also require a data-owner approval.
- Any gate marked passed must reference an existing project-local evidence file. An optional SHA-256 digest is checked against that file.
- Evidence is not independently authenticated. Approval names and timestamps are validated as declarations, not identity proofs.

## Important boundaries

- V30 does not publish places, create releases in Roblox, change live configuration, run Studio, execute migrations, write DataStores, or perform player-impacting operations.
- A valid manifest means its stated structure and evidence references passed local validation; it is not release authorization.
- Publishing remains manual and human-approved. Production releases require a staged rollout and an independently rehearsed rollback.
- Static credential/configuration findings are review leads, not a complete secret scanner or security certification. Matched values are never copied into reports.
- All V1-V29 capabilities and safeguards remain cumulative, including fair monetization and the mandatory no-gambling rule.
