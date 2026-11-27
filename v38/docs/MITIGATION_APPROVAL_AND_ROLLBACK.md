# Mitigation approval and rollback

A proposal is not authorization. Require a human approver and explicit approval reference for every high-risk, rollback, or restore action. Keep action scope and approval timestamp auditable.

Before action: define expected outcome, blast radius, dependencies, rollback point, backup/data compatibility, verification window, stop conditions, and responsible operator. Prefer reversible and narrow mitigations. Never bypass server authorization, remote validation, text filtering, rate limits, or transaction validation.

After action: verify intended behavior with independent evidence, record the applied/reverted state and reference, and reassess impact. If verification fails, stop and escalate rather than chaining speculative changes.

DataStore restores, migrations, economy operations, and server/client rollbacks can affect persisted state and compatibility. Require specialist review and a verified recovery point. The CLI validates approval metadata only; it never performs or authorizes an operation.
