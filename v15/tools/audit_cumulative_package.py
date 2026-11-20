#!/usr/bin/env python3
"""Deep static audit for the assembled cumulative Roblox Codex package."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

import jsonschema
import yaml
from referencing import Registry, Resource

CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt"},
    "V15_SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V15_SHA256SUMS.txt"},
}
EXPECTED_SKILL_COUNT = 143
EXPECTED_V15_SKILLS = {
    "roblox-project-intelligence",
    "roblox-skill-selection-orchestration",
    "roblox-acceptance-driven-implementation",
    "roblox-remote-security-review",
    "roblox-persistence-migration-testing",
    "roblox-performance-regression-testing",
    "roblox-runtime-evidence-triage",
    "roblox-reproducible-release-engineering",
}


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_manifest(root: Path, manifest_name: str, excluded_names: set[str], files: list[Path]) -> int:
    manifest = root / manifest_name
    if not manifest.is_file():
        raise ValueError(f"Missing current integrity manifest: {manifest_name}")
    entries: dict[str, str] = {}
    for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError(f"{manifest_name}:{number}: malformed checksum line")
        digest, rel = match.groups()
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            raise ValueError(f"{manifest_name}:{number}: unsafe manifest path {rel!r}")
        if rel in entries:
            raise ValueError(f"{manifest_name}:{number}: duplicate manifest path {rel!r}")
        entries[rel] = digest

    expected_paths = {
        path.relative_to(root).as_posix()
        for path in files
        if path.name not in excluded_names
    }
    actual_paths = set(entries)
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or extra:
        raise ValueError(
            f"{manifest_name}: coverage mismatch; missing={missing[:5]}, extra={extra[:5]}"
        )
    for rel, expected_digest in entries.items():
        actual_digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(f"{manifest_name}: checksum mismatch for {rel}")
    return len(entries)


def validate_skill_frontmatter(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\\n"):
        raise ValueError(f"{path}: missing YAML frontmatter opener")
    end = content.find("\\n---\\n", 4)
    if end < 0:
        raise ValueError(f"{path}: missing YAML frontmatter closer")
    metadata = yaml.safe_load(content[4:end])
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        raise ValueError(f"{path}: invalid skill name")
    if not isinstance(description, str) or not description.strip() or len(description) > 160:
        raise ValueError(f"{path}: invalid or overlong skill description")
    if name != path.parent.name:
        raise ValueError(f"{path}: skill name does not match its directory")
    if len(content[end + 5:].strip()) < 200:
        raise ValueError(f"{path}: skill instructions are unexpectedly short")
    if not any(gate in content[end + 5:] for gate in (
        "Mandatory current-source research gate", "V10 mandatory current-source research gate"
    )):
        raise ValueError(f"{path}: missing mandatory current-source research gate")
    return name


def validate_markdown_links(root: Path, markdown_files: list[Path]) -> int:
    pattern = re.compile(r"!?(?:\\[[^\\]]*\\])\\(([^)]+)\\)")
    checked = 0
    for source in markdown_files:
        content = source.read_text(encoding="utf-8")
        for raw in pattern.findall(content):
            target = raw.strip().strip("<>").split(" ", 1)[0]
            if not target or target.startswith((
                "#", "http://", "https://", "mailto:", "tel:", "data:", "javascript:"
            )):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            destination = (root / path_part.lstrip("/")) if path_part.startswith("/") else (source.parent / path_part)
            checked += 1
            if not destination.exists():
                raise ValueError(f"Broken local Markdown link: {source.relative_to(root)} -> {target}")
    return checked


def run_audit(root: Path) -> dict[str, int]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Package root does not exist: {root}")
    errors: list[str] = []
    files = sorted(path for path in root.rglob("*") if path.is_file())
    check(bool(files), "Package contains no files", errors)

    empty = [path.relative_to(root).as_posix() for path in files if path.stat().st_size == 0]
    check(not empty, f"Zero-byte files: {empty[:12]}", errors)
    caches = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if (path.is_dir() and path.name == "__pycache__")
        or (path.is_file() and path.suffix.lower() in {".pyc", ".pyo"})
    ]
    check(not caches, f"Generated Python cache artifacts: {caches[:12]}", errors)

    json_files = [path for path in files if path.suffix.lower() == ".json"]
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON {path.relative_to(root)}: {exc}")

    schema_files = [path for path in files if path.name.endswith(".schema.json")]
    for path in schema_files:
        try:
            jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            errors.append(f"Invalid JSON Schema {path.relative_to(root)}: {exc}")

    yaml_files = [path for path in files if path.suffix.lower() in {".yaml", ".yml"}]
    for path in yaml_files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid YAML {path.relative_to(root)}: {exc}")

    python_files = [path for path in files if path.suffix.lower() == ".py"]
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            errors.append(f"Invalid Python {path.relative_to(root)}: {exc}")

    toml_files = [path for path in files if path.suffix.lower() == ".toml"]
    for path in toml_files:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid TOML {path.relative_to(root)}: {exc}")

    csv_files = [path for path in files if path.suffix.lower() == ".csv"]
    for path in csv_files:
        try:
            rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
            widths = {len(row) for row in rows if row}
            if len(widths) > 1:
                errors.append(f"Inconsistent CSV row widths: {path.relative_to(root)}")
        except Exception as exc:
            errors.append(f"Invalid CSV {path.relative_to(root)}: {exc}")

    installed_root = root / ".agents" / "skills"
    installed_files = sorted(installed_root.glob("*/SKILL.md"))
    installed_names: set[str] = set()
    for path in installed_files:
        try:
            name = validate_skill_frontmatter(path)
            if name in installed_names:
                errors.append(f"Duplicate installed skill name: {name}")
            installed_names.add(name)
        except Exception as exc:
            errors.append(str(exc))
    check(len(installed_files) == EXPECTED_SKILL_COUNT,
          f"Expected {EXPECTED_SKILL_COUNT} installed skills, found {len(installed_files)}", errors)
    check(len(installed_names) == EXPECTED_SKILL_COUNT,
          f"Expected {EXPECTED_SKILL_COUNT} valid unique installed skills, found {len(installed_names)}", errors)

    source_root = root / "v15" / "codex-skills"
    source_files = sorted(source_root.glob("*/SKILL.md"))
    source_names = {path.parent.name for path in source_files}
    check(source_names == EXPECTED_V15_SKILLS,
          f"V15 source skill set mismatch: {sorted(source_names ^ EXPECTED_V15_SKILLS)}", errors)
    for path in source_files:
        installed = installed_root / path.parent.name / "SKILL.md"
        if not installed.is_file() or installed.read_bytes() != path.read_bytes():
            errors.append(f"V15 source/installed skill mismatch: {path.parent.name}")

    descriptor_schema_path = root / "schemas" / "v9-editor-field-descriptor.schema.json"
    collection_schema_path = root / "schemas" / "v9-editor-field-descriptors.schema.json"
    collection_example_path = root / "schemas" / "examples" / "v9-editor-field-descriptors.example.json"
    try:
        descriptor_schema = json.loads(descriptor_schema_path.read_text(encoding="utf-8"))
        collection_schema = json.loads(collection_schema_path.read_text(encoding="utf-8"))
        collection_example = json.loads(collection_example_path.read_text(encoding="utf-8"))
        registry = Registry().with_resource(
            descriptor_schema["$id"], Resource.from_contents(descriptor_schema)
        )
        validator = jsonschema.Draft202012Validator(collection_schema, registry=registry)
        validator.validate(collection_example)
        invalid = list(validator.iter_errors(collection_example + [{"path": "bad path"}]))
        check(bool(invalid), "V9 collection schema accepted an invalid descriptor", errors)
    except Exception as exc:
        errors.append(f"V9 editor-field collection schema/example validation failed: {exc}")

    markdown_files = [path for path in files if path.suffix.lower() == ".md"]
    markdown_links = 0
    try:
        markdown_links = validate_markdown_links(root, markdown_files)
    except Exception as exc:
        errors.append(str(exc))

    manifest_counts: dict[str, int] = {}
    for manifest, excluded in CURRENT_MANIFESTS.items():
        try:
            manifest_counts[manifest] = verify_manifest(root, manifest, excluded, files)
        except Exception as exc:
            errors.append(str(exc))

    if errors:
        raise RuntimeError("Cumulative package audit failed:\\n- " + "\\n- ".join(errors[:100]))
    return {
        "files": len(files),
        "json": len(json_files),
        "schemas": len(schema_files),
        "yaml": len(yaml_files),
        "python": len(python_files),
        "toml": len(toml_files),
        "csv": len(csv_files),
        "installed_skills": len(installed_files),
        "v15_source_skills": len(source_files),
        "markdown_links_checked": markdown_links,
        **{f"{name}_entries": count for name, count in manifest_counts.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        counts = run_audit(args.root)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Cumulative package audit passed.")
    for key, value in counts.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
