# Skill: Runtime Evidence and Failure Triage

For every runtime test, record a unique run ID, scenario ID, environment, timestamps, client count where relevant, logs, artifacts, and limitations. Reproduce failures with the smallest deterministic scenario possible.

Classify outcomes precisely: PASS only after execution and successful assertions; FAIL after an executed failing assertion; BLOCKED when execution could not proceed; NOT_RUN when no attempt occurred. Attach source references and logs to diagnosis. Do not convert a build success into a Studio runtime pass.
