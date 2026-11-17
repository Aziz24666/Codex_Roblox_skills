# Skill: Persistence and Migration Testing

Design persistence around explicit schema versions, deterministic migrations, bounded retries, idempotency, and clear session ownership. Use disposable test stores or mocks for tests; never point destructive tests at production player data.

Test old-schema migration, malformed records, interrupted operations, duplicate requests, concurrent sessions, save failures, and recovery. Document rollback constraints and any migration that cannot safely be reversed. Distinguish mocked persistence evidence from authorized staging or production evidence.
