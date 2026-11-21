#!/usr/bin/env python3
"""Integrate V18 into the pinned V17 package and produce reproducible metadata."""
from __future__ import annotations
import argparse, hashlib, re, shutil, subprocess, sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]
REPO=SOURCE.parent
EXCLUDED={'.git','.venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','target','build'}
UPGRADE_EXISTING_SKILLS={'roblox-deterministic-progression-shop','roblox-tiered-catalog-progression','roblox-earned-currency-economy','roblox-player-friendly-monetization'}
CONTRACT='''## V18 shared workflow and handoff contract

- Follow root `AGENTS.md` and `v18/docs/SKILL_INTEROPERABILITY.md`; consume the current work item and project profile when present.
- Own only the bounded responsibility assigned. Do not silently redefine shared APIs, schemas, remotes, data ownership, or another specialist's files.
- Return a structured handoff: scope, inputs, decisions, changed files, contracts consumed/produced, checks actually run, evidence, risks, blockers, and next owner.
- Update task/evidence artifacts. Use PASS only for checks that actually ran; keep unavailable Studio/device/live-service checks NOT_RUN or BLOCKED.
- Re-route when scope changes. Skills do not grant tools, permissions, MCP connections, or runtime capabilities.
'''

def clean(root):
    n=0
    for p in sorted(root.rglob('*'),key=lambda x:len(x.parts),reverse=True):
        if p.is_dir() and p.name in EXCLUDED: shutil.rmtree(p); n+=1
        elif p.is_file() and p.suffix in {'.pyc','.pyo'}: p.unlink(); n+=1
    return n

def add_contract(p):
    s=p.read_text(encoding='utf-8')
    if '## V18 shared workflow and handoff contract' in s: return False
    if not s.startswith('---\n'): raise ValueError(f'Missing skill frontmatter: {p}')
    end=s.find('\n---\n',4)
    if end<0: raise ValueError(f'Unclosed skill frontmatter: {p}')
    pos=end+5
    p.write_text(s[:pos]+'\n\n'+CONTRACT+'\n'+s[pos:].lstrip('\n').rstrip()+'\n',encoding='utf-8')
    return True

def upgrade_v17_audit(audit: Path):
    """Migrate the inherited V17 cumulative audit to the V18 package contract."""
    source=audit.read_text(encoding='utf-8')

    old_count='EXPECTED_INSTALLED_SKILLS = 163'
    new_count='EXPECTED_INSTALLED_SKILLS = 175'
    if source.count(old_count)==1 and source.count(new_count)==0:
        source=source.replace(old_count,new_count)
    elif source.count(old_count)==0 and source.count(new_count)==1:
        pass
    else:
        raise ValueError('Unexpected V17 audit skill-count declaration; refusing a partial migration')

    manifest_old='''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V17_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
    manifest_new='''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
    if source.count(manifest_old)==1 and source.count(manifest_new)==0:
        source=source.replace(manifest_old,manifest_new)
    elif source.count(manifest_old)==0 and source.count(manifest_new)==1:
        pass
    else:
        raise ValueError('Unexpected V17 manifest contract; refusing a partial migration')

    old_parity='''    for skill_name in V17_SKILLS:
        source = root / "v17" / "codex-skills" / skill_name / "SKILL.md"
        installed = installed_root / skill_name / "SKILL.md"
        if not source.is_file() or source.read_bytes() != installed.read_bytes():
            raise ValueError(f"V17 source/install mismatch: {skill_name}")'''
    new_parity='''    V18_UPGRADED_SKILLS = {
        "roblox-deterministic-progression-shop",
        "roblox-tiered-catalog-progression",
        "roblox-earned-currency-economy",
        "roblox-player-friendly-monetization",
    }
    for skill_name in V17_SKILLS:
        source_version = "v18" if skill_name in V18_UPGRADED_SKILLS else "v17"
        source = root / source_version / "codex-skills" / skill_name / "SKILL.md"
        installed = installed_root / skill_name / "SKILL.md"
        if not source.is_file() or source.read_bytes() != installed.read_bytes():
            raise ValueError(f"{source_version.upper()} source/install mismatch: {skill_name}")'''
    if source.count(old_parity)==1 and source.count(new_parity)==0:
        source=source.replace(old_parity,new_parity)
    elif source.count(old_parity)==0 and source.count(new_parity)==1:
        pass
    else:
        raise ValueError('Unexpected V17 source/install parity contract; refusing a partial migration')

    audit.write_text(source,encoding='utf-8')

def integrate(root):
    if not (root/'AGENTS.md').is_file() or not (root/'.agents/skills').is_dir(): raise ValueError('Target is not a reconstructed cumulative package')
    if not (root/'v17/VERSION').is_file(): raise ValueError('Pinned V17 baseline is required')
    if (root/'v18/VERSION').exists(): raise ValueError('V18 is already integrated; use --finalize-only')
    src_skills=SOURCE/'codex-skills'
    for p in sorted(src_skills.glob('*/SKILL.md')): add_contract(p)
    for folder in sorted(p for p in src_skills.iterdir() if p.is_dir()):
        target=root/'.agents/skills'/folder.name
        if target.exists():
            if folder.name not in UPGRADE_EXISTING_SKILLS:
                raise ValueError(f'Refusing to overwrite unapproved existing skill: {folder.name}')
            shutil.rmtree(target)
        shutil.copytree(folder,target)
    shutil.copytree(SOURCE,root/'v18')
    for p in sorted((root/'.agents/skills').glob('*/SKILL.md')): add_contract(p)
    # Keep every versioned overlay's source-to-installed copies byte-identical.
    for version in ('v15','v16','v17'):
        source_dir=root/version/'codex-skills'
        if source_dir.is_dir():
            for p in sorted(source_dir.glob('*/SKILL.md')): add_contract(p)
    # Upgrade the inherited V17 audit without weakening its V17 source checks.
    audit=root/'v17/tools/audit_cumulative_package.py'
    upgrade_v17_audit(audit)
    (root/'v17/docs/PACKAGE_INTEGRITY.md').write_text('''# Cumulative Package Integrity After V18

V17 manifests are historical snapshots in V18. The active manifests are `SHA256SUMS.txt`, `V18_SHA256SUMS.txt`, and `V14_SHA256SUMS.txt`. Generate in that order: root excludes all three; V18 includes root and excludes itself plus V14; V14 covers every file except itself. See `v18/docs/PACKAGE_INTEGRITY.md`.
''',encoding='utf-8')
    agents=root/'AGENTS.md'; text=agents.read_text(encoding='utf-8')
    text=text.replace('Roblox Codex Game Studio Kit — V17 Operating Contract','Roblox Codex Game Studio Kit — V18 Operating Contract',1).replace('INDEX_V17.md','INDEX_V18.md')
    section='''

## V18 connected automation and cross-skill workflow
- Use `$roblox-end-to-end-development-orchestrator` for substantial tasks; it owns integration and final reporting.
- Start with `$roblox-task-intake-and-requirements`; inspect an existing project with `$roblox-project-reconnaissance-automation` and `python v18/tools/v18.py doctor --root .`.
- Route only relevant specialists with `python v18/tools/v18.py route --root . --task "..."`; do not load every skill.
- Maintain a task packet under `.codex/workflows/tasks/<task-id>/work-item.json`; define interfaces, data authority, dependencies, and exclusive file ownership before coupled edits.
- Execute bounded implementation and repair loops; delegate only independent work when subagents are genuinely available.
- Record checks honestly. Static/CI success is not a Roblox Studio playtest or live-service verification.
- Stop for approval before publishing, deploying, changing production data/settings/permissions, uploading public assets, destructive changes, or spending.
- Enforce the V18 no-gambling rule for every economy/store task: no paid random rewards, wagers, paid rerolls, or Robux-funded chance outcomes. Read `v18/docs/NO_GAMBLING_AND_FAIR_MONETIZATION.md` and route to all four V18 economy specialists.
- Read `v18/docs/AUTOMATED_WORKFLOW.md`, `v18/docs/SKILL_INTEROPERABILITY.md`, and `v18/docs/APPROVAL_BOUNDARIES.md`.
'''
    if '## V18 connected automation and cross-skill workflow' not in text: text=text.rstrip()+section
    agents.write_text(text.rstrip()+'\n',encoding='utf-8')
    shutil.copy2(SOURCE/'INDEX_V18.md',root/'INDEX_V18.md')
    shutil.copy2(REPO/'RELEASE_NOTES_V18.md',root/'RELEASE_NOTES_V18.md')
    shutil.copy2(REPO/'RELEASE_NOTES_V18_0_1.md',root/'RELEASE_NOTES_V18_0_1.md')
    sample_source=SOURCE/'examples'/'luau-patterns'
    sample_target=root/'examples'/'luau-patterns'
    sample_target.mkdir(parents=True,exist_ok=True)
    shutil.copy2(sample_source/'RemoteRequestValidation.server.luau',sample_target/'RemoteRequestValidation.server.luau')
    shutil.copy2(sample_source/'README.md',sample_target/'README.md')
    (root/'INDEX.md').write_text('# Current Index\n\nSee [INDEX_V18.md](INDEX_V18.md) for the current cumulative release and skill routing.\n',encoding='utf-8')

def files(root): return sorted(p for p in root.rglob('*') if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts))
def manifests(root):
    paths=[root/'SHA256SUMS.txt',root/'V18_SHA256SUMS.txt',root/'V14_SHA256SUMS.txt']
    for p in paths:
        if not p.exists(): p.write_text('',encoding='utf-8')
    fs=files(root); policies=[{paths[0],paths[1],paths[2]},{paths[1],paths[2]},{paths[2]}]; counts={}
    for path,excluded,key in zip(paths,policies,('root','v18','v14')):
        lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix() for p in fs if p not in excluded]
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8'); counts[key]=len(lines)
        for line in lines:
            digest,rel=line.split('  ',1)
            if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=digest: raise ValueError(f'Checksum verification failed: {rel}')
    if counts!={'root':len(fs)-3,'v18':len(fs)-2,'v14':len(fs)-1}: raise ValueError(f'Unexpected checksum counts: {counts}')
    return counts

def finalize(root):
    removed=clean(root); version=(SOURCE/'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'18\.\d+\.\d+',version): raise ValueError('Invalid V18 version')
    data_dir=root/'v18/data'; data_dir.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,'v18/tools/v18.py','build-registry','--root',str(root),'--write'],cwd=root,check=True)
    fs=files(root); skill_count=len(list((root/'.agents/skills').glob('*/SKILL.md')))
    counts={'Installed native Codex skills':skill_count,'V18 specialist skills':len(list((root/'v18/codex-skills').glob('*/SKILL.md'))),'Markdown files':sum(p.suffix.lower()=='.md' for p in fs),'JSON files':sum(p.suffix.lower()=='.json' for p in fs),'Python files':sum(p.suffix.lower()=='.py' for p in fs),'Luau files':sum(p.suffix.lower() in {'.lua','.luau'} for p in fs),'GitHub Actions workflows':sum('.github/workflows' in p.as_posix() and p.suffix in {'.yml','.yaml'} for p in fs),'Total regular files including three active manifests':len(fs)}
    table='\n'.join(f'| {k} | {v} |' for k,v in counts.items())
    (root/'PACKAGE_INVENTORY.md').write_text(f'# Roblox Codex Game Studio Kit — V{version} Package Inventory\n\nGenerated from the final cumulative package tree.\n\n| Category | Count |\n|---|---:|\n{table}\n\n## V18 additions\n- 12 new workflow/orchestration skills and four upgraded inherited economy/monetization specialists.\n- Mandatory no-gambling policy and deterministic shop, tier, and earned-currency requirements.\n- Shared handoff contract across all installed skills.\n- Local CLI, cross-skill registry, task and project schemas, examples, documentation, tests, and CI workflow.\n\n## Evidence boundary\nStatic/package validation does not prove Roblox Studio, multiplayer, device, live DataStore, purchase fulfillment, asset permission, or production behavior.\n',encoding='utf-8')
    (root/'README.md').write_text(f'''# Roblox Codex Game Studio Kit

**Current cumulative release: V{version}.** This is the complete V1–V18 package; earlier versions do not need separate downloads.

## Start with Codex
1. Extract this archive and open the extracted folder in Codex.
2. Read `AGENTS.md` and `INDEX_V18.md`.
3. Start substantial tasks with `$roblox-end-to-end-development-orchestrator`.
4. Inspect projects with `python v18/tools/v18.py doctor --root .`.
5. Route specialists with `python v18/tools/v18.py route --root . --task "..."`.
6. Create a task packet with `python v18/tools/v18.py plan --root . --task "..." --write`.

## Python CLI setup

The full validation and registry commands use Python 3.13 and the pinned packages listed in the included `requirements-ci.txt`. From the extracted package root, install them with:

```powershell
python -m pip install -r requirements-ci.txt
```

For a project-local virtual environment, create and activate it before installing:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements-ci.txt
```

On macOS/Linux, activate with `source .venv/bin/activate` instead. The read-only `doctor` and `route` commands do not require the optional validation packages; `validate`, `build-registry`, `validate-task`, and `verify` do.

## V18 automation
175 native skills, 12 new V18 orchestration skills plus four upgraded V17 economy/monetization specialists, a strict no-gambling policy, a shared handoff contract, cross-skill registry, task/dependency schemas, read-only project doctor, routing, planning, and validation tools. The CLI does not grant Codex MCP, subagents, Studio access, or permissions; those depend on the current environment.

## Validation
Run `python v18/tools/v18.py validate --root .` and `python v18/tools/v18.py verify --root .`. CI does not launch Roblox Studio. Studio, multiplayer, device, live-service, purchase-fulfillment, and production checks require their real environments and evidence.

## License
MIT. This independent community toolkit is not affiliated with or endorsed by Roblox Corporation or OpenAI.
''',encoding='utf-8')
    checks=manifests(root)
    print(f'Removed {removed} cache entries; inventory files={len(files(root))}; skills={skill_count}; manifests={checks}')
    if skill_count!=175: raise ValueError(f'Expected 175 installed skills; found {skill_count}')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--finalize-only',action='store_true'); a=p.parse_args(); root=a.package_root.resolve()
    if not a.finalize_only: integrate(root)
    finalize(root)
    print(f'V18 package integration passed: {len(list((root/".agents/skills").glob("*/SKILL.md")))} skills')
if __name__=='__main__': main()
