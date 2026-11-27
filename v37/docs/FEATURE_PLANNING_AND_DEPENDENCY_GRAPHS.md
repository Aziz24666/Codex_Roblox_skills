# V37 Feature Planning and Dependency Graphs

A V37 plan is a bounded contract for a feature implementation. Each task needs a stable ID, objective, dependencies, allowed paths, risk classification, human-review flag, and verifiable acceptance criteria.

## Planning principles

1. Keep the goal aligned with the user's requested outcome.
2. Prefer small tasks that can be reviewed independently.
3. Declare dependencies explicitly; cyclic or missing dependencies invalidate the plan.
4. Keep file scopes narrow. Independent tasks may not silently claim overlapping paths.
5. Use verification kinds honestly: `static`, `automated_test`, `studio_manual`, and `runtime_manual`.
6. High-risk work and tasks with manual Studio/runtime criteria require human review.
7. Preserve server authority, secure persistence, privacy, user-generated text filtering, player safety, and transparent non-gambling monetization.

The CLI computes a stable topological order and reports scope conflicts. It does not infer architecture or execute implementation.
