# Roblox Experiments and Open Cloud lifecycle

## Native experience experiments

Use Creator Hub Experiments for in-experience config tests. The platform assigns eligible players to a control or treatment variant and retains their enrollment assignment. Do not add a second custom client-side random assignment mechanism on top of the native experiment.

An in-game experiment varies config values. This V43 plan and validator is deliberately limited to that product type; Roblox matchmaking experiments have a separate configuration contract.

## Open Cloud scopes

The current experimentation guide documents:
- Read/list/get/stats operations require the universe:read scope.
- Create/update/discard/start/schedule/complete operations require universe:write.
- Every API endpoint is scoped to a universe ID.
- Keep API credentials outside source control, project prompts, manifests, and logs.

Use the least privilege needed. Keep read-only inspection separate from write operations and require a human to approve every write.

## Asynchronous operations

Create/update/discard/start/schedule/complete operations return an operation object rather than finishing synchronously. Capture its operationId and poll the operations endpoint until done is true. Handle structured errors, failed operations, and timeouts explicitly. Stats requests also resolve asynchronously.

Never assume an initial HTTP success means the experiment was created, started, scheduled, or completed. Check the final operation result and inspect the returned experiment state.

## Lifecycle

1. Create a draft for one config key and review the control value, treatment value(s), variant weights, exposure, metric, and duration.
2. Confirm event instrumentation is already available and the sample feasibility/MDE is acceptable.
3. Test the experience behavior and request human approval.
4. Start or schedule using the authorized workflow.
5. Monitor experiment state, confidence intervals, guardrails, and SRM.
6. Let the planned duration complete unless an operator must respond to critical early harm or invalid data.
7. Complete with a reviewed winning variant ID, or omit the winner to stop without selecting a treatment.
8. Read back the permanent config value and verify deployed server behavior.

After an experiment is started or scheduled, its configuration becomes immutable. Do not attempt to patch a running experiment's duration, variants, rollout, or targeting. Create a new experiment for a new hypothesis.

## V43 tooling boundary

The V43 CLI does not call the Open Cloud API, retrieve live results, poll operations, start/schedule/complete experiments, or edit experience configs. It validates local plans and helps review result summaries that an authorized person exports or transcribes from Roblox.
