# V17 baseline repair for V18 staging

The V18 draft PR is blocked because its pinned V17 TAR.XZ baseline is reconstructed from incorrect/incomplete base64 chunks and the workflow has the wrong SHA-256.

The verified baseline archive is `roblox-codex-game-studio-kit-v17.tar.xz` with SHA-256:

`6679380cdfd962611645bd6b9427690ef7d036784ba033825480847026cf8c61`

## Repair steps

1. Download the verified V17 archive linked with this repair note.
2. Clone `https://github.com/Aziz24666/Codex_Roblox_skills.git` or open your existing checkout.
3. Check out the PR staging branch:

   ```bash
   git checkout v18-release-staging
   git pull origin v18-release-staging
   ```

4. Save the archive somewhere on your computer. Run the repair script from the repository root, passing the archive's full path:

   ```bash
   python tools/repair_v17_baseline.py /path/to/roblox-codex-game-studio-kit-v17.tar.xz
   ```

   On Windows, use the Windows path, for example:

   ```powershell
   py tools/repair_v17_baseline.py "C:\Users\YOUR_USER\Downloads\roblox-codex-game-studio-kit-v17.tar.xz"
   ```

5. The script verifies the archive hash, TAR.XZ structure, V17 validator/test files, 163 installed skills, chunk reconstruction, and workflow checksum before reporting success. It refuses to run on `main` or any branch other than `v18-release-staging`. It does not commit or push.
6. Review and push the generated repair:

   ```bash
   git status --short
   git add .github/workflows/v18-quality.yml dist/v17-baseline-b64parts
   git commit -m "Repair verified V17 baseline reconstruction"
   git push origin v18-release-staging
   ```

7. Open [PR #6](https://github.com/Aziz24666/Codex_Roblox_skills/pull/6) and confirm the cumulative package job passes. Keep the PR unmerged until the full workflow, inventory audit, and archive comparison pass.

## Expected local result

- V17 archive size: 445,044 bytes
- SHA-256: `6679380cdfd962611645bd6b9427690ef7d036784ba033825480847026cf8c61`
- Base64 chunks: 50 files, 12,000 characters each except the final file
- Chunk round-trip: byte-for-byte identical to the verified archive
- Workflow checksum: updated to the verified SHA-256
