# V18 Migration Guide

V18 is cumulative: download and use only the V18 package. It retains V1–V17 content and adds a connected workflow layer. Existing Codex workflows continue to work; the V18 orchestrator and shared handoff contract become the recommended entry points.

## Existing projects

1. Extract V18 and open the package root in Codex.
2. Run `python v18/tools/v18.py doctor --root .` to inspect the package, then run the doctor against your actual game repository when working there.
3. Read root `AGENTS.md` and `INDEX_V18.md`.
4. Use `$roblox-end-to-end-development-orchestrator` for substantial tasks.
5. Create a work item with `v18/tools/v18.py plan --task "..." --write`.
6. Let the router suggest a minimal skill set, then validate the routing against actual project impact.
7. Keep external actions approval-gated and record evidence.

## Compatibility

- V1–V17 skills remain installed; V18 adds a shared invocation/handoff section without replacing their domain instructions.
- The root checksum manifest, V18 manifest, and V14 compatibility manifest are regenerated for the final V18 tree. Older manifests remain historical snapshots.
- Existing project architecture is not migrated automatically. The V18 doctor is read-only and will not convert Studio-native projects to Rojo or alter `.codex` global configuration.
