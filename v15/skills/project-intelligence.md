# Skill: Roblox Project Intelligence

## Purpose
Build an evidence-based map of an existing Roblox project before changing it.

## Required workflow
1. Inspect repository instructions, project files, Rojo mappings, manifests, and tests.
2. Identify server/client/shared boundaries and runtime entrypoints.
3. Trace dependencies and locate existing implementations before proposing new modules.
4. Detect generated files, duplicated systems, stale docs, and unowned configuration.
5. Produce a concise architecture map with file references and confidence labels.
6. Record unknowns rather than guessing.

## Output contract
Return project kind, toolchain, entrypoints, system map, dependency risks, test commands, and a prioritized list of verified findings. Do not claim a complete audit if the repository could not be fully inspected.
