# V19.0.0 — Testing Intelligence and Evidence Governance

**Release:** \`v19.0.0\`  
**Type:** feature release  
**Base:** V18.0.1  
**License:** MIT

V19 advances the Roblox Codex Game Studio Kit from connected workflow orchestration into measurable verification. It retains the inherited V1–V18 library and adds five focused V19 specialists, a deterministic routing benchmark, test-plan generation, evidence validation, and Studio multi-client testing guidance.

## What's new

### Five V19 specialists
- Risk-based test matrix planning for changed systems, acceptance criteria, and failure impact.
- Luau static analysis and gradual strict-type adoption using the project's existing analyzer/linter configuration.
- Roblox Studio multi-client test engineering using the actual StudioTestService and supported Studio automation capabilities.
- Deterministic skill-routing benchmarking with positive and negative regression cases.
- Verification evidence auditing so completion status aligns with observed outcomes and inspectable artifacts.

### New local tooling
- \`python v19/tools/v19.py plan-tests\` generates an ordered, risk-based verification plan. Every generated check begins as \`NOT_RUN\`; the command does not execute game code or launch Studio.
- \`python v19/tools/v19.py evaluate-routing\` runs 12 version-controlled cases against the deterministic V18 router and reports missing required skills/domains and forbidden over-selection.
- \`python v19/tools/v19.py validate-evidence\` validates an evidence packet against the V19 schema, checks status requirements, and verifies that artifact paths remain inside the package and point to non-empty files.
- Cumulative audits and checksums are extended to 180 installed native skills and four active hierarchical checksum manifests.

## Verification

The V19 workflow validates the overlay, runs V19 regression tests, reconstructs the pinned V17 baseline, integrates and fully verifies V18, integrates V19, validates its routing benchmark and evidence schemas, runs inherited audits, and compares ZIP/TAR.XZ extraction contents before release publication.

GitHub Actions does not launch Roblox Studio. Real Studio playtests, multi-client sessions, device/input matrices, performance profiling, live DataStore behavior, purchase fulfillment, and production operations remain environment-specific and must be recorded as such. A routing benchmark measures deterministic router selection only; it is not a score of LLM reasoning or generated game quality.

## Installation

Download the complete V1–V19 package from the [V19.0.0 GitHub Release](https://github.com/Aziz24666/Codex_Roblox_skills/releases/tag/v19.0.0), extract it, open the package root in Codex, and start with \`AGENTS.md\` and \`INDEX_V19.md\`.

See \`v19/README.md\` and \`v19/docs/\` for detailed use and maintenance guidance.
