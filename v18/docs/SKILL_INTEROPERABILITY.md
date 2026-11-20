# V18 Skill Interoperability Contract

## Why this exists

The package contains many specialist skills. V18 prevents them from behaving like disconnected prompt collections by giving them one shared task record, one workflow vocabulary, explicit handoffs, and a single integration owner.

## Shared artifacts

- `.codex/workflows/project-profile.json` — verified repository/toolchain facts.
- `.codex/workflows/tasks/<task-id>/work-item.json` — user outcome, scope, acceptance criteria, domains, skills, dependency graph, risks, approvals, evidence.
- `.codex/workflows/tasks/<task-id>/contracts/` — API, schema, remote, data, and lifecycle contracts.
- `.codex/workflows/tasks/<task-id>/decisions/` — dated decisions and source evidence.
- `.codex/workflows/tasks/<task-id>/evidence/` — command output, test reports, Studio reports, and artifact references.
- `.codex/workflows/tasks/<task-id>/completion.md` — final human-readable completion report.

These are conventions, not magically synchronized databases. Codex must read and update them explicitly.

## Specialist contract

Every skill invocation should:

1. Read the applicable root/nested `AGENTS.md`, work item, project profile, and upstream contract.
2. State its bounded responsibility and avoid redoing another specialist's work.
3. Re-verify current facts when the task touches a changing API, tool, platform rule, or external service.
4. Consume upstream decisions and preserve stable identifiers.
5. Produce concrete outputs that downstream specialists can use.
6. Record changed paths, interface changes, tests actually run, evidence, risks, and next owner.

## Standard handoff fields

```json
{
  "skill": "roblox-example-specialist",
  "work_item_id": "task-example",
  "scope_completed": [],
  "inputs_consumed": [],
  "decisions": [],
  "changed_files": [],
  "contracts_consumed": [],
  "contracts_produced": [],
  "checks": [],
  "evidence_paths": [],
  "risks": [],
  "blockers": [],
  "next_owner": "integration-owner"
}
```

## Integration ownership

One orchestrator owns cross-skill integration. Specialists do not independently redefine shared schemas, RemoteEvent names, persistent data ownership, or public module APIs. Any such change is proposed as a contract update and reviewed by the integration owner. Parallel agents receive exclusive path scopes; conflicts are resolved before merge.

## Cross-cutting rules

- Use server authority for consequential game state.
- Make persistence and economy mutations idempotent and auditable.
- Enforce `NO_GAMBLING_AND_FAIR_MONETIZATION.md` for every shop/economy task: monetized outcomes are fixed and disclosed; paid random outcomes and wagering are prohibited.
- Route monetization work to all four V18 economy specialists. Tier progression requires ownership of every required item in all earlier tiers, and required items must have a non-Robux acquisition route.
- Treat imported/generated content and client input as untrusted.
- Generate outputs from canonical schemas/catalogs where practical.
- Prefer shared modules and explicit interfaces over copy-paste systems.
- Every requirement maps to an implementation owner and evidence-producing check.
- No skill may claim that another skill ran, a tool was connected, or a test passed without evidence.
