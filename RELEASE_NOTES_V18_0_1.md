# V18.0.1 — Cumulative Audit and CLI Setup Fixes

**Release:** `v18.0.1`  
**Type:** maintenance release  
**Base:** V18.0.0  
**License:** MIT

V18.0.1 fixes the cumulative package integration and inherited-audit migration discovered during the V18 release audit. The release retains the V1–V18 skill library and contains **175 installed native Codex skills**.

## Fixes

- Migrates the embedded V17 cumulative audit from its actual baseline count of 163 to the V18 cumulative total of 175.
- Excludes only the four V18-upgraded economy specialists from the legacy V17 byte-for-byte parity comparison. The V18 validator independently enforces current V18 source-to-installed parity for those upgraded skills.
- Updates the migrated audit's active checksum manifest policy for the V18 package.
- Runs both the V18 cumulative audit and migrated V17 cumulative audit during `python v18/tools/v18.py verify`.
- Adds regression tests for audit migration, fail-closed behavior when the expected V17 baseline changes, and the inherited incomplete remote-validation teaching sample.
- Makes PyYAML and jsonschema lazy-loaded so basic `doctor` and `route` commands work without validation dependencies.
- Documents Python 3.13 and the dependency installation command:
  `python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt`.
- Labels the inherited remote-validation Luau example as teaching-only and explicitly not production-ready.
- Documents the Roblox restriction that paid experience access and private servers cannot be enabled together for the same experience.
- Corrects the package skill count to 175; four V18 economy specialists upgrade existing V17 skills rather than adding four additional installed skills.

## Verification

GitHub Actions successfully:
- Reconstructed the pinned V17 baseline.
- Integrated V18 into the cumulative package.
- Ran V14, V15, V17, and V18 validators and regression suites.
- Ran the migrated V17 cumulative audit and the V18 cumulative audit.
- Confirmed 175 installed skills and package integrity.
- Built the ZIP and TAR.XZ release archives, tested extraction, and compared their extracted contents.

Roblox Studio playtests, multiplayer runtime checks, live DataStore behavior, live purchase fulfillment, asset permissions, and production operations are not simulated by CI and still require validation in their actual authorized environments.

## Installation

Download the ZIP or TAR.XZ asset from the [V18.0.1 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v18.0.1), extract it, open the package root in Codex, and read `AGENTS.md` and `INDEX_V18.md`.
