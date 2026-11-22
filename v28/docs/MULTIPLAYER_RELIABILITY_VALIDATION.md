# Multiplayer Reliability Validation

Security and reliability need repeatable multi-client tests, not just a successful solo play session. Use the V26 Studio MCP workflow and device/network matrix together with these V28 scenarios.

## Scenario matrix

- **Remote contract:** valid request, wrong type, missing argument, oversized collection, unknown enum, invalid Instance, and unexpected nil.
- **Authority:** attempt a state change without ownership, with another player's object, outside interaction range, in the wrong match phase, or after the state has changed.
- **Frequency:** normal cadence, rapid repeated requests, simultaneous requests, and requests after a cooldown expires.
- **Idempotency:** submit the same logical action twice, retry after a timeout, and simulate a client reconnect after the server has committed the action.
- **Persistence:** save during progression, rejoin, concurrent server activity, service throttling, transient errors, and server shutdown.
- **Migration:** legacy profiles, current profiles, malformed profiles, partial migration, repeated migration, backup restore, and rollback.
- **Network:** latency, jitter, packet loss, temporary disconnect, reconnect, and out-of-order presentation. Verify that the server remains authoritative and clients reconcile.

## Execution discipline

1. Use a dedicated test place or private staging environment with synthetic data.
2. Record the place/version, test build, client count, device profile, and network conditions.
3. Run the same scenario with one, two, four, and up to eight Studio test clients where practical.
4. Capture server and client output, assertion results, and relevant state before and after each scenario.
5. Separate expected rejection from an unhandled error. Confirm that rejected requests do not mutate state.
6. Repeat tests after fixes and record regression evidence.
7. Keep saving, publishing, production DataStore writes, and player-impacting cloud operations behind explicit human approval.

## V28 and V26 relationship

V26 supplies the local Studio MCP and multiplayer/device test-planning workflow. V28 adds security-focused scenarios and local source review. GitHub Actions cannot interact with a developer's local Studio session. A generated plan or static report must never be described as a completed playtest.
