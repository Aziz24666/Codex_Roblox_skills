# V18 Automated Development Workflow

V18 turns the toolkit into one connected operating system for Codex. It does not promise unattended or unlimited autonomy: it automates repeatable discovery, task routing, work-item creation, graph validation, static checks, regression selection, and evidence packaging while preserving human approval for consequential external actions.

## Default lifecycle

1. **Intake** — turn the request into a scoped work item with goals, non-goals, constraints, assumptions, and observable acceptance criteria.
2. **Discover** — run the read-only project doctor, identify source of truth, nested guidance, module boundaries, test entry points, toolchain, and current Git state.
3. **Route** — select a small set of non-overlapping skills using task intent and impacted system boundaries. Use the end-to-end orchestrator as the owner.
4. **Specify** — record affected systems, authority, data and remote contracts, versioning, lifecycle, failure behavior, and test seams.
5. **Plan** — split the task into an acyclic workstream graph. Define exclusive path ownership. Parallelize only independent work.
6. **Implement** — complete one vertical slice at a time, inspect the diff, and update the work item.
7. **Integrate** — connect real interfaces, run end-to-end paths, and reconcile cross-system assumptions.
8. **Verify** — run the impact-selected checks from cheap deterministic tests to environment-specific tests. Repair root causes with bounded retries.
9. **Review** — check scope, security/trust boundaries, generated drift, documentation, acceptance evidence, and approval requirements.
10. **Handoff** — deliver a completion report with changed paths, evidence, limitations, unresolved risks, and checks not run.

## CLI quick start

From the package root:

```bash
python v18/tools/v18.py doctor --root .
python v18/tools/v18.py route --root . --task "Add persistent player inventory with a cross-platform UI"
python v18/tools/v18.py plan --root . --task "Add persistent player inventory with a cross-platform UI" --write
python v18/tools/v18.py validate-task --root . --file .codex/workflows/tasks/<task-id>/work-item.json
python v18/tools/v18.py validate --root .
```

`doctor`, `route`, `plan` (without `--write`), and validation are read-only. `plan --write` creates a task artifact but does not edit game source. The CLI never installs tools, edits global Codex configuration, publishes, deploys, uploads assets, or touches production data.

## What is automated

- Read-only project marker and toolchain discovery.
- Skill inventory and deterministic task-to-skill routing suggestions.
- Economy/monetization routing to four V18 specialists, backed by a mandatory no-gambling policy and regression tests.
- Work-item and dependency-graph validation.
- Structured JSON project profile and task artifacts.
- Package/schema/skill audits and repeatable Python test suites.
- V18 handoff conventions across all installed skills.

## What still requires a capable runtime or human approval

Codex must actually expose terminal, repository, MCP, subagent, or browser tools for those actions to occur. The toolkit cannot create capabilities or permissions. Roblox Studio MCP automation requires a connected Studio instance and compatible client. Studio, multiplayer, device, live-service, and production checks are not implied by static tests. Publishing, deployment, live data, public assets, permission changes, destructive actions, and spend require the explicit approvals defined in `APPROVAL_BOUNDARIES.md`.
