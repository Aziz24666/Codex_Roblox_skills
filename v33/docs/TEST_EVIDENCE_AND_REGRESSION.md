# Test Evidence, Regression Comparison, and QA Decisions

## Use the V33 structured format

The V33 test plan schema records a suite ID, max simulated client count, platform/network profiles, and bounded test cases. The run report records an opaque run reference, timestamp, environment, and exactly one result for every planned test.

The CLI validates the structures without executing tests:

- validate-plan checks unique test IDs, allowed scenario/category codes, client bounds, supported platforms, and execution modes.
- validate-report checks the plan/report relationship, environment, complete test coverage, result status/outcome combinations, and opaque evidence references.
- compare identifies regressions, improvements, newly blocked tests, and coverage gaps between two reports for the same suite.

## Status semantics

- pass: the test actually ran and the expected behavior was verified.
- fail: the test ran and a defined assertion or behavior failed.
- blocked: execution was prevented by environment/setup/tool availability.
- not_run: the test was intentionally not attempted.

A blocked or not_run case is never a pass. If Studio was unavailable, record that fact using the bounded result code; do not create a synthetic pass.

## Evidence minimization

Reports accept only fixed codes and opaque references. Do not include names, user IDs, raw chat, voice content, credentials, access tokens, private server identifiers, or free-form player data. Preserve detailed logs/screenshots only in authorized project-owned systems and reference them through an opaque token.

## Baseline rules

Compare the same suite ID and test IDs. A test changing from pass to fail is a regression; pass to blocked is a new execution blocker; pass to not_run is a coverage gap. Improvements do not cancel unrelated regressions. A report comparison is a triage aid, not an automated release approval.

## Limitations

A V33 report is a statement of evidence supplied by the person running the test; the validator checks structure and consistency, not truthfulness of external evidence. Static scans do not parse all Luau semantics. Studio-only testing must be run and reviewed in Roblox Studio.
