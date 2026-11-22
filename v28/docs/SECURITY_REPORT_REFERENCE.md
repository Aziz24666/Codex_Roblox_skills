# V28 Security and Reliability Report Reference

The default report is .codex/reports/v28-security-reliability-report.json.

## Sections

- inventory: bounded count of source files read, discovered remote handlers, and DataStore operations.
- remote_security.handlers: statically recognized server handler locations, remote names when statically bound, and nearby review signals.
- remote_security.client_to_server_calls: statically discovered FireServer/InvokeServer counts by remote name or unresolved variable.
- remote_security.unpaired_client_calls: client calls without a matching statically named server handler in the scanned files.
- datastore.operations: API name, relative file, line number, and advisory review class.
- datastore.signals: presence/count of explicit version, migration, backup, protected-call, retry, budget, UpdateAsync, and SetAsync patterns.
- review_priorities: ordered reminders generated from the text scan; they are not severity scores or proof of a flaw.
- limitations: fixed statements describing the scanner's static and incomplete nature.

## Interpretation

A positive token signal merely indicates that a keyword or pattern exists in a bounded source area. For example, seeing typeof does not prove every argument is validated; seeing UpdateAsync does not prove the callback is idempotent. A missing signal may be implemented through helper modules, abstractions, wrappers, or generated code that a local scan cannot resolve.

The report is intentionally source-light: it records paths and line numbers, not entire source contents, secret values, DataStore keys, player identifiers, or credentials. Treat the report as an engineering review checklist, not a penetration test, exploit recipe, certification, or a substitute for Studio tests.
