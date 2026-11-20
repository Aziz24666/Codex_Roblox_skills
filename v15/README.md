# V15 Project-Aware Development System

V15.0.4 is a corrective cumulative release. It retains the V1–V14 package and adds a project-aware implementation workflow, measurable acceptance criteria, explicit security/persistence/performance review, runtime-evidence rules, and eight native Codex skills.

## What changed
- Eight native Codex skills are provided under codex-skills/ in this source overlay and copied into the cumulative package's .agents/skills/ directory. Codex can discover these skills from the package root.
- Project intelligence, architecture discovery, source-of-truth mapping, and project-manifest guidance.
- Task-to-skill routing that keeps context focused.
- Acceptance-driven implementation and vertical-slice verification.
- Remote-security, persistence-migration, and performance-regression review workflows.
- Runtime evidence classification and reproducible release guidance.
- JSON schemas, example records, regression tests, package inventory, and SHA-256 file manifest.

## Install and use
1. Download the V15.0.4 ZIP or TAR.XZ release asset and extract it.
2. Open the extracted package root in Codex.
3. Read AGENTS.md and INDEX_V15.md.
4. Start whole-project work with $roblox-game-builder; add only the V15 specialist skills relevant to the task.
5. Run python v15/tools/v15_validate.py --root v15 and python -m unittest discover -s v15/tests -v after changing V15 contracts or skill metadata.

## Source overlay layout
- codex-skills/<skill-name>/SKILL.md — native Codex skills; copied to package .agents/skills/.
- skills/ — concise workflow-specification source notes retained for traceability.
- schemas/ and examples/ — machine-readable contracts and illustrative records.
- tools/v15_validate.py — standard-library validator.
- tools/patch_cumulative_package.py — applies the V15 layer, normalizes installed skill metadata, and regenerates package documentation and all current checksums.
- tools/audit_cumulative_package.py — validates the complete installed skill library, JSON schemas/examples, source syntax, local links, and current checksum manifests.
- schemas/v9-editor-field-descriptors.schema.json — collection schema for the legacy V9 field-descriptor example.
- docs/IMPLEMENTATION_PIPELINE.md and docs/QUALITY_GATES.md — project and verification policies.

## Full cumulative package audit

After installing the pinned CI dependencies, run `python v15/tools/audit_cumulative_package.py --root .` from the package root. This validates all 143 installed skill frontmatters, all V15 source-to-installed skill copies, JSON/JSON Schema and the V9 descriptor collection, source file syntax, local Markdown links, empty/cache files, and all three current checksum manifests.

See `v15/docs/PACKAGE_INTEGRITY.md` for the current-versus-historical manifest policy.

## Evidence boundaries
The V15 CI workflow validates metadata and JSON contracts, runs Python regression tests, compiles Python, reconstructs the cumulative package, integrates the V15 layer, verifies per-file checksums, and creates ZIP/TAR.XZ archives. The separate V14 CI workflow compiles Luau and builds the sample experience, Content Factory plugin, V14 Test Runner plugin, and disposable fixture.

Neither workflow launches Roblox Studio. No CI result alone proves a Studio playtest, multiplayer runtime correctness, physical-device behavior, live DataStore behavior, asset permissions, or production safety. Such checks must be executed in their real authorized environments and recorded as separate evidence.
