# Skill: Remote Security Review

Treat every client-originated value as untrusted. Review each RemoteEvent and RemoteFunction for:
- payload type, shape, size, and numeric bounds;
- player identity, ownership, permissions, distance, cooldown, and state;
- server authority over currency, inventory, rewards, progression, and match outcomes;
- rate limits and abuse-resistant failure behavior;
- replay, duplicate requests, and race conditions where relevant.

Create negative tests for malformed, unauthorized, stale, and excessive requests. Never imply that static inspection proves exploit resistance. Do not build exploit tooling; focus on defensive validation and controlled tests.
