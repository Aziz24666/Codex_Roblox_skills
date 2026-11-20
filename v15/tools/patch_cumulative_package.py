#!/usr/bin/env python3
"""Apply the V15 overlay to a reconstructed V14 package and verify its integrity."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package_readme(version: str, skill_count: int) -> str:
    return f"""# Roblox Codex Game Studio Kit

**Current cumulative release: V{version}.** This package contains the complete V1–V14 toolkit plus the V15 project-aware development and verification layer. Earlier versions do not need separate downloads.

## Included

- **{skill_count} native Codex skills** in .agents/skills/, including eight V15 skills for project intelligence, skill orchestration, acceptance-driven implementation, remote security, persistence migrations, performance regression, runtime evidence, and reproducible releases.
- Reusable Luau systems, data-driven gameplay patterns, server/client architecture guidance, UI and content workflows, Studio tooling, templates, examples, schemas, and quality automation.
- The V14 Studio Test Runner plugin, disposable multi-client fixture, scenario catalog, and evidence/report utilities.
- V15 project manifest, task evaluation, runtime evidence schemas, examples, validator, package-integrity tooling, and implementation/quality-gate references.

## Quick start

1. Download the ZIP or TAR.XZ asset from the V{version} GitHub Release.
2. Extract the archive and open the extracted package root in Codex.
3. Read AGENTS.md and INDEX_V15.md.
4. Start whole-game or cross-system work with $roblox-game-builder.
5. Use $roblox-project-intelligence before substantial changes to an existing game.
6. Load only the specialist skills relevant to the task.

## V15 validation

From the extracted package root, run:

    python v15/tools/v15_validate.py --root v15
    python -m unittest discover -s v15/tests -v
    python tools/v14_pack_doctor.py .
    python -m pip install --requirement requirements-ci.txt
    python v15/tools/audit_cumulative_package.py --root .
    sha256sum --check SHA256SUMS.txt
    sha256sum --check V14_SHA256SUMS.txt
    sha256sum --check V15_SHA256SUMS.txt

## Studio and runtime evidence

The V14 Test Runner plugin and disposable fixture require execution inside Roblox Studio. CI compilation and Rojo builds do not launch Studio playtests. Device simulation is not physical-device testing, and a local mock is not a live DataStore or production-service test. Use NOT_RUN or BLOCKED for checks that were not executed.

## Package integrity manifests

`SHA256SUMS.txt` covers the complete current package except itself. `V14_SHA256SUMS.txt` and `V15_SHA256SUMS.txt` are the current version-layer manifests and omit the generic root manifest to avoid checksum cycles. V6–V13 manifests are historical snapshots; use the three current manifests above for this release.

## Release and provenance

GitHub Actions validates all installed skill YAML frontmatter, V15 metadata/contracts, schemas and examples, runs regression tests, compiles Python, reconstructs the cumulative V14 package, applies V15, runs the cumulative package audit, generates package inventory and all three current checksum manifests, and builds ZIP/TAR.XZ archives. The V14 workflow separately compiles Luau and builds the sample experience, Content Factory plugin, Test Runner plugin, and disposable test fixture.

## License and affiliation

Released under the MIT License. Roblox, Roblox Studio, and Luau are trademarks or projects of their respective owners. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
"""

def update_agents(package_root: Path) -> None:
    path = package_root / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("Roblox Codex Game Studio Kit — V14 Operating Contract",
                        "Roblox Codex Game Studio Kit — V15 Operating Contract", 1)
    text = text.replace("INDEX_V13.md", "INDEX_V15.md")
    chunks = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    seen, kept = set(), []
    for chunk in chunks:
        normalized = chunk.strip()
        if normalized and normalized in seen:
            continue
        if normalized:
            seen.add(normalized)
        kept.append(chunk)
    text = "".join(kept).rstrip()
    if "## V15 project-aware implementation and verification" not in text:
        text += """

## V15 project-aware implementation and verification
- Read INDEX_V15.md and inspect the real project before changing source.
- Use $roblox-project-intelligence to map source of truth, architecture, entry points, and verified toolchain.
- Use $roblox-skill-selection-orchestration to select the smallest relevant specialist set.
- Define observable acceptance criteria before substantial implementation; implement one complete vertical slice at a time.
- Apply V15 security, persistence, and performance skills when those boundaries are touched.
- Separate static, compiler/build, automated-test, Studio, simulator, physical-device, staging, and production evidence.
- Never report an unexecuted check as PASS. Record environment, build identity, scenario, logs/artifacts, status, and limitations.
- Use synthetic and isolated persistence fixtures. Ask before touching live player data, production services, or public assets.
- Read v15/docs/IMPLEMENTATION_PIPELINE.md and v15/docs/QUALITY_GATES.md for the full workflow.
"""
    path.write_text(text + "\n", encoding="utf-8")


def clean_generated_python_artifacts(package_root: Path) -> int:
    """Remove interpreter caches so generated bytecode never ships in release archives."""
    removed = 0
    for path in sorted(package_root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and path.name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            shutil.rmtree(path)
            removed += 1
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            path.unlink()
            removed += 1
    return removed


def normalize_invalid_skill_descriptions(package_root: Path) -> int:
    """Quote plain YAML descriptions containing a colon-space sequence."""
    changed = 0
    skill_root = package_root / ".agents" / "skills"
    for path in sorted(skill_root.glob("*/SKILL.md")):
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            raise ValueError(f"{path}: missing YAML frontmatter opener")
        end = content.find("\n---\n", 4)
        if end < 0:
            raise ValueError(f"{path}: missing YAML frontmatter closer")
        front = content[4:end]
        lines = front.splitlines()
        updated = []
        for line in lines:
            match = re.match(r"^(description:\s*)(.*)$", line)
            if match and ": " in match.group(2) and not match.group(2).startswith(('"', "'", "|", ">")):
                line = match.group(1) + json.dumps(match.group(2), ensure_ascii=False)
                changed += 1
            updated.append(line)
        if updated != lines:
            path.write_text(content[:4] + "\n".join(updated) + content[end:], encoding="utf-8")
    return changed


def generate_inventory_and_checksums(package_root: Path, version: str) -> None:
    inventory_path = package_root / "PACKAGE_INVENTORY.md"
    root_sums = package_root / "SHA256SUMS.txt"
    v14_sums = package_root / "V14_SHA256SUMS.txt"
    v15_sums = package_root / "V15_SHA256SUMS.txt"
    for manifest in (root_sums, v14_sums, v15_sums):
        if not manifest.exists():
            manifest.write_text("", encoding="utf-8")
    excluded_dirs = {".git", "__pycache__", "node_modules", ".venv"}
    files = sorted(p for p in package_root.rglob("*") if p.is_file()
                   and not any(part in excluded_dirs for part in p.parts))
    skill_count = len(list((package_root / ".agents" / "skills").glob("*/SKILL.md")))
    total = len(files)
    counts = {
        "Installed native Codex skills": skill_count,
        "Documentation Markdown files in docs/": len(list((package_root / "docs").rglob("*.md"))),
        "All Markdown files": len(list(package_root.rglob("*.md"))),
        "Prompt files": len([p for p in (package_root / "prompts").rglob("*") if p.is_file()]),
        "Template files": len([p for p in (package_root / "templates").rglob("*") if p.is_file()]),
        "Top-level JSON schemas": len(list((package_root / "schemas").glob("*.schema.json"))),
        "JSON files total": len(list(package_root.rglob("*.json"))),
        "Top-level Python tools": len(list((package_root / "tools").glob("*.py"))),
        "Python files total": len(list(package_root.rglob("*.py"))),
        "Luau source files": len([p for p in package_root.rglob("*") if p.suffix.lower() in {".lua", ".luau"}]),
        "Active GitHub Actions workflows": len(list((package_root / ".github" / "workflows").glob("*.yml"))) + len(list((package_root / ".github" / "workflows").glob("*.yaml"))),
        "Total regular files (including three current checksum manifests)": total,
        "Root SHA256SUMS.txt entries": total - 1,
        "V14_SHA256SUMS.txt entries": total - 2,
        "V15_SHA256SUMS.txt entries": total - 3,
    }
    rows = "\n".join(f"| {label} | {value} |" for label, value in counts.items())
    inventory = f"""# Roblox Codex Game Studio Kit — V{version} Package Inventory

This inventory is generated from the final cumulative package tree. Counts exclude .git, __pycache__, node_modules, and .venv.

## Verified package counts

| Category | Count |
|---|---:|
{rows}

## V15 additions
- Eight native Codex skills copied into .agents/skills/.
- Project manifest, task evaluation, runtime evidence, and legacy V9 collection-schema contracts and examples.
- V15 validator, cumulative-package audit, regression suite, package integration tool, and three current checksum manifests.
- V15 index, implementation pipeline, package-integrity guide, and quality-gate documentation.

## Evidence boundary
File integrity and static validation do not prove Roblox Studio runtime behavior. Studio playtests, multiplayer execution, device checks, live DataStore behavior, asset permissions, and production operations require separate execution and evidence.
"""
    inventory_path.write_text(inventory, encoding="utf-8")

    def write_manifest(path: Path, excluded_manifests: set[Path]) -> int:
        entries = []
        for target in sorted(p for p in package_root.rglob("*") if p.is_file()
                              and p not in excluded_manifests
                              and not any(part in excluded_dirs for part in p.parts)):
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            entries.append(f"{digest}  {target.relative_to(package_root).as_posix()}")
        path.write_text("\n".join(entries) + "\n", encoding="utf-8")
        for entry in entries:
            digest, rel = entry.split("  ", 1)
            target = package_root / rel
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum verification failed: {rel}")
        return len(entries)

    # Avoid cycles:
    # V15 excludes V14/V15/root; V14 excludes V14/root; root covers V14 and V15.
    v15_count = write_manifest(v15_sums, {v14_sums, v15_sums, root_sums})
    v14_count = write_manifest(v14_sums, {v14_sums, root_sums})
    root_count = write_manifest(root_sums, {root_sums})
    expected = {
        "Root SHA256SUMS.txt entries": total - 1,
        "V14_SHA256SUMS.txt entries": total - 2,
        "V15_SHA256SUMS.txt entries": total - 3,
    }
    actual = {
        "Root SHA256SUMS.txt entries": root_count,
        "V14_SHA256SUMS.txt entries": v14_count,
        "V15_SHA256SUMS.txt entries": v15_count,
    }
    if actual != expected:
        raise ValueError(f"Checksum entry counts do not match package inventory: {actual} != {expected}")
    print(f"Generated inventory for {total} files; verified root={root_count}, V14={v14_count}, V15={v15_count} SHA-256 entries.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    args = parser.parse_args()
    package_root = args.package_root.resolve()
    if not (package_root / "AGENTS.md").is_file() or not (package_root / ".agents" / "skills").is_dir():
        raise SystemExit(f"Not a reconstructed cumulative package: {package_root}")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"15\.\d+\.\d+", version):
        raise ValueError(f"Expected stable V15 semantic version; got {version!r}")
    target_skills = package_root / ".agents" / "skills"
    for source in sorted((ROOT / "codex-skills").iterdir()):
        if source.is_dir():
            shutil.copytree(source, target_skills / source.name, dirs_exist_ok=True)
    shutil.copy2(ROOT / "INDEX_V15.md", package_root / "INDEX_V15.md")
    shutil.copy2(ROOT / "schemas" / "v9-editor-field-descriptors.schema.json", package_root / "schemas" / "v9-editor-field-descriptors.schema.json")
    shutil.copy2(ROOT / "examples" / "v9-editor-field-descriptors.example.json", package_root / "schemas" / "examples" / "v9-editor-field-descriptors.example.json")
    shutil.copy2(ROOT / "docs" / "PACKAGE_INTEGRITY.md", package_root / "docs" / "PACKAGE_INTEGRITY.md")
    skill_descriptions_fixed = normalize_invalid_skill_descriptions(package_root)
    print(f"Quoted {skill_descriptions_fixed} YAML skill descriptions requiring explicit quoting.")
    removed = clean_generated_python_artifacts(package_root)
    print(f"Removed {removed} generated Python cache entries before checksumming.")
    update_agents(package_root)
    (package_root / "README.md").write_text(package_readme(version, len(list((package_root / ".agents" / "skills").rglob("SKILL.md")))), encoding="utf-8")
    generate_inventory_and_checksums(package_root, version)
    print(f"V{version} cumulative package integration passed.")


if __name__ == "__main__":
    main()
