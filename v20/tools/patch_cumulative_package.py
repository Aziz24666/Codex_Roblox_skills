#!/usr/bin/env python3
"""Integrate V20 into a fully verified V19 cumulative package."""
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
EXPECTED_V19 = 180
EXPECTED_V20 = 185
V20_CONTRACT = """## V20 production reliability contract

- Treat the server as authority for consequential state and enforce an explicit remote allowlist, server validation, ownership/context checks, bounded payloads, and rate limits.
- Make persistence writes retry-safe, migrations deterministic/idempotent, and recovery decisions explicit; isolate tests from production data.
- Fulfill fixed-price products from server-verified receipts with idempotent exact grants; preserve the V18 no-gambling policy.
- Use staged rollouts, feature flags, a kill switch, schema compatibility, monitoring, and a data-safe rollback/forward-recovery plan.
- Track actionable service-health metrics and alerts; protect dashboards and redact personal data/secrets from logs.
- Static contracts and CI do not prove live Roblox services or production behavior; record environment-specific checks with V19 evidence rules.
"""

OLD_V19_MANIFESTS = '''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
NEW_V20_MANIFESTS = '''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V20_SHA256SUMS.txt"},
    "V20_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V20_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V19_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''

OLD_V19_V18_POLICIES = '''policies={'SHA256SUMS.txt':{'SHA256SUMS.txt','V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt'},
      'V19_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt'},
      'V18_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V14_SHA256SUMS.txt':{'V14_SHA256SUMS.txt'}}'''
NEW_V20_V18_POLICIES = '''policies={'SHA256SUMS.txt':{'SHA256SUMS.txt','V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt','V20_SHA256SUMS.txt'},
      'V20_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt','V20_SHA256SUMS.txt'},
      'V19_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt','V19_SHA256SUMS.txt'},
      'V18_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V14_SHA256SUMS.txt':{'V14_SHA256SUMS.txt'}}'''

OLD_V19_AUDIT_POLICIES = '''MANIFEST_POLICIES = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
NEW_V20_AUDIT_POLICIES = '''MANIFEST_POLICIES = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V20_SHA256SUMS.txt": {"V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''


def add_v20_contract(path: Path):
    content = path.read_text(encoding="utf-8")
    marker = "## V20 production reliability contract"
    if marker in content:
        return False
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise ValueError(f"Invalid skill frontmatter: {path}")
    path.write_text(content.rstrip() + "\n\n" + V20_CONTRACT + "\n", encoding="utf-8")
    return True


def merge_routing(root: Path):
    route_path = root / "v18/workflow/skill-routing.json"
    additions_path = root / "v20/workflow/routing-additions.json"
    routing = json.loads(route_path.read_text(encoding="utf-8"))
    additions = json.loads(additions_path.read_text(encoding="utf-8"))
    for name, extra in additions["additions"].items():
        if name not in routing["domains"]:
            raise ValueError(f"V20 cannot extend unknown routing domain: {name}")
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
        r"(?m)^EXPECTED_INSTALLED_SKILLS\s*=\s*180\s*$",
        "EXPECTED_INSTALLED_SKILLS = 185",
        content,
    )
    if count != 1:
        raise ValueError(f"Expected one V19 installed-skill count in V17 audit, found {count}")
    if content.count(OLD_V19_MANIFESTS) != 1:
        raise ValueError("Could not uniquely migrate the V19 V17-audit manifest policy")
    content = content.replace(OLD_V19_MANIFESTS, NEW_V20_MANIFESTS, 1)
    v17_audit.write_text(content, encoding="utf-8")

    v18_audit = root / "v18/tools/audit_cumulative_package.py"
    content = v18_audit.read_text(encoding="utf-8")
    content, count = re.subn(r"if len\(skills\)!=180:", "if len(skills)!=185:", content)
    if count != 1:
        raise ValueError(f"Expected one V19 skill-count check in V18 audit, found {count}")
    if content.count(OLD_V19_V18_POLICIES) != 1:
        raise ValueError("Could not uniquely migrate the V18 manifest policy to V20")
    content = content.replace(OLD_V19_V18_POLICIES, NEW_V20_V18_POLICIES, 1)
    v18_audit.write_text(content, encoding="utf-8")

    v19_audit = root / "v19/tools/audit_cumulative_package.py"
    content = v19_audit.read_text(encoding="utf-8")
    content, count = re.subn(r"(?m)^EXPECTED_SKILLS\s*=\s*180\s*$", "EXPECTED_SKILLS = 185", content)
    if count != 1:
        raise ValueError(f"Expected one V19 audit installed-skill count, found {count}")
    if content.count(OLD_V19_AUDIT_POLICIES) != 1:
        raise ValueError("Could not uniquely migrate the V19 manifest policy to V20")
    content = content.replace(OLD_V19_AUDIT_POLICIES, NEW_V20_AUDIT_POLICIES, 1)
    v19_audit.write_text(content, encoding="utf-8")


def update_agents(root: Path):
    agents = root / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    old_title = "Roblox Codex Game Studio Kit — V19 Operating Contract"
    if old_title not in content:
        raise ValueError("Could not find the V19 operating-contract title in AGENTS.md")
    content = content.replace(old_title, "Roblox Codex Game Studio Kit — V20 Operating Contract", 1)
    content = content.replace("INDEX_V19.md", "INDEX_V20.md")
    section = """

## V20 production reliability and live operations
- Keep consequential gameplay state server-authoritative; route remote changes through explicit allowlists, server-side schema/ownership/context validation, bounded payloads, and rate limits.
- Use the V20 production-contract specialist and validate project declarations with python v20/tools/v20.py validate-contract --root . --file <path>.
- Protect player data with UpdateAsync-safe transforms, bounded retries, isolated test stores, adjacent idempotent migrations, and an owner-reviewed recovery plan.
- Fulfill paid products only from verified server receipts with fixed grants and idempotent transaction records. The V18 no-gambling policy remains mandatory.
- Promote through development, staging, canary, and production with feature flags, kill-switch ownership, compatible data schemas, monitoring, and a data-safe rollback/forward-recovery plan.
- Keep production metrics actionable and logs privacy-safe. CI and static contract validation do not prove live Roblox behavior; use V19 evidence rules for real environment checks.
"""
    if "## V20 production reliability and live operations" not in content:
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


def run(command, root):
    print("$ " + " ".join(str(item) for item in command))
    subprocess.run(command, cwd=root, check=True)


def package_files(root: Path):
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )


def manifests(root: Path):
    names = [
        "SHA256SUMS.txt", "V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt",
        "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"
    ]
    paths = [root / name for name in names]
    for path in paths:
        if not path.exists():
            path.write_text("", encoding="utf-8")
    exclusions = [
        set(names),
        {"V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
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


def integrate(root: Path):
    if not (root / "AGENTS.md").is_file() or not (root / ".agents/skills").is_dir():
        raise ValueError("Target is not a reconstructed cumulative package")
    if not (root / "v19/VERSION").is_file():
        raise ValueError("Validated V19 package is required before V20 integration")
    if (root / "v20/VERSION").exists():
        raise ValueError("V20 is already integrated; use --finalize-only")
    if (root / "v19/VERSION").read_text(encoding="utf-8").strip() != "19.0.0":
        raise ValueError("Unexpected V19 package version; refusing an unreviewed baseline")

    skills_source = SOURCE / "codex-skills"
    source_names = {path.parent.name for path in skills_source.glob("*/SKILL.md")}
    if len(source_names) != 5:
        raise ValueError(f"Expected five V20 source skills, found {len(source_names)}")
    installed = root / ".agents/skills"
    collisions = sorted(name for name in source_names if (installed / name).exists())
    if collisions:
        raise ValueError(f"Refusing to overwrite inherited skills: {collisions}")

    for path in sorted(installed.glob("*/SKILL.md")):
        add_v20_contract(path)
    for version in ("v15", "v16", "v17", "v18", "v19"):
        source_dir = root / version / "codex-skills"
        if source_dir.is_dir():
            for path in sorted(source_dir.glob("*/SKILL.md")):
                add_v20_contract(path)
    for path in sorted(skills_source.glob("*/SKILL.md")):
        add_v20_contract(path)

    for folder in sorted(path for path in skills_source.iterdir() if path.is_dir()):
        shutil.copytree(folder, installed / folder.name)
    shutil.copytree(SOURCE, root / "v20")
    merge_routing(root)
    migrate_cumulative_audits(root)
    update_agents(root)

    (root / "INDEX_V20.md").write_text((REPO / "INDEX_V20.md").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "RELEASE_NOTES_V20.md").write_text((REPO / "RELEASE_NOTES_V20.md").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "INDEX.md").write_text(
        "# Current Index\n\nSee [INDEX_V20.md](INDEX_V20.md) for the current cumulative release and skill routing.\n",
        encoding="utf-8"
    )
    workflow = REPO / ".github/workflows/v20-quality.yml"
    if workflow.is_file():
        (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, root / ".github/workflows/v20-quality.yml")


def finalize(root: Path):
    removed = clean(root)
    version = (SOURCE / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"20\.\d+\.\d+", version):
        raise ValueError(f"Invalid V20 version: {version}")
    skills = list((root / ".agents/skills").glob("*/SKILL.md"))
    if len(skills) != EXPECTED_V20:
        raise ValueError(f"Expected {EXPECTED_V20} installed skills; found {len(skills)}")

    run([sys.executable, "v18/tools/v18.py", "build-registry", "--root", str(root), "--write"], root)
    run([
        sys.executable, "v19/tools/v19.py", "evaluate-routing", "--root", str(root),
        "--output", str(root / "v19/data/routing-benchmark-report.json")
    ], root)
    run([
        sys.executable, "v20/tools/v20.py", "evaluate-routing", "--root", str(root),
        "--output", str(root / "v20/data/routing-benchmark-report.json")
    ], root)
    run([
        sys.executable, "v20/tools/v20.py", "validate-contract", "--root", str(root),
        "--file", "v20/examples/production-contract.example.json"
    ], root)

    files = package_files(root)
    counts = {
        "Installed native Codex skills": len(skills),
        "V19 verification specialists": len(list((root / "v19/codex-skills").glob("*/SKILL.md"))),
        "V20 production specialists": len(list((root / "v20/codex-skills").glob("*/SKILL.md"))),
        "Markdown files": sum(path.suffix.lower() == ".md" for path in files),
        "JSON files": sum(path.suffix.lower() == ".json" for path in files),
        "Python files": sum(path.suffix.lower() == ".py" for path in files),
        "Luau files": sum(path.suffix.lower() in {".lua", ".luau"} for path in files),
        "GitHub Actions workflows": sum(".github/workflows" in path.as_posix() and path.suffix in {".yml", ".yaml"} for path in files),
        "Total regular files including five active manifests": len(files) + 1,
    }
    table = "\n".join(f"| {key} | {value} |" for key, value in counts.items())
    (root / "PACKAGE_INVENTORY.md").write_text(
        f"# Roblox Codex Game Studio Kit — V{version} Package Inventory\n\n"
        "Generated from the final cumulative package tree.\n\n"
        "| Category | Count |\n|---|---:|\n" + table +
        "\n\n## V20 additions\n"
        "- Five production reliability specialists covering server authority, player-data resilience, idempotent transactions, safe rollouts, and observability/incident response.\n"
        "- Production contract schema, example, and cross-field validator.\n"
        "- Five deterministic V20 routing regression cases.\n\n"
        "## Evidence boundary\n"
        "Static package validation does not prove Studio, live DataStore, purchase fulfillment, production telemetry, or deployment behavior.\n",
        encoding="utf-8"
    )
    (root / "README.md").write_text(
        f"""# Roblox Codex Game Studio Kit

**Current cumulative release: V{version}.** This is the complete V1–V20 package; earlier versions do not need separate downloads.

## Requirements
- Python 3.13 is the supported and CI-validated runtime.
- Install validation dependencies from the package root: python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt.

## Start with Codex
1. Extract this archive and open the extracted folder in Codex.
2. Read AGENTS.md and INDEX_V20.md.
3. Start substantial tasks with the end-to-end development orchestrator.
4. Inspect the project with python v18/tools/v18.py doctor --root .
5. Generate a risk-based verification plan with python v19/tools/v19.py plan-tests --root . --task "...".
6. Validate production declarations with python v20/tools/v20.py validate-contract --root . --file path/to/production-contract.json.
7. Run applicable tests and Studio scenarios in their real environments; record results with V19 evidence rules.

## V20 production reliability
185 native skills, including five V20 specialists for server authority, resilient player data, idempotent economy transactions, safe rollouts, and production observability. Includes a machine-readable production contract and five routing regressions. V18 no-gambling rules remain mandatory.

## Verification boundary
GitHub Actions validates the cumulative package, schemas, regressions, routing, checksums, and archives. It does not launch Roblox Studio or prove live DataStore, receipt fulfillment, production alerting, deployment, or rollback behavior. Static contract validation is not a runtime test.

## License
MIT. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
""",
        encoding="utf-8"
    )
    checksum_counts = manifests(root)
    run([sys.executable, "v20/tools/audit_cumulative_package.py", "--root", str(root)], root)
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
    print(f"V20 package integration passed: {len(list((root/'.agents/skills').glob('*/SKILL.md')))} skills")


if __name__ == "__main__":
    raise SystemExit(main())
