#!/usr/bin/env python3
"""Apply the V15 overlay to a reconstructed V14 package and verify its integrity."""
from __future__ import annotations
import argparse
import hashlib
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
    sha256sum --check V15_SHA256SUMS.txt

## Studio and runtime evidence

The V14 Test Runner plugin and disposable fixture require execution inside Roblox Studio. CI compilation and Rojo builds do not launch Studio playtests. Device simulation is not physical-device testing, and a local mock is not a live DataStore or production-service test. Use NOT_RUN or BLOCKED for checks that were not executed.

## Release and provenance

GitHub Actions validates V15 metadata/contracts, runs regression tests, compiles Python, reconstructs the cumulative V14 package, applies V15, generates package inventory and both checksum manifests, and builds ZIP/TAR.XZ archives. The V14 workflow separately compiles Luau and builds the sample experience, Content Factory plugin, Test Runner plugin, and disposable test fixture.

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


def generate_inventory_and_checksums(package_root: Path, version: str) -> None:
    inventory_path = package_root / "PACKAGE_INVENTORY.md"
    v14_sums = package_root / "V14_SHA256SUMS.txt"
    v15_sums = package_root / "V15_SHA256SUMS.txt"
    for manifest in (v14_sums, v15_sums):
        if not manifest.exists():
            manifest.write_text("", encoding="utf-8")
    excluded = {".git", "__pycache__", "node_modules", ".venv"}
    files = sorted(p for p in package_root.rglob("*") if p.is_file()
                   and not any(part in excluded for part in p.parts))
    skill_count = len(list((package_root / ".agents" / "skills").rglob("SKILL.md")))
    counts = {
        "Specialist skills (SKILL.md)": skill_count,
        "Documentation Markdown files in docs/": len(list((package_root / "docs").rglob("*.md"))),
        "All Markdown files": len(list(package_root.rglob("*.md"))),
        "Prompt files": len([p for p in (package_root / "prompts").rglob("*") if p.is_file()]),
        "Template files": len([p for p in (package_root / "templates").rglob("*") if p.is_file()]),
        "Top-level JSON schemas": len(list((package_root / "schemas").glob("*.json"))),
        "JSON files total": len(list(package_root.rglob("*.json"))),
        "Top-level Python tools": len(list((package_root / "tools").glob("*.py"))),
        "Python files total": len(list(package_root.rglob("*.py"))),
        "Luau source files": len([p for p in package_root.rglob("*") if p.suffix.lower() in {".lua", ".luau"}]),
        "Active GitHub Actions workflows": len(list((package_root / ".github" / "workflows").glob("*.yml"))) + len(list((package_root / ".github" / "workflows").glob("*.yaml"))),
        "Total regular files (including both checksum manifests)": len(files),
        "V14 SHA-256 manifest entries": len(files) - 1,
        "V15 SHA-256 manifest entries": len(files) - 2,
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
- Project manifest, task evaluation, and runtime evidence contracts and examples.
- V15 validator, regression suite, package integration tool, and dual checksum manifests.
- V15 index, implementation pipeline, and quality-gate documentation.

## Evidence boundary
File integrity and Python/schema validation do not prove Roblox Studio runtime behavior. Studio playtests, multiplayer execution, device checks, live DataStore behavior, asset permissions, and production operations require separate execution and evidence.
"""
    inventory_path.write_text(inventory, encoding="utf-8")
    # Avoid circular checksums: V15 omits both manifests; V14 includes V15's manifest.
    def write_manifest(path: Path, excluded_manifests: set[Path]) -> int:
        entries = []
        for target in sorted(p for p in package_root.rglob("*") if p.is_file()
                              and p not in excluded_manifests
                              and not any(part in excluded for part in p.parts)):
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            entries.append(f"{digest}  {target.relative_to(package_root).as_posix()}")
        path.write_text("\n".join(entries) + "\n", encoding="utf-8")
        for entry in entries:
            digest, rel = entry.split("  ", 1)
            target = package_root / rel
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum verification failed: {rel}")
        return len(entries)
    v15_count = write_manifest(v15_sums, {v14_sums, v15_sums})
    v14_count = write_manifest(v14_sums, {v14_sums})
    if v15_count != counts["V15 SHA-256 manifest entries"] or v14_count != counts["V14 SHA-256 manifest entries"]:
        raise ValueError("Checksum entry count does not match package inventory")
    print(f"Generated inventory for {len(files)} files; verified {v14_count} V14 and {v15_count} V15 SHA-256 entries.")

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
    update_agents(package_root)
    (package_root / "README.md").write_text(package_readme(version, len(list((package_root / ".agents" / "skills").rglob("SKILL.md")))), encoding="utf-8")
    generate_inventory_and_checksums(package_root, version)
    print(f"V{version} cumulative package integration passed.")


if __name__ == "__main__":
    main()
