# V15 Implementation Pipeline

Use this pipeline for every substantial feature. Small documentation-only changes may skip runtime stages, but must still state why.

## 1. Discover
- Read root instructions, project manifest, and architecture documentation.
- Inspect the actual project tree before proposing edits.
- Identify source-of-truth files, framework versions, Rojo mappings, existing conventions, and generated files.
- Search existing systems before creating new ones.
- Record unknowns; do not invent project structure or APIs.

## 2. Select skills
- Search the skill index using task intent, system boundaries, and required evidence.
- Load the primary orchestrator plus only relevant specialists.
- Record selected skill IDs and why each was selected.
- If no skill matches, proceed cautiously and propose a reusable skill only after completing the task.

## 3. Plan
Create a task plan containing:
- user-visible outcome;
- systems and files likely affected;
- dependencies and risks;
- data and network boundaries;
- acceptance criteria that can be observed;
- required tests and evidence;
- rollback or migration strategy where persistent data is affected.

Do not start implementation until the plan is coherent. Ask one targeted question only when a missing decision blocks safe implementation.

## 4. Design
Define module ownership, public interfaces, data schemas, lifecycle, error handling, and client/server authority. Prefer existing project patterns unless they are demonstrably unsafe or unmaintainable. Avoid broad rewrites for a narrow feature.

## 5. Implement
- Make small, reviewable changes.
- Keep server-authoritative state on the server.
- Validate every client-originated request on the server.
- Keep configuration data separate from behavior.
- Use strict types where supported and avoid hidden global state.
- Never put secrets or production credentials in source control.

## 6. Verify
Run relevant static checks, format/lint checks, Luau compilation, Rojo builds, unit tests, and integration tests available in the environment. Then identify which tests require Roblox Studio or external services. Never label an unexecuted test as passed.

## 7. Runtime validation
For runtime-sensitive work, run the disposable Studio fixture and relevant scenarios. Capture run IDs, scenario IDs, environment, client count, logs, and results. Device, published-service, asset-permission, and production checks require their own authorized environments.

## 8. Review and report
Report:
- changed files and behavior;
- tests actually executed and their outcomes;
- tests not executed and why;
- known risks and follow-up work;
- data migrations and rollback instructions;
- exact manual steps remaining.

## 9. Maintain
Update architecture docs, schemas, skill mappings, tests, and examples when interfaces change. Remove stale guidance rather than accumulating contradictory instructions.
