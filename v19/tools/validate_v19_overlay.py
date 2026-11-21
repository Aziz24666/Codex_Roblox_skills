#!/usr/bin/env python3
"""Validate V19 overlay files without reconstructing the cumulative V17 package."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V19 = ROOT / "v19"
SKILLS = V19 / "codex-skills"
EXPECTED = {
    "roblox-test-matrix-and-risk-planning",
    "roblox-luau-static-analysis-and-type-safety",
    "roblox-studio-multiplayer-test-engineering",
    "roblox-skill-routing-benchmarking",
    "roblox-test-evidence-auditing",
}
V18_CONTRACT = "## V18 shared workflow and handoff contract"
V19_CONTRACT = "## V19 verification and evaluation contract"


def fail(message: str):
    raise SystemExit(f"V19 overlay validation failed: {message}")


def main():
    version = (V19 / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"19\.\d+\.\d+", version):
        fail(f"invalid V19 version: {version}")
    files = sorted(SKILLS.glob("*/SKILL.md"))
    if len(files) != len(EXPECTED):
        fail(f"expected {len(EXPECTED)} V19 skills, found {len(files)}")
    names = set()
    for path in files:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
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
                fail(f"{path}: malformed frontmatter line")
            metadata[key.strip()] = value.strip()
        name, description = metadata.get("name", ""), metadata.get("description", "")
        if name != path.parent.name or name in names:
            fail(f"{path}: folder/name mismatch or duplicate: {name}")
        if not description or len(description) > 160:
            fail(f"{path}: description must contain 1..160 characters")
        body = "\n".join(lines[closing + 1:])
        for marker in (V18_CONTRACT, V19_CONTRACT):
            if marker not in body:
                fail(f"{path}: missing required contract {marker}")
        names.add(name)
    if names != EXPECTED:
        fail(f"skill inventory mismatch; missing={sorted(EXPECTED - names)}, extra={sorted(names - EXPECTED)}")

    additions = json.loads((V19 / "workflow/routing-additions.json").read_text(encoding="utf-8"))
    routed = {skill for domain in additions["additions"].values() for skill in domain.get("skills", [])}
    if not EXPECTED <= routed:
        fail(f"V19 routing additions omit skills: {sorted(EXPECTED - routed)}")

    cases = json.loads((V19 / "evals/routing-cases.json").read_text(encoding="utf-8"))
    ids = [case.get("id") for case in cases.get("cases", [])]
    if cases.get("schema_version") != 1 or len(ids) < 10 or len(ids) != len(set(ids)):
        fail("routing benchmark must contain at least ten uniquely identified cases")

    for path in sorted((V19 / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{path}: unexpected schema dialect")
    print("V19 overlay validation passed.")
    print(f"V19 source specialists: {len(files)}")
    print(f"Routing regression cases: {len(ids)}")
    print("Evidence/test-plan schemas: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
