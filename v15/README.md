# V15 Development System Overlay

V15 extends the cumulative V14 kit with a project-aware development and verification layer. This directory is a source-controlled V15 overlay; it does not replace the V14 release or claim that Roblox Studio runtime tests have been executed.

## V15 objectives
- Inspect a project before changing it and build a dependency-aware implementation plan.
- Select only relevant specialist skills instead of loading the entire library.
- Define measurable acceptance criteria for each implementation task.
- Evaluate skill selection and task outcomes with repeatable benchmark cases.
- Validate security, persistence, performance, and runtime evidence explicitly.
- Keep verification claims honest: static checks, builds, Studio runtime tests, device checks, and production checks are separate evidence classes.

## Contents
- `skills/`: eight specialist workflow specifications.
- `schemas/`: project manifest, task evaluation, and runtime evidence contracts.
- `examples/`: benchmark tasks and example evidence.
- `tools/v15_validate.py`: standard-library validator for manifests, benchmark cases, and evidence.
- `docs/IMPLEMENTATION_PIPELINE.md`: mandatory project workflow.
- `docs/QUALITY_GATES.md`: evidence and release gates.

## Use with V14
Keep the V14 package intact. Copy or merge this `v15/` directory into the extracted cumulative package, then read the skill specifications and schemas relevant to the task. V15 is an additive development-system layer, not a replacement for V14's existing skills, plugins, or fixtures.

## Validation
Run:
```bash
python v15/tools/v15_validate.py --root v15
python -m unittest discover -s v15/tests -v
```

These checks validate V15 metadata and evidence contracts. They do not launch Roblox Studio, simulate physical devices, verify live DataStores, or prove production behavior.
