# Roblox Codex Game Studio Kit — V15 Index

V15 is cumulative. It includes all V1–V14 material plus eight native Codex skills and a project-aware implementation and verification layer.

## Start here
- AGENTS.md — global engineering, research, safety, and approval contract.
- README.md — installation, package validation, and capability boundaries.
- INDEX_V15.md — current skill and reference routing.
- PACKAGE_INVENTORY.md — generated package counts.
- SHA256SUMS.txt, V14_SHA256SUMS.txt, and V15_SHA256SUMS.txt — current per-file integrity manifests.
- v15/docs/PACKAGE_INTEGRITY.md — manifest coverage and historical checksum policy.
- v15/README.md — V15 layer overview and validation commands.

## V15 Codex skills
The following native skills are installed in .agents/skills/ in the extracted package. Each has its own SKILL.md entry point.

- $roblox-project-intelligence — inspect the project, map its source of truth, and create a project manifest.
- $roblox-skill-selection-orchestration — choose the smallest useful set of specialist skills.
- $roblox-acceptance-driven-implementation — turn requests into observable criteria and a verified vertical slice.
- $roblox-remote-security-review — review client-originated requests and server-side validation.
- $roblox-persistence-migration-testing — plan and verify versioned persistence changes using isolated test data.
- $roblox-performance-regression-testing — profile representative workloads and compare measured results to baselines.
- $roblox-runtime-evidence-triage — classify evidence, investigate failures, and report unexecuted checks honestly.
- $roblox-reproducible-release-engineering — audit source, build, archive, checksum, and release reproducibility.

## V15 references and contracts
- v15/docs/IMPLEMENTATION_PIPELINE.md — end-to-end project workflow.
- v15/docs/QUALITY_GATES.md — quality gates and evidence vocabulary.
- v15/schemas/ — project manifest, task evaluation, runtime evidence, and V9 collection schemas.
- v15/examples/ — illustrative manifests, benchmark tasks, evaluation, and NOT_RUN evidence.
- v15/tools/v15_validate.py — V15 contract and native-skill validator.
- v15/tools/audit_cumulative_package.py — full installed-skill, schema, source-syntax, link, and checksum audit.
- v15/tools/patch_cumulative_package.py — package integration, inventory, and checksum generation.

## V14 Studio testing
Retain V14's Studio Test Runner plugin, disposable fixture, scenario catalog, and Studio-specific runbook. See docs/V14_STUDIO_TEST_HARNESS_ARCHITECTURE.md, docs/V14_STUDIOTESTSERVICE_REFERENCE.md, docs/V14_STUDIO_TEST_PLUGIN_RUNBOOK.md, and INDEX_V14.md.

## Earlier material
All V1–V13 skills, documentation, templates, prompts, examples, schemas, and tools remain part of the cumulative package. Use this index to route current work, then read only the relevant specialist skill and references.
