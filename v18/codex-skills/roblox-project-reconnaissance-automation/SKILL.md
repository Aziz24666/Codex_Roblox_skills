---
name: roblox-project-reconnaissance-automation
description: Run repeatable, read-only discovery of a Roblox repository, source-of-truth workflow, toolchain, architecture markers, skills, and validation entry points.
---


## V18 shared workflow and handoff contract

- Follow the root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned by the orchestrator. Do not silently redefine shared APIs, schemas, RemoteEvents, data ownership, or another specialist's files.
- Return a structured handoff: scope completed, inputs consumed, decisions, changed files, contracts consumed/produced, checks actually run, evidence paths, risks/blockers, and next owner.
- Update the shared work item and evidence artifacts. Use `PASS` only for checks that actually ran; keep Studio/device/live-service checks `NOT_RUN` or `BLOCKED` when not executed.
- Re-route and update downstream contracts when scope or impact changes. Skills do not grant tools, permissions, connected MCP servers, or runtime capabilities.

## Mandatory current-source research gate
Before changing Roblox APIs, Studio behavior, toolchains, security, persistence, monetization, or external integrations, re-check current official Roblox Creator Hub/API documentation and upstream tool documentation. Record exact URLs, accessed date, claims, decision, alternatives, and verification plan in `research/decisions/`. Prior notes are context, not current proof. Never invent sources. Mark unresolved critical facts `BLOCKED — RESEARCH NOT VERIFIED`.

# Project reconnaissance automation

## Operating procedure
1. Begin with read-only inspection. Use `python v18/tools/v18.py doctor --root . --json` when the V18 toolkit is present. Never modify the project during reconnaissance.
2. Identify the source of truth: Studio-native place files, Rojo project mappings, Script Sync, a documented hybrid, or unknown. Detect project markers without assuming that the presence of a Rojo file means every asset is Rojo-managed.
3. Map top-level directories, nested AGENTS.md guidance, scripts, packages, schemas, assets, tests, build configuration, CI workflows, and deployment-related files. Exclude caches, generated output, secrets, and large binary payloads from routine summaries.
4. Detect available tool executables and versions using read-only version commands. Do not install, upgrade, authenticate, publish, or execute arbitrary project scripts during discovery.
5. Record evidence with path, timestamp, and confidence. Mark conflicting source-of-truth indicators as unresolved rather than choosing silently.
6. Write a project profile only when explicitly requested, preserve an existing profile unless the user requests refresh, and keep secret values out of generated reports.

## Required handoff
Return: outcome and scope; inputs inspected; decisions and assumptions; files changed; contracts consumed/produced; selected next skills; checks actually run and statuses; evidence paths; blockers and approvals. See `v18/docs/SKILL_INTEROPERABILITY.md` and `v18/docs/AUTOMATED_WORKFLOW.md`.
