#!/usr/bin/env python3
"""Validate V20 source specialists, schema, routing cases, and documentation."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "v20"
SKILLS = V20 / "codex-skills"
EXPECTED = {
    "roblox-server-authority-and-remote-boundaries",
    "roblox-player-data-resilience-and-migrations",
    "roblox-idempotent-economy-transactions",
    "roblox-live-operations-and-safe-rollouts",
    "roblox-production-observability-and-incident-response",
}
CONTRACTS = (
    "## V18 shared workflow and handoff contract",
    "## V19 verification and evaluation contract",
    "## V20 production reliability contract",
)


def fail(message: str):
    raise SystemExit(f"V20 overlay validation failed: {message}")


def main():
    version = (V20 / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"20\.\d+\.\d+", version):
        fail(f"invalid V20 version: {version}")
    files = sorted(SKILLS.glob("*/SKILL.md"))
    if len(files) != len(EXPECTED):
        fail(f"expected {len(EXPECTED)} V20 skills, found {len(files)}")
    names = set()
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            fail(f"{path}: missing frontmatter")
        try:
            closing = lines.index("---", 1)
        except ValueError:
            fail(f"{path}: unterminated frontmatter")
        metadata = {}
        for line in lines[1:closing]:
            key, sep, value = line.partition(":")
            if not sep:
                fail(f"{path}: malformed frontmatter")
            metadata[key.strip()] = value.strip()
        name, description = metadata.get("name", ""), metadata.get("description", "")
        if name != path.parent.name or name in names:
            fail(f"{path}: duplicate or mismatched skill name {name}")
        if not description or len(description) > 160:
            fail(f"{path}: description must contain 1..160 characters")
        body = "\n".join(lines[closing + 1:])
        for marker in CONTRACTS:
            if marker not in body:
                fail(f"{path}: missing {marker}")
        names.add(name)
    if names != EXPECTED:
        fail(f"skill inventory mismatch: missing={sorted(EXPECTED-names)}, extra={sorted(names-EXPECTED)}")

    import jsonschema
    schema = json.loads((V20 / "schemas/production-contract.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    additions = json.loads((V20 / "workflow/routing-additions.json").read_text(encoding="utf-8"))
    routed = {skill for domain in additions["additions"].values() for skill in domain.get("skills", [])}
    if not EXPECTED <= routed:
        fail(f"routing additions omit V20 skills: {sorted(EXPECTED-routed)}")
    base_routes = json.loads((ROOT / "v18/workflow/skill-routing.json").read_text(encoding="utf-8"))
    unknown_domains = set(additions["additions"]) - set(base_routes["domains"])
    if unknown_domains:
        fail(f"routing additions reference unknown domains: {sorted(unknown_domains)}")

    cases = json.loads((V20 / "evals/routing-cases.json").read_text(encoding="utf-8"))
    rows = cases.get("cases", [])
    ids = [row.get("id") for row in rows]
    if cases.get("schema_version") != 1 or len(rows) < 5 or len(ids) != len(set(ids)):
        fail("routing regression corpus must have at least five uniquely identified cases")

    docs = ["README.md", "INDEX_V20.md", "docs/PRODUCTION_RELIABILITY.md",
            "docs/OPERATIONS_AND_ROLLOUTS.md", "docs/REMOTE_AUTHORITY_AND_DATA.md"]
    for relative in docs:
        if not (V20 / relative).is_file():
            fail(f"missing V20 documentation: {relative}")

    import importlib.util
    spec = importlib.util.spec_from_file_location("v20_overlay_cli", V20 / "tools/v20.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.validate_contract(ROOT, Path("v20/examples/production-contract.example.json"))
    if result["status"] != "PASS":
        fail("example production contract did not validate")
    print("V20 overlay validation passed.")
    print(f"V20 specialist skills: {len(files)}")
    print(f"Routing regression cases: {len(rows)}")
    print("Production contract schema and example: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
