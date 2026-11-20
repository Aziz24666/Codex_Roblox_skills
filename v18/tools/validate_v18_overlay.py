#!/usr/bin/env python3
"""Validate the V18 overlay independently of the reconstructed V17 baseline."""
from __future__ import annotations
import json
import re
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
        if not source.startswith("---\\n"):
            fail(f"{path}: missing frontmatter")
        end = source.find("\\n---\\n", 4)
        if end < 0:
            fail(f"{path}: unterminated frontmatter")
        frontmatter = source[4:end]
        name_match = re.search(r"(?m)^name:\\s*([a-z0-9-]+)\\s*$", frontmatter)
        desc_match = re.search(r"(?m)^description:\\s*(.+?)\\s*$", frontmatter)
        if not name_match or not desc_match:
            fail(f"{path}: invalid name or description")
        name, description = name_match.group(1), desc_match.group(1)
        if name != path.parent.name:
            fail(f"{path}: folder/name mismatch")
        if len(description) > 160:
            fail(f"{path}: description exceeds 160 characters")
        if name in names:
            fail(f"duplicate skill name: {name}")
        if not source[end + 5:].strip():
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
