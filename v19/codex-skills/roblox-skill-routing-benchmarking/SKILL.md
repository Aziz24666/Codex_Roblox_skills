---
name: roblox-skill-routing-benchmarking
description: Create positive and negative regression cases to measure deterministic skill-router coverage and over-selection.
---

# Skill Routing Benchmarking

## Mission

Keep deterministic skill selection accurate, bounded, and relevant as the skill library grows. Prevent routing regressions, missing specialists, and indiscriminate loading.

## Benchmark corpus

Maintain version-controlled cases with:
- a stable case ID;
- a realistic task request (include concise and multi-system examples);
- expected domains;
- required skills;
- forbidden or irrelevant skills.

Include positive cases for common Roblox systems and negative cases for small tasks, unrelated specialist domains, and ambiguous multi-system requests. Prefer representative wording over repeated exact trigger terms.

## Metrics

For each case, report:
- required skill coverage (selected required skills / required skills);
- forbidden-skill violations;
- required-domain coverage;
- case pass rate;
- selected-skill count and selection breadth.

A case passes only when every required domain and required skill appears and no forbidden skill is selected. Report per-case failures; aggregate percentages must never hide a broken critical route.

## Evaluation procedure

1. Inspect the router's signals, domain priorities, limits, and fallback behavior.
2. Add the case before changing a routing rule.
3. Run \`python v19/tools/v19.py evaluate-routing --root .\`.
4. Review actual selected skills and every failure, not only the summary.
5. Add a negative case when a broader signal could load irrelevant specialists.
6. Keep benchmark changes auditable and avoid editing expectations merely to match a flawed implementation.

## Interpretation limits

The V19 evaluator exercises the deterministic keyword/domain routing function. It does not score a language model, prove that an agent read or followed a skill, or validate generated code. Model-level evaluations need their own controlled fixtures, prompt versions, blinded review, acceptance criteria, and repeatable scoring process.

## V18 shared workflow and handoff contract

- Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned. Do not silently redefine shared APIs, schemas, remotes, data ownership, or another specialist's files.
- Return a structured handoff: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence, risks, blockers, and next owner.
- Update task/evidence artifacts. Use PASS only for checks that actually ran; keep unavailable Studio/device/live-service checks NOT_RUN or BLOCKED.
- Re-route when scope changes. Skills do not grant tools, permissions, MCP connections, or runtime capabilities.

## V19 verification and evaluation contract

- Select verification from changed paths, impacted systems, trust boundaries, and failure impact; do not run or report unrelated checks as proof.
- Separate formatting, static analysis, unit, contract, integration, Studio, multi-client, device, performance, persistence, economy, and live-service checks.
- A plan is not an execution result. Preserve NOT_RUN and BLOCKED states for checks that did not run.
- A PASS requires the exact command or scenario, named environment, tool/runtime version, build identity, expected behavior, observed behavior, and a non-empty inspectable evidence artifact.
- Keep failures visible. Do not weaken acceptance criteria, delete negative benchmark cases, or convert a failed check into a pass.
- Deterministic routing benchmarks measure router behavior only; they do not prove model reasoning quality, skill compliance, or game correctness.
