# V18 Automation CLI

The V18 utility is a local, read-only-first helper. It uses Python and the package's pinned dependencies. Run from the package root.

## Commands

```bash
# Discover the project, source-of-truth indicators, skill count, and installed tools.
python v18/tools/v18.py doctor --root .

# Machine-readable report.
python v18/tools/v18.py doctor --root . --json

# Recommend a minimal skill set for a task.
python v18/tools/v18.py route --root . --task "Build a character customization system"

# Draft a task plan without writing files.
python v18/tools/v18.py plan --root . --task "Build a character customization system"

# Explicitly write a task packet under .codex/workflows/tasks/.
python v18/tools/v18.py plan --root . --task "Build a character customization system" --write

# Validate a saved task and its dependency graph.
python v18/tools/v18.py validate-task --root . --file .codex/workflows/tasks/<id>/work-item.json

# Validate V18 schemas, examples, source skills, installed skill registry, and shared contracts.
python v18/tools/v18.py validate --root .

# Rebuild registry from the current installed skill collection.
python v18/tools/v18.py build-registry --root . --write
```

## Automation safety

`doctor` never runs build/test scripts from the target project. It only checks known executable version flags with short timeouts. `route` and `plan` do not edit game source. `plan --write` creates a new work artifact and refuses to overwrite an existing task. The CLI does not install tools, fetch dependencies, modify Codex global settings, invoke MCP, access credentials, publish, deploy, or alter live Roblox data.

The CLI's route is a deterministic recommendation based on keywords and registered skill metadata. The orchestrator must read descriptions, inspect the real task impact, and adjust the selection. It is not an LLM and does not replace engineering judgment.
