# Roblox Codex Game Studio Kit — V32

V32.0.0 is the complete cumulative V1-V32 package with **232 native Codex skills**.

## V32 additions

- Four native Codex skills for UGC text filtering, privacy-minimal report triage, human moderation review/appeals, and safety-by-design.
- v32/tools/v32.py:
  - doctor: local source inventory and optional tool checks.
  - audit: bounded Luau audit for legacy text filtering, likely client-context TextService calls, and possible raw text assignments.
  - validate-policy: validate review-time bands, evidence retention, appeal window, second-review policy, and the mandatory no-automation rule.
  - validate-case: validate one privacy-minimal moderation record.
  - validate-register: validate a batch of records and unique opaque case references.
- Three JSON schemas, three examples, three guides, regression tests, cumulative package patcher/auditor, and a V1-V32 release workflow.
- Cumulative package target: **232 native Codex skills**.

## Quick start

From the extracted V32 package root, run:

    python .\v32\tools\v32.py doctor --root C:\Path\To\YourGame
    python .\v32\tools\v32.py audit --root C:\Path\To\YourGame
    python .\v32\tools\v32.py validate-policy --root C:\Path\To\YourGame
    python .\v32\tools\v32.py validate-case --root C:\Path\To\YourGame
    python .\v32\tools\v32.py validate-register --root C:\Path\To\YourGame

Copy the policy and case examples from v32/examples/ into the selected project's .codex/moderation/ directory. Edit only project-owned policy values and opaque references; do not add player identity or content fields.

## Safety boundaries

The tools are offline and non-enforcing. They do not contact Roblox, read live reports, inspect chat, collect player identities, or apply moderation actions. Preserve Report Abuse and platform moderation tools. Keep original player/evidence records in authorized Roblox systems, and use V32 case metadata only for privacy-minimal internal tracking.

All custom non-chat text visible to other players must follow current server-side TextService filtering guidance. Use native TextChatService for chat. If filtering fails, do not display the submitted text. Human review and appeals are required; high-impact cases may require an independent second reviewer.

All V1-V31 safeguards remain cumulative.
