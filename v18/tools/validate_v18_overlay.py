#!/usr/bin/env python3
"""Validate the V18 overlay independently of the reconstructed V17 baseline."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "v18" / "codex-skills"
POLICY = ROOT / "v18" / "docs" / "NO_GAMBLING_AND_FAIR_MONETIZATION.md"
ROUTING = ROOT / "v18" / "workflow" / "skill-routing.json"
ORCHESTRATOR = SKILLS / "roblox-end-to-end-development-orchestrator" / "SKILL.md"
EXPECTED = {
    "roblox-player-friendly-monetization",
    "roblox-deterministic-progression-shop",
    "roblox-tiered-catalog-progression",
    "roblox-earned-currency-economy",
}

def fail(message: str) -> None:
    raise SystemExit(f"V18 overlay validation failed: {message}")

def main() -> int:
    files = sorted(SKILLS.glob("*/SKILL.md"))
    if len(files) != 16:
        fail(f"expected 16 V18 skills, found {len(files)}")
    names: set[str] = set()
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
            key, separator, value = line.partition(":")
            if not separator:
                fail(f"{path}: malformed frontmatter line: {line}")
            metadata[key.strip()] = value.strip()
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name or not description:
            fail(f"{path}: missing name or description")
        if name != path.parent.name:
            fail(f"{path}: folder/name mismatch")
        if len(description) > 160:
            fail(f"{path}: description exceeds 160 characters")
        if name in names:
            fail(f"duplicate skill name: {name}")
        if not "\n".join(lines[closing + 1:]).strip():
            fail(f"{path}: empty skill body")
        names.add(name)

    missing = EXPECTED - names
    if missing:
        fail(f"missing economy specialists: {sorted(missing)}")

    policy = POLICY.read_text(encoding="utf-8")
    for phrase in ("Absolute no-gambling rule", "Robux-funded random outcome",
                   "non-Robux", "developer products", "subscriptions",
                   "private servers"):
        if phrase.lower() not in policy.lower():
            fail(f"policy is missing required concept: {phrase}")

    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    economy = routing.get("domains", {}).get("economy", {})
    routed = set(economy.get("skills", []))
    if not EXPECTED <= routed:
        fail(f"economy routing is missing: {sorted(EXPECTED - routed)}")

    orchestrator = ORCHESTRATOR.read_text(encoding="utf-8")
    for token in ("NO_GAMBLING_AND_FAIR_MONETIZATION.md", *EXPECTED):
        if token not in orchestrator:
            fail(f"orchestrator does not enforce or route to {token}")

    print("V18 overlay validation passed.")
    print(f"V18 source skills: {len(files)}")
    print(f"Economy specialists: {len(EXPECTED)}")
    print("No-gambling policy, economy routing, and orchestrator enforcement: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
