# V14 source overlay

The repository's V14 source is cumulative. It is reconstructed from the existing V13 source archive and the ten base64 text segments in `v14-overlay-b64parts/`.

The overlay itself has SHA-256:

`8ac5adfe3aaa54e33c674e979cf2814fc8f311933176f1890fadf0fa84b79158`

The `ci.yml` workflow concatenates the segments in lexicographic order, decodes them, verifies the hash, extracts the overlay over the V13 source tree, then runs all V14 checks and builds.

The full ZIP and TAR.XZ files are created by the workflow and exposed as the Actions artifact `roblox-codex-game-studio-kit-v14`. This split representation is a storage optimization; the actual downloaded archive contains the normal, complete V14 directory tree and does not need the overlay to run.
