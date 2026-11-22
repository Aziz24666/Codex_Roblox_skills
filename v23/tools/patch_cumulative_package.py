#!/usr/bin/env python3
"""Integrate V23 into a reconstructed V22 package and regenerate cumulative manifests."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]
REPO=SOURCE.parent
EXCLUDED={".git",".venv","node_modules","__pycache__",".pytest_cache","target","build","dist"}
CONTRACT="## V23 value-led monetization and opportunity coverage contract\n\n- Search the widest relevant monetization catalogue and rank by game evidence, genuine player value, cost, fairness, and verified demand; never forecast Robux from source code.\n- Keep player purchases, Creator Rewards, ads, avatar/affiliate income, and Creator Store income separate with separate eligibility and accounting.\n- Improve retention through fun, stable, accessible, social, replayable content; never create artificial playtime, AFK loops, forced attendance, coercive prompts, or spending-based player profiling.\n- Preserve V18 no-gambling: no paid random outcomes, mystery purchases, paid chance modifiers, spins, wagers, paid rerolls, or indirect Robux-funded random reward paths.\n- Keep the core game enjoyable without spending; paid outcomes must be deterministic, optional, fixed, and clearly disclosed.\n- Use aggregate analytics and current platform documentation; mark live Studio, Creator Dashboard, marketplace, eligibility, receipt, and subscription checks NOT_RUN or BLOCKED until evidenced.\n"

def append_contract(path):
    content=path.read_text(encoding="utf-8")
    if "## V23 value-led monetization and opportunity coverage contract" not in content:
        if not content.startswith("---\n") or "\n---\n" not in content[4:]:
            raise ValueError("Invalid skill frontmatter: "+str(path))
        path.write_text(content.rstrip()+"\n\n"+CONTRACT+"\n",encoding="utf-8")

def update_old_audit_text(content):
    content=re.sub(r"(?m)^(\s*EXPECTED_SKILLS\s*=\s*)196(\s*(?:#.*)?$)",r"\g<1>201\g<2>",content)
    content=re.sub(r"(?m)^(\s*if\s+len\(skills\)\s*!=\s*)196(\s*:)",r"\g<1>201\g<2>",content)
    return content

def migrate_historical_audits(root):
    for version in ("v17","v18","v19","v20","v22"):
        folder=root/version/"tools"
        if folder.exists():
            for path in folder.glob("*.py"):
                original=path.read_text(encoding="utf-8")
                updated=update_old_audit_text(original)
                if updated!=original: path.write_text(updated,encoding="utf-8")
    folder=root/"v21/tools"
    if folder.exists():
        for path in folder.glob("*.gz"):
            try: original=gzip.decompress(path.read_bytes()).decode("utf-8")
            except (OSError,UnicodeDecodeError): continue
            updated=update_old_audit_text(original)
            if updated!=original: path.write_bytes(gzip.compress(updated.encode("utf-8"),mtime=0))

def merge_routing(root):
    route=root/"v18/workflow/skill-routing.json"
    data=json.loads(route.read_text(encoding="utf-8"))
    additions=json.loads((SOURCE/"workflow/routing-additions.json").read_text(encoding="utf-8"))
    for domain,values in additions["additions"].items():
        if domain not in data["domains"]: raise ValueError("Unknown V23 routing domain: "+domain)
        for signal in values.get("signals",[]):
            if signal not in data["domains"][domain]["signals"]: data["domains"][domain]["signals"].append(signal)
        for skill in values.get("skills",[]):
            if skill not in data["domains"][domain]["skills"]: data["domains"][domain]["skills"].insert(0,skill)
    route.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def update_agents(root):
    path=root/"AGENTS.md"
    content=path.read_text(encoding="utf-8").replace("V22 Operating Contract","V23 Operating Contract").replace("INDEX_V22.md","INDEX_V23.md")
    if "## V23 monetization opportunity and healthy growth" not in content:
        content=content.rstrip()+"\n\n## V23 monetization opportunity and healthy growth\n"
        content+="- Search relevant monetization routes, then implement only evidence-supported offers with real player value.\n"
        content+="- Keep free progression meaningful; purchases are optional, deterministic, transparent, and server-authoritative.\n"
        content+="- Preserve no-gambling; reject artificial playtime, AFK loops, fake scarcity, forced ads, and individual-spender profiling.\n"
        content+="- Separate player purchases, Creator Rewards, ads, and Creator Store income; never invent earnings.\n"
    path.write_text(content,encoding="utf-8")

def package_files(root):
    return sorted(p for p in root.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))

def clean(root):
    for path in sorted(root.rglob("*"),key=lambda p:len(p.parts),reverse=True):
        if path.is_dir() and path.name in EXCLUDED: shutil.rmtree(path)
        elif path.is_file() and path.suffix in {".pyc",".pyo"}: path.unlink()

def write_manifests(root):
    names=["SHA256SUMS.txt","V23_SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"]
    for name in names:
        if not (root/name).exists(): (root/name).write_text("",encoding="utf-8")
    excluded=[
        set(names),
        {"V23_SHA256SUMS.txt","V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V22_SHA256SUMS.txt","V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V21_SHA256SUMS.txt","V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V20_SHA256SUMS.txt","V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V19_SHA256SUMS.txt","V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V18_SHA256SUMS.txt","V14_SHA256SUMS.txt"},
        {"V14_SHA256SUMS.txt"},
    ]
    for name,excluded_names in zip(names,excluded):
        rows=[hashlib.sha256(file.read_bytes()).hexdigest()+"  "+file.relative_to(root).as_posix() for file in package_files(root) if file.name not in excluded_names]
        (root/name).write_text("\n".join(rows)+"\n",encoding="utf-8")

def run(command,root):
    print("$ "+" ".join(map(str,command)))
    subprocess.run(command,cwd=root,check=True)

def integrate(root):
    if not (root/"AGENTS.md").is_file() or not (root/".agents/skills").is_dir():
        raise ValueError("Target is not a reconstructed cumulative package")
    if (root/"v22/VERSION").read_text(encoding="utf-8").strip()!="22.0.1":
        raise ValueError("A verified V22.0.1 package is required")
    if (root/"v23/VERSION").exists(): raise ValueError("V23 already integrated")
    skill_dirs=sorted(p for p in (SOURCE/"codex-skills").iterdir() if p.is_dir())
    if len(skill_dirs)!=5: raise ValueError("Expected five V23 source skills")
    for path in (root/".agents/skills").glob("*/SKILL.md"): append_contract(path)
    shutil.copytree(SOURCE,root/"v23")
    installed=root/".agents/skills"
    for folder in skill_dirs:
        destination=installed/folder.name
        if destination.exists(): raise ValueError("Skill-name collision: "+folder.name)
        shutil.copytree(folder,destination)
    merge_routing(root)
    migrate_historical_audits(root)
    update_agents(root)
    for relative in ("README.md","INDEX_V23.md","RELEASE_NOTES_V23.md"):
        shutil.copy2(REPO/relative,root/relative)
    (root/"INDEX.md").write_text("# Current Index\n\nSee [INDEX_V23.md](INDEX_V23.md) for the current cumulative release and routing.\n",encoding="utf-8")
    (root/".github/workflows").mkdir(parents=True,exist_ok=True)
    shutil.copy2(REPO/".github/workflows/v23-quality.yml",root/".github/workflows/v23-quality.yml")

def finalize(root):
    clean(root)
    run([sys.executable,"v18/tools/v18.py","build-registry","--root",str(root),"--write"],root)
    run([sys.executable,"v23/tools/v23.py","evaluate-routing","--root",str(root)],root)
    inventory={"installed_native_skills":len(list((root/".agents/skills").glob("*/SKILL.md"))),"v23_specialists":5,"v23_opportunity_catalogue":len(json.loads((root/"v23/data/opportunity-catalog.json").read_text(encoding="utf-8")))}
    (root/"PACKAGE_INVENTORY.md").write_text("# V23 Cumulative Package Inventory\n\n"+json.dumps(inventory,indent=2)+"\n\nStatic CI does not prove live Studio, Creator Dashboard, purchase, eligibility, or production behavior.\n",encoding="utf-8")
    write_manifests(root)
    run([sys.executable,"v23/tools/audit_cumulative_package.py","--root",str(root)],root)
    print("V23 cumulative integration passed:",json.dumps(inventory))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--package-root",type=Path,required=True)
    args=parser.parse_args()
    root=args.package_root.resolve()
    integrate(root)
    finalize(root)
if __name__=="__main__": main()
