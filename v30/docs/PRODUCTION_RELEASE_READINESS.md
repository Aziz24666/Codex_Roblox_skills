# Production release readiness

V30 connects the toolkit's earlier Studio testing, server-authority, persistence, and performance evidence into one reviewable release dossier. The tool validates that the dossier is structurally complete and that referenced local evidence exists. It does not decide whether the evidence is true or authorize a publish.

## 1. Freeze the candidate identity

Before collecting release evidence, record the exact source revision and candidate version. Keep the test place, target environment, configuration, and candidate build aligned. Do not reuse staging evidence for a different source revision without recording and reviewing the difference.

Use the same version string across the release plan, candidate notes, and human release record. A source revision is a 7-64 character hexadecimal Git commit identifier.

## 2. Create a release plan

From the cumulative V30 package root:

```powershell
python ".\v30\tools\v30.py" plan --root "C:\Path\To\YourGame" --version "1.2.3" --environment staging --source-revision "0123456789abcdef0123456789abcdef01234567" --summary "Staging candidate"
```

The command writes `.codex/releases/release-plan.json` unless another project-local output path is supplied. Every gate begins as `not_run`. Creating a plan does not mark tests complete.

## 3. Collect evidence before marking gates passed

The standard gate identifiers are:

| Gate | Evidence examples |
|---|---|
| `functional_tests` | Test report, reproducible test matrix, and known failures |
| `multiplayer_tests` | Client-count, replication, network-condition, and device test summary |
| `server_authority` | Remote-contract and ownership-validation review |
| `persistence` | DataStore schema, retry/idempotency, and failure-mode test report |
| `security_review` | Threat review, permission boundaries, and credential/configuration check |
| `performance_review` | V29 capture comparison and device-budget report |
| `studio_smoke` | Human-recorded smoke-test evidence from the intended Studio build |
| `rollback_drill` | Evidence from an isolated rollback rehearsal |
| `monetization_policy` | Review of fixed outcomes, clear pricing, fair progression, and no-gambling compliance |
| `migration_validation` | Required when the release changes persistent data schema or migration behavior |

Use evidence files inside the selected project root. Keep them small, sanitized, dated, and tied to the exact candidate revision. You may add a SHA-256 digest to guard against accidental file changes. Never put credentials, player identifiers, private support messages, or production data into the dossier.

## 4. Validate the plan

```powershell
python ".\v30\tools\v30.py" validate --root "C:\Path\To\YourGame"
```

A successful result means the declared environment-specific gates are marked passed and required references can be opened within the project directory. Production additionally requires all nine standard gates, a staged rollout, rollback and backup references, and approval records for the release owner, QA lead, and security reviewer. A production DataStore migration adds the migration-validation gate and data-owner approval.

The validator rejects missing files, path traversal, symlink traversal, oversized evidence, optional digest mismatches, duplicate records, invalid timestamps, and an automatic publishing mode.

## 5. Run the hygiene audit

```powershell
python ".\v30\tools\v30.py" audit --root "C:\Path\To\YourGame"
```

The bounded audit checks project-local text/configuration files for credential-like assignments, non-template environment files, and Rojo `$path` mappings that are missing or unsafe. Reports contain file paths and line numbers but intentionally do not include matched secret values. Review every finding manually; false positives and missed formats are possible.

## 6. Human release decision

A release owner must independently verify the candidate in Roblox Studio and the Creator Dashboard, confirm the evidence is authentic and current, review support/rollback readiness, and publish manually through the authorized workflow. Start with a controlled staged rollout and defined monitoring/stop conditions. The local validator is not a substitute for this decision.
