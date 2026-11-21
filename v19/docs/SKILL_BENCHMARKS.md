# V19 Skill Routing Benchmarks

V19 adds a deterministic benchmark corpus for the package's keyword/domain router.

## What is measured

Each case contains a task prompt, expected domains, skills that must be selected, and skills that must not be selected. The evaluator reports:
- required-skill coverage;
- forbidden-skill violations;
- required-domain coverage;
- case pass rate.

The corpus is version-controlled in \`v19/evals/routing-cases.json\`. Add cases for ambiguous, multi-system, small-scope, and out-of-domain requests. Include negative cases so that the router is not rewarded for selecting every specialist.

## What is not measured

The benchmark executes the deterministic \`route_task\` function. It does not measure the quality of Codex model reasoning, prove that a skill was followed, or establish code quality. It is a regression test for routing behavior only.

For model-level quality evaluation, use separately reviewed tasks with fixed project fixtures, blinded reviewers, explicit acceptance criteria, and reproducible scoring. Record the model/client version and prompt context. Do not mix those subjective results into the deterministic router pass rate.

## Change policy

A routing change should:
1. add or update at least one positive case;
2. add a negative case when the change could cause over-selection;
3. explain expected skills and forbidden specialists;
4. run the complete corpus;
5. review selection count and domain breadth, not just the pass percentage.

Do not weaken a case by removing a required skill merely to make a failing change pass. Fix the routing signals or selection strategy and preserve the regression.
