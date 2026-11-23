---
name: roblox-environment-configuration-hygiene-v30
description: Review Roblox project configuration, Rojo path mappings, and environment-specific secret handling before a release.
---

# Roblox Environment Configuration Hygiene

## Configuration review

1. Identify the exact project configuration used by the candidate, including Rojo project files and environment-specific settings.
2. Confirm mapped paths exist and remain inside the project root. Resolve missing or out-of-root mappings before building.
3. Keep development, staging, and production configuration distinct and review every difference that affects permissions, services, monetization, persistence, or feature flags.
4. Keep API keys and credentials in approved local secret storage or CI secret managers. Never commit real credentials or put them in Codex prompts, release manifests, screenshots, or issue comments.
5. Provide sanitized `.env.example` templates containing placeholder values only.
6. Limit each credential to the minimum permissions and intended environment; rotate exposed credentials using the authorized owner process.
7. Review configuration changes as part of the release diff and rollback plan.

## V30 audit

Run `v30/tools/v30.py audit --root <project>` for a bounded, read-only review of selected text/config formats, environment files, and Rojo `$path` mappings. Inspect findings manually. The audit is not a complete secret scanner and may report false positives or miss obfuscated/different credential formats.

## Safety

Do not print secret values, access live Roblox services, modify project files, or publish configuration changes automatically. Preserve least-privilege, server-authoritative boundaries and earlier V1-V29 safeguards.
