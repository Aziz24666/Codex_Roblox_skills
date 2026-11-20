# V18 Automation Approval Boundaries

## Safe default autonomy

The agent may inspect the authorized workspace, read documentation, create a plan, edit reversible source files, add tests, run trusted local validators, build locally, and prepare a reviewable diff. Normal implementation should not be interrupted by unnecessary confirmation requests.

## Stop and request approval

Stop before publishing/unpublishing, deploying, changing live experience settings/permissions, uploading or replacing public assets, modifying production data, migrating/resetting live player data, creating/deleting places, spending Robux or money, or pushing external changes unless the user explicitly requested that exact action. Explain target, effect, risk, rollback, and evidence.

## Credentials

Never request, print, commit, or store passwords, API keys, cookies, tokens, or `.ROBLOSECURITY`. Do not put secret values in project profiles, task contracts, logs, reports, screenshots, or issue comments. Presence of a configured credential does not itself authorize its use.

## CI boundaries

Use least-privilege permissions. Pull-request workflows are read-only where possible. Do not execute untrusted pull-request code in privileged triggers. Package build, artifact creation, release publishing, and deployment are separate jobs/gates. Never add an implicit deploy/publish step to a validation workflow.
