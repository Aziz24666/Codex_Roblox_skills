#!/usr/bin/env python3
"""Integrate V19 into the validated V18 cumulative package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
REPO = SOURCE.parent
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "target", "build"}
EXPECTED_V18 = 175
EXPECTED_V19 = 180
V19_CONTRACT = """## V19 verification and evaluation contract

- Select verification from changed paths, impacted systems, trust boundaries, and failure impact; do not run or report unrelated checks as proof.
- Separate formatting, static analysis, unit, contract, integration, Studio, multi-client, device, performance, persistence, economy, and live-service checks.
- A plan is not an execution result. Preserve NOT_RUN and BLOCKED states for checks that did not run.
- A PASS requires the exact command or scenario, named environment, tool/runtime version, build identity, expected behavior, observed behavior, and a non-empty inspectable evidence artifact.
- Keep failures visible. Do not weaken acceptance criteria, delete negative benchmark cases, or convert a failed check into a pass.
- Deterministic routing benchmarks measure router behavior only; they do not prove model reasoning quality, skill compliance, or game correctness.
"""

OLD_V17_MANIFESTS = '''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
NEW_V19_MANIFESTS = '''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
OLD_V18_POLICIES = '''policies={'SHA256SUMS.txt':{'SHA256SUMS.txt','V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V18_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V14_SHA256SUMS.txt':{'V14_SHA256SUMS.txt'}}'''
NEW_V19_POLICIES = '''policies={'SHA256SUMS.txt':{'SHA256SUMS.txt','V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt'},
      'V19_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt'},
      'V18_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V14_SHA256SUMS.txt':{'V14_SHA256SUMS.txt'}}'''


def add_v19_contract(path: Path):
    content = path.read_text(encoding="utf-8")
    marker = "## V19 verification and evaluation contract"
    if marker in content:
        return False
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise ValueError(f"Invalid skill frontmatter: {path}")
    path.write_text(content.rstrip() + "\n\n" + V19_CONTRACT + "\n", encoding="utf-8")
    return True


def merge_routing(root: Path):
    route_path = root / "v18/workflow/skill-routing.json"
    additions_path = root / "v19/workflow/routing-additions.json"
    routing = json.loads(route_path.read_text(encoding="utf-8"))
    additions = json.loads(additions_path.read_text(encoding="utf-8"))
    for name, extra in additions["additions"].items():
        if name not in routing["domains"]:
            raise ValueError(f"V19 cannot extend unknown routing domain: {name}")
        current = routing["domains"][name]
        for signal in extra.get("signals", []):
            if signal not in current["signals"]:
                current["signals"].append(signal)
        for skill in extra.get("skills", []):
            if skill not in current["skills"]:
                current["skills"].insert(0, skill)
    route_path.write_text(json.dumps(routing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def migrate_cumulative_audits(root: Path):
    v17_audit = root / "v17/tools/audit_cumulative_package.py"
    content = v17_audit.read_text(encoding="utf-8")
    content, count = re.subn(
        r"(?m)^EXPECTED_INSTALLED_SKILLS\s*=\s*175\s*$",
        "EXPECTED_INSTALLED_SKILLS = 180",
        content,
    )
    if count != 1:
        raise ValueError(f"Expected one V18 installed-skill count in V17 audit, found {count}")
    if content.count(OLD_V17_MANIFESTS) != 1:
        raise ValueError("Could not uniquely migrate the inherited V17 manifest policy to V19")
    content = content.replace(OLD_V17_MANIFESTS, NEW_V19_MANIFESTS, 1)
    v17_audit.write_text(content, encoding="utf-8")

    v18_audit = root / "v18/tools/audit_cumulative_package.py"
    content = v18_audit.read_text(encoding="utf-8")
    content, count = re.subn(r"if len\(skills\)!=175:", "if len(skills)!=180:", content)
    if count != 1:
        raise ValueError(f"Expected one V18 audit skill-count check, found {count}")
    if content.count(OLD_V18_POLICIES) != 1:
        raise ValueError("Could not uniquely migrate the V18 manifest policy to V19")
    content = content.replace(OLD_V18_POLICIES, NEW_V19_POLICIES, 1)
    v18_audit.write_text(content, encoding="utf-8")


def update_agents(root: Path):
    agents = root / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("Roblox Codex Game Studio Kit — V18 Operating Contract",
                              "Roblox Codex Game Studio Kit — V19 Operating Contract", 1)
    content = content.replace("INDEX_V18.md", "INDEX_V19.md")
    section = """

## V19 testing intelligence and evidence
- Create a risk-based verification matrix with the V19 test-planning specialist and python v19/tools/v19.py plan-tests --root . --task "...".
- Use the Luau static-analysis specialist for configured Luau type checks, lint, and formatting. Adopt strict typing incrementally and preserve the project's actual analyzer configuration.
- Use the Studio multiplayer test specialist when behavior depends on multiple clients, player lifecycle, replication, matchmaking, or join/leave behavior.
- Run python v19/tools/v19.py evaluate-routing --root . after routing changes. This is a deterministic router regression benchmark, not an LLM-quality score.
- Validate verification packets with the V19 evidence-auditing specialist and python v19/tools/v19.py validate-evidence --root . --file <path>.
- Plans are not test results. Record PASS only with a real execution, exact environment/tool version, expected and actual outcomes, build identity, and inspectable evidence.
- Keep Studio, multi-client, device, performance, persistence, purchase, and live-service checks NOT_RUN or BLOCKED until they are run in their real authorized environment.
"""
    if "## V19 testing intelligence and evidence" not in content:
        content = content.rstrip() + section
    agents.write_text(content.rstrip() + "\n", encoding="utf-8")


def clean(root: Path):
    removed = 0
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir() and path.name in EXCLUDED:
            shutil.rmtree(path)
            removed += 1
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            path.unlink()
            removed += 1
    return removed


def integrate(root: Path):
    if not (root / "AGENTS.md").is_file() or not (root / ".agents/skills").is_dir():
        raise ValueError("Target is not a reconstructed cumulative package")
    if not (root / "v18/VERSION").is_file():
        raise ValueError("Validated V18 package is required before V19 integration")
    if (root / "v19/VERSION").exists():
        raise ValueError("V19 is already integrated; use --finalize-only")
    if (root / "v18/VERSION").read_text(encoding="utf-8").strip() != "18.0.1":
        raise ValueError("Unexpected V18 package version; refusing an unreviewed baseline")
    skills_source = SOURCE / "codex-skills"
    source_names = {p.parent.name for p in skills_source.glob("*/SKILL.md")}
    if len(source_names) != 5:
        raise ValueError(f"Expected five V19 source skills, found {len(source_names)}")
    installed = root / ".agents/skills"
    collisions = sorted(name for name in source_names if (installed / name).exists())
    if collisions:
        raise ValueError(f"Refusing to overwrite inherited skills: {collisions}")

    # Keep current source and installed copies identical while adding the V19 contract.
    for path in sorted(installed.glob("*/SKILL.md")):
        add_v19_contract(path)
    for version in ("v15", "v16", "v17", "v18"):
        source_dir = root / version / "codex-skills"
        if source_dir.is_dir():
            for path in sorted(source_dir.glob("*/SKILL.md")):
                add_v19_contract(path)

    for folder in sorted(path for path in skills_source.iterdir() if path.is_dir()):
        shutil.copytree(folder, installed / folder.name)
    shutil.copytree(SOURCE, root / "v19")
    merge_routing(root)
    migrate_cumulative_audits(root)
    update_agents(root)

    (root / "INDEX_V19.md").write_text((REPO / "INDEX_V19.md").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "RELEASE_NOTES_V19.md").write_text((REPO / "RELEASE_NOTES_V19.md").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "INDEX.md").write_text(
        "# Current Index\n\nSee [INDEX_V19.md](INDEX_V19.md) for the current cumulative release and skill routing.\n",
        encoding="utf-8",
    )
    workflow = REPO / ".github/workflows/v19-quality.yml"
    if workflow.is_file():
        (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, root / ".github/workflows/v19-quality.yml")


def package_files(root: Path):
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )


def manifests(root: Path):
    names = ["SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"]
    paths = [root / name for name in names]
    for path in paths:
        if not path.exists():
            path.write_text("", encoding="utf-8")
    exclusions = [
        set(names),
        {"V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
        {"V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
        {"V14_SHA256SUMS.txt"},
    ]
    files = package_files(root)
    counts = {}
    for path, excluded in zip(paths, exclusions):
        rows = [
            hashlib.sha256(file.read_bytes()).hexdigest() + "  " + file.relative_to(root).as_posix()
            for file in files if file.name not in excluded
        ]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        counts[path.name] = len(rows)
        for row in rows:
            digest, relative = row.split("  ", 1)
            if hashlib.sha256((root / relative).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum verification failed: {relative}")
    return counts


def finalize(root: Path):
    removed = clean(root)
    version = (SOURCE / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"19\.\d+\.\d+", version):
        raise ValueError(f"Invalid V19 version: {version}")
    skills = list((root / ".agents/skills").glob("*/SKILL.md"))
    if len(skills) != EXPECTED_V19:
        raise ValueError(f"Expected {EXPECTED_V19} installed skills; found {len(skills)}")

    subprocess.run(
        [sys.executable, "v18/tools/v18.py", "build-registry", "--root", str(root), "--write"],
        cwd=root, check=True,
    )
    report = root / "v19/data/routing-benchmark-report.json"
    subprocess.run(
        [sys.executable, "v19/tools/v19.py", "evaluate-routing", "--root", str(root),
         "--output", str(report)],
        cwd=root, check=True, stdout=subprocess.DEVNULL,
    )
    if json.loads(report.read_text(encoding="utf-8"))["status"] != "PASS":
        raise ValueError("V19 routing benchmark did not pass")

    files = package_files(root)
    counts = {
        "Installed native Codex skills": len(skills),
        "V19 specialist skills": len(list((root / "v19/codex-skills").glob("*/SKILL.md"))),
        "Markdown files": sum(path.suffix.lower() == ".md" for path in files),
        "JSON files": sum(path.suffix.lower() == ".json" for path in files),
        "Python files": sum(path.suffix.lower() == ".py" for path in files),
        "Luau files": sum(path.suffix.lower() in {".lua", ".luau"} for path in files),
        "GitHub Actions workflows": sum(".github/workflows" in path.as_posix() and path.suffix in {".yml", ".yaml"} for path in files),
        "Total regular files including four active manifests": len(files) + 4,
    }
    table = "\n".join(f"| {key} | {value} |" for key, value in counts.items())
    (root / "PACKAGE_INVENTORY.md").write_text(
        f"# Roblox Codex Game Studio Kit — V{version} Package Inventory\n\n"
        "Generated from the final cumulative package tree.\n\n"
        "| Category | Count |\n|---|---:|\n" + table +
        "\n\n## V19 additions\n"
        "- Five verification specialists for risk-based test planning, Luau static analysis, Studio multi-client testing, routing benchmarks, and evidence auditing.\n"
        "- Deterministic routing benchmark corpus with positive and negative regression cases.\n"
        "- CLI verification-plan generator and evidence validator.\n"
        "- StudioTestService and Studio MCP workflows with explicit runtime/CI boundaries.\n\n"
        "## Evidence boundary\n"
        "Static/package validation does not prove Roblox Studio, multiplayer, device, live DataStore, purchase fulfillment, asset permission, or production behavior.\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        f"""# Roblox Codex Game Studio Kit

**Current cumulative release: V{version}.** This is the complete V1–V19 package; earlier versions do not need separate downloads.

## Requirements
- Python 3.13 is the supported and CI-validated runtime. The inherited package uses tomllib (standard library since Python 3.11).
- Install validation dependencies from the package root: python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt.

## Start with Codex
1. Extract this archive and open the extracted folder in Codex.
2. Read AGENTS.md and INDEX_V19.md.
3. Start substantial tasks with the end-to-end development orchestrator.
4. Inspect the project with python v18/tools/v18.py doctor --root .
5. Generate a test plan with python v19/tools/v19.py plan-tests --root . --task "..."
6. Run applicable project checks and Studio scenarios in their real environments.
7. Validate evidence with python v19/tools/v19.py validate-evidence --root . --file <path>.

## V19 testing intelligence
180 native skills; five V19 verification specialists; risk-based test-plan generation; Luau static-analysis/type-safety guidance; Studio multi-client testing playbooks; deterministic routing benchmarks; and evidence validation. The benchmark measures deterministic router behavior only, not LLM quality or game correctness.

## Verification
Run python v18/tools/v18.py validate --root . and python v19/tools/v19.py verify --root .. GitHub Actions validates package logic, tests, schemas, routing, checksums, and archives. It does not launch Roblox Studio or prove device, multiplayer, live-service, or production behavior.

## License
MIT. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
""",
        encoding="utf-8",
    )
    checksum_counts = manifests(root)
    print(f"Removed {removed} cache entries; skills={len(skills)}; checksums={checksum_counts}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--finalize-only", action="store_true")
    args = parser.parse_args()
    root = args.package_root.resolve()
    if not args.finalize_only:
        integrate(root)
    finalize(root)
    print(f"V19 package integration passed: {len(list((root/'.agents/skills').glob('*/SKILL.md')))} skills")


if __name__ == "__main__":
    main()
