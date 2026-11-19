---
name: roblox-runtime-evidence-triage
description: Classify Roblox validation evidence, triage failed or blocked Studio scenarios, and report static, build, runtime, device, and production checks separately.
---

# Roblox Runtime Evidence and Triage

## When to use
Use after tests/builds, when investigating a failing scenario, or when preparing a milestone/release report that needs an accurate evidence boundary.

## Evidence classes
- Static: validators, linters, schema checks, source inspection.
- Toolchain: Luau compilation and Rojo/project builds.
- Automated tests: unit or integration tests in their actual runner.
- Studio runtime: a scenario actually launched and executed inside Roblox Studio.
- Device: a real device or explicitly named simulator preset.
- Service/production: an authorized staging or production operation.

These classes are not interchangeable.

## Procedure
1. Capture commit/build ID, tool or Studio version, environment, scenario ID, run ID, start/end time, and client count where relevant.
2. Define expected results and observable assertions before investigating.
3. Inspect structured reports, logs, artifacts, and cleanup results. Preserve the first failing evidence before a fix.
4. Classify the failure as assertion failure, setup/environment blocker, timeout, toolchain issue, flaky behavior, or incomplete evidence.
5. Reproduce with the smallest disposable fixture and deterministic inputs. Avoid real player data and production services.
6. Make one targeted correction, then rerun the same scenario and relevant neighboring tests.
7. Record each retry as a distinct attempt. Do not overwrite original failing evidence.
8. Use v15/schemas/runtime-evidence.schema.json. A PASS requires an evidence artifact or log reference.
9. Use PASS, FAIL, BLOCKED, NOT_RUN, or NOT_APPLICABLE accurately and include limitations.
10. Report unresolved failures as blockers; do not hide them behind unrelated green checks.

## Pitfalls and fixes
- Build success presented as gameplay pass: split the report by evidence class.
- No run ID or logs: report evidence as incomplete, not passed.
- Simulator reported as physical device: name the actual environment.
- No cleanup evidence: flag leaked fixtures or state as unresolved.

## Output contract
Produce a criterion-by-criterion report with run metadata, logs/artifacts, actual status, failure classification, retries, cleanup, and limitations.
