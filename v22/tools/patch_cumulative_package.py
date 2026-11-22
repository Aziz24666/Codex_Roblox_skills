#!/usr/bin/env python3
"""Integrate V22 into a reconstructed V21 package and regenerate cumulative manifests."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]
REPO=SOURCE.parent
EXCLUDED={".git",".venv","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache","target","build"}
CONTRACT="""## V22 platform monetization contract

- Verify Creator Rewards, Managed Pricing, subscriptions, advertising, and other earning-program eligibility using current official documentation and Creator Dashboard; never infer eligibility or payout from source code.
- Use platform-returned dynamic prices for custom UI where applicable; never display stale regional prices or trust clients for price/entitlement decisions.
- Subscriptions require disclosed recurring benefits, server-confirmed status, paid-term delivery, idempotent period grants, and reconciliation.
- Keep player purchases, Roblox-funded rewards, advertising, and marketplace revenue separate in accounting; use aggregate evidence and state uncertainty.
- Improve genuine player value, not artificial session length, fake traffic, AFK loops, individual-spender targeting, or manipulative retention.
- Preserve V18 no-gambling rules: no gambling, paid random outcomes, or paid chance modifiers.
- Mark Creator Dashboard, Studio, live marketplace, receipt, subscription, and production checks NOT_RUN or BLOCKED until actually performed with V19 evidence.
"""
def append_contract(path):
    content=path.read_text(encoding="utf-8")
    if "## V22 platform monetization contract" not in content:
        if not content.startswith("---\n") or "\n---\n" not in content[4:]: raise ValueError("Invalid skill frontmatter: "+str(path))
        path.write_text(content.rstrip()+"\n\n"+CONTRACT+"\n",encoding="utf-8")
def patch_old_python(path):
    original=path.read_text(encoding="utf-8")
    content=re.sub(r"(?m)^(\s*EXPECTED_[A-Z0-9_]*SKILLS\s*=\s*)(?:175|180|185|191)(\s*(?:#.*)?$)",r"\g<1>196\g<2>",original)
    content=re.sub(r"(?m)^(\s*if\s+len\(skills\)\s*!=\s*)(?:175|180|185|191)(\s*:)",r"\g<1>196\g<2>",content)
    if content!=original: path.write_text(content,encoding="utf-8")
def migrate_historical_audits(root):
    for version in ("v18","v19","v20"):
        folder=root/version/"tools"
        if folder.exists():
            for path in folder.glob("*.py"): patch_old_python(path)
    folder=root/"v21/tools"
    if folder.exists():
        for path in folder.glob("*.gz"):
            try: original=gzip.decompress(path.read_bytes()).decode("utf-8")
            except (OSError,UnicodeDecodeError): continue
            content=re.sub(r"(?m)^(\s*EXPECTED_[A-Z0-9_]*SKILLS\s*=\s*)191(\s*(?:#.*)?$)",r"\g<1>196\g<2>",original)
            content=re.sub(r"(?m)^(\s*if\s+len\(skills\)\s*!=\s*)191(\s*:)",r"\g<1>196\g<2>",content)
            if content!=original: path.write_bytes(gzip.compress(content.encode("utf-8"),mtime=0))
def merge_routing(root):
    route=root/"v18/workflow/skill-routing.json"
    data=json.loads(route.read_text(encoding="utf-8"))
    additions=json.loads((SOURCE/"workflow/routing-additions.json").read_text(encoding="utf-8"))
    for domain,values in additions["additions"].items():
        if domain not in data["domains"]: raise ValueError("Unknown V22 routing domain: "+domain)
        for signal in values.get("signals",[]):
            if signal not in data["domains"][domain]["signals"]: data["domains"][domain]["signals"].append(signal)
        for skill in values.get("skills",[]):
            if skill not in data["domains"][domain]["skills"]: data["domains"][domain]["skills"].insert(0,skill)
    route.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def update_agents(root):
    path=root/"AGENTS.md"
    text=path.read_text(encoding="utf-8")
    text=text.replace("V21 Operating Contract","V22 Operating Contract").replace("INDEX_V21.md","INDEX_V22.md")
    if "## V22 platform monetization and creator economics" not in text:
        text=text.rstrip()+"\n\n## V22 platform monetization and creator economics\n- Verify current eligibility and product rules before planning Creator Rewards, Managed Pricing, price optimization, subscriptions, or ads.\n- Use dynamic platform-returned prices for custom UI where applicable; keep server authority over catalog, transfers, receipts, and subscription entitlements.\n- Disclose recurring subscription benefits and renewal/cancellation details; make period grants idempotent and reconcile missed delivery.\n- Keep revenue streams distinct and use aggregate evidence. Never manipulate playtime or target individual spenders.\n- Preserve V18 no-gambling and V21 fixed-known-outcome requirements.\n"
    path.write_text(text,encoding="utf-8")
def package_files(root):
    return sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
def clean(root):
    for path in sorted(root.rglob("*"),key=lambda p:len(p.parts),reverse=True):
        if path.is_dir() and path.name in EXCLUDED: shutil.rmtree(path)
        elif path.is_file() and path.suffix in {".pyc",".pyo"}: path.unlink()
def write_manifests(root):
    names=["SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"]
    paths=[root/name for name in names]
    for path in paths:
        if not path.exists(): path.write_text("",encoding="utf-8")
    excluded=[set(names),
      {"V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
      {"V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
      {"V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
      {"V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
      {"V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},{"V14_SHA256SUMS.txt"}]
    for path,excluded_names in zip(paths,excluded):
        rows=[hashlib.sha256(file.read_bytes()).hexdigest()+"  "+file.relative_to(root).as_posix() for file in package_files(root) if file.name not in excluded_names]
        path.write_text("\n".join(rows)+"\n",encoding="utf-8")
def run(command,root):
    print("$ "+" ".join(map(str,command))); subprocess.run(command,cwd=root,check=True)
def integrate(root):
    if not (root/"AGENTS.md").is_file() or not (root/".agents/skills").is_dir(): raise ValueError("Target is not a reconstructed cumulative package")
    if (root/"v21/VERSION").read_text().strip()!="21.0.0": raise ValueError("A verified V21.0.0 package is required")
    if (root/"v22/VERSION").exists(): raise ValueError("V22 already integrated")
    source_skills=SOURCE/"codex-skills"
    if len(list(source_skills.glob("*/SKILL.md")))!=5: raise ValueError("Expected five V22 source skills")
    for path in (root/".agents/skills").glob("*/SKILL.md"): append_contract(path)
    shutil.copytree(SOURCE,root/"v22")
    installed=root/".agents/skills"
    for folder in sorted(p for p in source_skills.iterdir() if p.is_dir()):
        destination=installed/folder.name
        if destination.exists(): raise ValueError("Skill-name collision: "+folder.name)
        shutil.copytree(folder,destination)
    for path in (root/"v22/codex-skills").glob("*/SKILL.md"): append_contract(path)
    for path in (installed).glob("*/SKILL.md"):
        if path.parent.name in {p.parent.name for p in (root/"v22/codex-skills").glob("*/SKILL.md")}:
            append_contract(path)
    merge_routing(root); migrate_historical_audits(root); update_agents(root)
    for relative in ("INDEX_V22.md","RELEASE_NOTES_V22.md","README.md"):
        shutil.copy2(REPO/relative,root/relative)
    (root/"INDEX.md").write_text("# Current Index\n\nSee [INDEX_V22.md](INDEX_V22.md) for the current cumulative release and routing.\n",encoding="utf-8")
    (root/".github/workflows").mkdir(parents=True,exist_ok=True)
    shutil.copy2(REPO/".github/workflows/v22-quality.yml",root/".github/workflows/v22-quality.yml")
def finalize(root):
    clean(root)
    run([sys.executable,"v18/tools/v18.py","build-registry","--root",str(root),"--write"],root)
    run([sys.executable,"v22/tools/v22.py","evaluate-routing","--root",str(root)],root)
    run([sys.executable,"v22/tools/v22.py","validate-subscription-contract","--root",str(root),"--file","v22/examples/subscription-contract.example.json"],root)
    inventory={"installed_native_skills":len(list((root/".agents/skills").glob("*/SKILL.md"))),"v22_specialists":5,"v21_specialists":6,"v20_specialists":5,"v19_specialists":5}
    (root/"PACKAGE_INVENTORY.md").write_text("# V22 Cumulative Package Inventory\n\n"+json.dumps(inventory,indent=2)+"\n\nStatic CI does not prove Studio, Creator Dashboard, live purchase, subscription, or production behavior.\n",encoding="utf-8")
    write_manifests(root)
    run([sys.executable,"v22/tools/audit_cumulative_package.py","--root",str(root)],root)
    print("V22 cumulative integration passed:",json.dumps(inventory))
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--package-root",type=Path,required=True); args=parser.parse_args()
    root=args.package_root.resolve(); integrate(root); finalize(root)
if __name__=="__main__": main()
