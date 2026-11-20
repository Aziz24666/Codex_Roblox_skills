#!/usr/bin/env python3
"""Rebuild the pinned V17 baseline chunks for the V18 staging branch.

Run from a checkout of Aziz24666/Codex_Roblox_skills:
    python tools/repair_v17_baseline.py /path/to/roblox-codex-game-studio-kit-v17.tar.xz

The script refuses an archive whose SHA-256 is not the independently verified
V17 baseline. It rewrites the chunk directory and fixes the workflow checksum.
It does not commit, push, merge, or publish anything.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile

EXPECTED_SHA256 = "6679380cdfd962611645bd6b9427690ef7d036784ba033825480847026cf8c61"
OLD_WORKFLOW_SHA256 = "b1501a65fc4455ba358a6100e2a3a5bddb3b0363ad615d3d9971466634fc57d9"
CHUNK_CHARS = 12_000
EXPECTED_SKILLS = 163
ARCHIVE_ROOT = "roblox-codex-game-studio-kit-v17"


def fail(message: str) -> None:
    raise SystemExit(f"V17 baseline repair refused: {message}")


def verify_archive(archive_bytes: bytes) -> None:
    actual = hashlib.sha256(archive_bytes).hexdigest()
    if actual != EXPECTED_SHA256:
        fail(f"archive SHA-256 mismatch: expected {EXPECTED_SHA256}, got {actual}")

    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:xz") as package:
            members = package.getmembers()
            names = [member.name for member in members]
    except (tarfile.TarError, OSError, EOFError) as exc:
        fail(f"archive is not a valid readable TAR.XZ: {exc}")

    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            fail(f"unsafe path inside archive: {name}")

    required = {
        f"{ARCHIVE_ROOT}/v17/tools/v17_validate.py",
        f"{ARCHIVE_ROOT}/v17/tests/test_validator.py",
    }
    missing = required - set(names)
    if missing:
        fail(f"archive is missing required V17 files: {sorted(missing)}")

    skill_files = [
        name for name in names
        if name.startswith(f"{ARCHIVE_ROOT}/.agents/skills/") and name.endswith("/SKILL.md")
    ]
    if len(skill_files) != EXPECTED_SKILLS:
        fail(f"expected {EXPECTED_SKILLS} installed skills in archive, found {len(skill_files)}")


def chunk_base64(archive_bytes: bytes) -> list[str]:
    encoded = base64.b64encode(archive_bytes).decode("ascii")
    parts = [encoded[index:index + CHUNK_CHARS] for index in range(0, len(encoded), CHUNK_CHARS)]
    if not parts or any(not part for part in parts):
        fail("base64 chunking produced an empty part")
    reconstructed = base64.b64decode("".join(parts), validate=True)
    if reconstructed != archive_bytes:
        fail("local chunk round-trip did not reproduce the archive byte-for-byte")
    expected_count = math.ceil(len(encoded) / CHUNK_CHARS)
    if len(parts) != expected_count:
        fail("unexpected number of generated chunks")
    return parts


def require_staging_branch(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        fail(f"{repo_root} is not a Git checkout")
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "--show-current"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        fail(f"could not verify the current Git branch: {exc}")
    branch = result.stdout.strip()
    if branch != "v18-release-staging":
        fail(f"expected branch 'v18-release-staging', found {branch!r}; refusing to touch main")


def write_chunks(repo_root: Path, parts: list[str]) -> Path:
    destination = repo_root / "dist" / "v17-baseline-b64parts"
    destination.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / ".v17-baseline-b64parts.staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    try:
        for index, part in enumerate(parts):
            path = staging / f"part-{index:03d}.b64"
            path.write_text(part, encoding="ascii", newline="")

        staged_parts = sorted(staging.glob("part-*.b64"))
        joined = "".join(path.read_text(encoding="ascii") for path in staged_parts)
        rebuilt = base64.b64decode(joined, validate=True)
        if len(staged_parts) != len(parts) or hashlib.sha256(rebuilt).hexdigest() != EXPECTED_SHA256:
            fail("staged chunks failed the SHA-256 round-trip check")

        for old in destination.glob("part-*.b64"):
            old.unlink()
        for new in staged_parts:
            os.replace(new, destination / new.name)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def fix_workflow(repo_root: Path) -> Path:
    workflow = repo_root / ".github" / "workflows" / "v18-quality.yml"
    if not workflow.is_file():
        fail(f"missing workflow file: {workflow}")
    text = workflow.read_text(encoding="utf-8")
    if OLD_WORKFLOW_SHA256 in text:
        text = text.replace(OLD_WORKFLOW_SHA256, EXPECTED_SHA256)
    elif EXPECTED_SHA256 not in text:
        fail("workflow contains neither the known incorrect nor the verified V17 SHA-256")
    workflow.write_text(text, encoding="utf-8", newline="")
    return workflow


def repair(repo_root: Path, archive_path: Path, check_branch: bool = True) -> dict[str, object]:
    repo_root = repo_root.resolve()
    archive_path = archive_path.resolve()
    if check_branch:
        require_staging_branch(repo_root)
    if not archive_path.is_file():
        fail(f"archive file does not exist: {archive_path}")

    archive_bytes = archive_path.read_bytes()
    verify_archive(archive_bytes)
    parts = chunk_base64(archive_bytes)
    parts_dir = write_chunks(repo_root, parts)
    workflow = fix_workflow(repo_root)

    final_parts = sorted(parts_dir.glob("part-*.b64"))
    final_b64 = "".join(path.read_text(encoding="ascii") for path in final_parts)
    final_archive = base64.b64decode(final_b64, validate=True)
    if hashlib.sha256(final_archive).hexdigest() != EXPECTED_SHA256:
        fail("final repository chunk directory failed SHA-256 verification")

    return {
        "archive": str(archive_path),
        "archive_bytes": len(archive_bytes),
        "sha256": EXPECTED_SHA256,
        "chunk_count": len(final_parts),
        "chunk_chars": CHUNK_CHARS,
        "parts_directory": str(parts_dir.relative_to(repo_root)),
        "workflow": str(workflow.relative_to(repo_root)),
        "round_trip": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="verified V17 TAR.XZ archive")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="repository root (default: current directory)")
    args = parser.parse_args()
    result = repair(args.repo_root, args.archive, check_branch=True)
    print("V17 baseline repair prepared successfully:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("\nReview the changes, then commit and push the staging branch:")
    print("  git status --short")
    print("  git add .github/workflows/v18-quality.yml dist/v17-baseline-b64parts")
    print('  git commit -m "Repair verified V17 baseline reconstruction"')
    print("  git push origin v18-release-staging")
    print("Do not merge PR #6 until the cumulative V18 workflow passes.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, base64.binascii.Error) as exc:
        print(f"V17 baseline repair failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
