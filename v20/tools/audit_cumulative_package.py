#!/usr/bin/env python3
"""Audit V20 cumulative skills, schemas, routing benchmark, and checksum hierarchy."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

EXPECTED_SKILLS = 185
EXPECTED_V20_SKILLS = 5
CONTRACTS = (
    "## V18 shared workflow and handoff contract",
    "## V19 verification and evaluation contract",
    "## V20 production reliability contract",
)
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "target", "build"}
MANIFEST_POLICIES = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V20_SHA256SUMS.txt": {"V20_SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}


def load_v18(root: Path):
    path = root / "v18/tools/v18.py"
    spec = importlib.util.spec_from_file_location("v18_for_v20_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load V18 validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_manifests(root: Path):
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )
    expected_files = {path.relative_to(root).as_posix() for path in files}
    counts = {}
    for name, excluded in MANIFEST_POLICIES.items():
        manifest = root / name
        if not manifest.is_file():
            raise ValueError(f"Missing manifest: {name}")
        seen = set()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            if relative in seen:
                raise ValueError(f"Duplicate checksum row: {relative}")
            seen.add(relative)
            target = root / relative
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum mismatch: {relative}")
        expected = {relative for relative in expected_files if Path(relative).name not in excluded}
        if seen != expected:
            raise ValueError(f"{name} coverage mismatch: missing={len(expected-seen)}, extra={len(seen-expected)}")
        counts[name] = len(seen)
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args().root.resolve()
    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    source_skills = sorted((root / "v20/codex-skills").glob("*/SKILL.md"))
    if len(skills) != EXPECTED_SKILLS:
        raise SystemExit(f"Expected {EXPECTED_SKILLS} installed skills, found {len(skills)}")
    if len(source_skills) != EXPECTED_V20_SKILLS:
        raise SystemExit(f"Expected {EXPECTED_V20_SKILLS} V20 source skills, found {len(source_skills)}")
    installed = {path.parent.name: path for path in skills}
    for path in skills:
        content = path.read_text(encoding="utf-8")
        if any(marker not in content for marker in CONTRACTS):
            raise SystemExit(f"Missing V18/V19/V20 contract: {path}")
    for path in source_skills:
        installed_path = installed.get(path.parent.name)
        if installed_path is None or installed_path.read_bytes() != path.read_bytes():
            raise SystemExit(f"V20 source/install mismatch: {path.parent.name}")

    router = load_v18(root)
    report = router.validate(root)
    if report["installed_skills"] != EXPECTED_SKILLS:
        raise SystemExit("V18 shared validator returned an unexpected installed-skill count")

    import jsonschema
    for schema_path in sorted((root / "v20/schemas").glob("*.schema.json")):
        jsonschema.Draft202012Validator.check_schema(json.loads(schema_path.read_text(encoding="utf-8")))

    benchmark_path = root / "v20/data/routing-benchmark-report.json"
    if not benchmark_path.is_file():
        raise SystemExit("Missing generated V20 routing benchmark report")
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if benchmark.get("status") != "PASS" or benchmark.get("summary", {}).get("failed_cases") != 0:
        raise SystemExit("V20 routing benchmark report has failing cases")

    example_path = root / "v20/examples/production-contract.example.json"
    from importlib.util import spec_from_file_location, module_from_spec
    cli_spec = spec_from_file_location("v20_for_audit", root / "v20/tools/v20.py")
    cli = module_from_spec(cli_spec)
    cli_spec.loader.exec_module(cli)
    cli.validate_contract(root, example_path)

    paths = sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )
    if any(path.suffix in {".pyc", ".pyo"} for path in paths):
        raise SystemExit("Compiled Python bytecode remains in the release tree")
    counts = check_manifests(root)
    print("Cumulative V20 audit passed.")
    print(json.dumps({
        "installed_skills": len(skills),
        "v20_skills": len(source_skills),
        "routing_benchmark": benchmark["summary"],
        "production_contract": "PASS",
        "schemas": len(list((root / "v20/schemas").glob("*.schema.json"))),
        "manifests": counts,
        "files": len(paths)
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
