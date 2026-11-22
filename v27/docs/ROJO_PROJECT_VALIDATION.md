# V27 Rojo Project Validation

Rojo project files are JSON files ending in `.project.json`. V27 validates the top-level project name, tree structure, `$className` values, and `$path` mappings.

## Validate a project

With one project file in the game folder:

    python v27/tools/v27.py rojo-check --root "C:\Path\To\YourGame"

When there are multiple project files, select one explicitly:

    python v27/tools/v27.py rojo-check --root "C:\Path\To\YourGame" --project default.project.json

Run a real build without leaving a generated place file behind:

    python v27/tools/v27.py rojo-check --root "C:\Path\To\YourGame" --project default.project.json --build

The optional build requires the Rojo CLI. V27 directs the build output to a temporary directory and removes it after validation. It does not start `rojo serve`, connect a Studio plugin, sync into a live place, or publish.

## Mapping checks

The validator checks that each constant `$path` is a string, resolves relative to its project file, exists, stays inside the selected game-project root, and does not traverse a symlink. It also checks that nested instance descriptors are objects.

Warnings for repeated path mappings are review-only; a project may intentionally map one source directory more than once. The validator does not attempt to fully reproduce Rojo's mapping semantics, glob behavior, metadata handling, or all descriptor options. A successful static check is not a replacement for running Rojo's actual build.

## Live-sync precautions

- Make sure the intended project file, universe, and place are selected before using the Rojo Studio plugin.
- Confirm the configured place ID and any allowed place IDs.
- Review the Rojo diff and Studio DataModel before accepting changes.
- Keep an isolated test place for validation.
- Do not treat a successful local build as approval to live-sync, save, or publish.

## Sources

- [Rojo v7 Project Format](https://rojo.space/docs/v7/project-format/)
- [Rojo v7 Installation](https://rojo.space/docs/v7/getting-started/installation/)
- [Rojo: Creating a new game and building](https://rojo.space/docs/v7/getting-started/new-game/)
