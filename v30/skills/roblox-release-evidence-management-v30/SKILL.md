---
name: roblox-release-evidence-management-v30
description: Collect, organize, and review candidate-specific Roblox release evidence with provenance, integrity checks, and privacy boundaries.
---

# Roblox Release Evidence Management

## Evidence protocol

For each artifact, record:

- Candidate version and exact source revision.
- Development, staging, or production context.
- Place/build identity and relevant configuration.
- Test scenario, device tier, player count, and conditions where applicable.
- Execution timestamp with timezone, tool version, owner, observed result, and limitations.
- Relative evidence path and optional SHA-256 digest.

Keep artifacts project-local for V30 validation. Use bounded, sanitized summaries. Do not include secrets, player identifiers, private support conversations, access tokens, or raw production data.

## Review sequence

1. Confirm the artifact belongs to the current candidate and environment.
2. Check that the test was executed, not merely planned.
3. Confirm expected and observed results are both recorded.
4. Record failures and missing dimensions; do not silently discard them.
5. Repeat measurements where capture variance could change the conclusion.
6. Hash stable artifacts when useful and record the digest with the plan.
7. Preserve the source artifact and review history when regenerating a report.

## V30 validator

Use `v30/tools/v30.py validate` to check evidence references, project-root containment, optional digests, gate completeness, and declared approvals. The validator does not authenticate people, tools, timestamps, or test execution.

## Reporting

Separate verified observations from assumptions and static heuristics. Do not convert a missing measurement into a zero, a planned test into a pass, or an unverified dashboard setting into a fact. Mark blocked and not-run evidence plainly.

## Safety

Keep the dossier privacy-minimal. If a credential is exposed, do not paste it into the report; revoke/rotate it through the approved owner workflow and record the remediation without revealing the value.
