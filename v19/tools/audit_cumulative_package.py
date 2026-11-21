#!/usr/bin/env python3
"""Audit V19 cumulative skills, routing, evidence schemas, and hierarchical manifests."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

EXPECTED_SKILLS = 180
EXPECTED_V19_SKILLS = 5
V18_CONTRACT = "## V18 shared workflow and handoff contract"
V19_CONTRACT = "## V19 verification and evaluation contract"
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "target", "build"}
MANIFEST_POLICIES = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V19_SHA256SUMS.txt": {"V19_SHA256SUMS.txt", "V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V18_SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}


def load_v18(root: Path):
    path = root / "v18/tools/v18.py"
    spec = importlib.util.spec_from_file_location("v18_for_v19_audit", path)
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
    if len(skills) != EXPECTED_SKILLS:
        raise SystemExit(f"Expected {EXPECTED_SKILLS} installed skills, found {len(skills)}")
    source_skills = sorted((root / "v19/codex-skills").glob("*/SKILL.md"))
    if len(source_skills) != EXPECTED_V19_SKILLS:
        raise SystemExit(f"Expected {EXPECTED_V19_SKILLS} V19 source skills, found {len(source_skills)}")
    installed = {path.parent.name: path for path in skills}
    for path in skills:
        content = path.read_text(encoding="utf-8")
        if V18_CONTRACT not in content or V19_CONTRACT not in content:
            raise SystemExit(f"Missing V18/V19 contract: {path}")
    for path in source_skills:
        installed_path = installed.get(path.parent.name)
        if installed_path is None or installed_path.read_bytes() != path.read_bytes():
            raise SystemExit(f"V19 source/install mismatch: {path.parent.name}")

    router = load_v18(root)
    report = router.validate(root)
    if report["installed_skills"] != EXPECTED_SKILLS:
        raise SystemExit("V18 shared validator returned an unexpected installed-skill count")

    import jsonschema
    for schema_path in sorted((root / "v19/schemas").glob("*.schema.json")):
        jsonschema.Draft202012Validator.check_schema(json.loads(schema_path.read_text(encoding="utf-8")))

    benchmark_path = root / "v19/data/routing-benchmark-report.json"
    if not benchmark_path.is_file():
        raise SystemExit("Missing generated V19 routing benchmark report")
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if benchmark.get("status") != "PASS" or benchmark.get("summary", {}).get("failed_cases") != 0:
        raise SystemExit("V19 routing benchmark report has failing cases")

    paths = sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )
    if any(path.suffix in {".pyc", ".pyo"} for path in paths):
        raise SystemExit("Compiled Python bytecode remains in the release tree")
    counts = check_manifests(root)
    print("Cumulative V19 audit passed.")
    print(json.dumps({
        "installed_skills": len(skills),
        "v19_skills": len(source_skills),
        "routing_benchmark": benchmark["summary"],
        "schemas": len(list((root / "v19/schemas").glob("*.schema.json"))),
        "manifests": counts,
        "files": len(paths),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
