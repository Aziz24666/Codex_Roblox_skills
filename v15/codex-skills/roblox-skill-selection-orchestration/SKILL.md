---
name: roblox-skill-selection-orchestration
description: Select and coordinate the smallest effective set of Roblox Codex specialist skills for a feature, subsystem, bug, audit, or release task.
---

## Mandatory current-source research gate

Before substantive implementation, perform fresh online research using the current official Roblox Creator Hub/API documentation and relevant Roblox platform updates, deprecations, security guidance, or release notes. Check upstream documentation for any external tool or framework involved. Compare viable approaches when an API, architecture, or platform behavior is version-sensitive. Record exact source URLs, access dates, verified claims, alternatives, decisions, and the verification plan in `research/decisions/`. Re-open sources for each new task; previous research is background, not a substitute for current verification. Never invent a citation or claim a source was checked when it was not. If a critical platform or tool claim cannot be verified, mark the affected implementation `BLOCKED — RESEARCH NOT VERIFIED` rather than guessing.

# Roblox Skill Selection and Orchestration

## When to use
Use when a task spans several Roblox subsystems, when choosing specialists before implementation, or when the agent risks loading too much unrelated guidance.

## Procedure
1. Restate the requested player-visible or developer-visible outcome in one sentence.
2. Inspect INDEX_V15.md, the relevant earlier index, and the project manifest if present.
3. Split the task into bounded concerns such as architecture, UI, networking, persistence, assets, animation, performance, Studio tooling, or release engineering.
4. Map each concern to a skill using its declared scope and description. Choose one primary orchestrator and only specialists needed to cover real risks.
5. Record each selected skill and the concern it owns. Avoid selecting skills that duplicate the same review.
6. Identify missing coverage. If no skill addresses a risk, use current official documentation and project evidence rather than inventing a specialist.
7. Load the chosen SKILL.md files and only the linked references required for the task.
8. Keep ownership clear: one implementation plan, one source of truth, shared acceptance criteria, and one verification report.
9. Re-evaluate selection when scope changes. Add a specialist only when the newly discovered concern justifies it.

## Efficiency rules
- Prefer a small, non-overlapping set over broad loading.
- Do not read all 144 skills for an ordinary task.
- Avoid chaining skills merely because their titles sound related.
- Reuse verified project facts and read deep references only on demand.

## Output contract
Report the primary skill, selected specialists, why each is necessary, uncovered concerns, and which checks each skill contributes. Selection is not proof that implementation or tests succeeded.
