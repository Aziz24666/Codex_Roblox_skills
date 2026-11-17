# Skill: Reproducible Release Engineering

Keep canonical source human-readable and build distributable archives from source. Pin tool versions and verify downloaded tool checksums. Generate manifests and checksums from the final package. Verify archive contents, required files, and clean extraction before release.

Use least-privilege CI permissions. Separate validation jobs from release jobs. Release only artifacts produced by the same successful workflow run and refuse to overwrite an existing immutable release tag. Document exactly which checks ran and which require Studio or external environments.
