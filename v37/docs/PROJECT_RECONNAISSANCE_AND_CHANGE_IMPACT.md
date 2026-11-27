# V37 Project Reconnaissance and Change Impact

## Read before write

Start by confirming the game project root. Inspect its structure and configuration before proposing architecture or editing files. Distinguish source facts from assumptions. Exclude generated assets, dependency caches, and large binary files from broad inventories.

## Trace the real feature flow

For the feature under change, map the relevant entry points and data flow across client scripts, server scripts, shared modules, remotes, UI, persistence, assets, and tests. Use paths and symbol names actually present in the project. Identify who owns state and which layer validates it.

## Change-impact checklist

Review:
- Public module and remote contracts.
- Client/server trust boundaries and payload validation.
- DataStore keys, schemas, migrations, and rollback options.
- UI, input, device, and localization implications.
- Asset references and dependency ownership.
- Tests and build mappings.
- Privacy, moderation, filtering, and monetization constraints where relevant.

A project tree or static reference scan is not proof of runtime behavior. Do not claim a Studio test happened unless evidence exists.
