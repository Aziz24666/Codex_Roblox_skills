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


def migrate_v17_audit(audit_path: Path):
    """Migrate the embedded V17 audit without weakening unrelated V17 checks."""
    content=audit_path.read_text(encoding='utf-8')
    count_pattern=re.compile(r'(?m)^EXPECTED_INSTALLED_SKILLS\s*=\s*163\s*$')
    content,count=count_pattern.subn('EXPECTED_INSTALLED_SKILLS = 175',content)
    if count!=1:
        raise ValueError(f'Expected exactly one V17 installed-skill count of 163; found {count}')
    if 'V18_UPGRADED_SKILLS' in content:
        raise ValueError('V17 audit already contains a V18 migration marker')
    upgraded='V18_UPGRADED_SKILLS = {\n'+''.join(f'    "{name}",\n' for name in sorted(UPGRADE_EXISTING_SKILLS))+'}'
    content=content.replace('EXPECTED_INSTALLED_SKILLS = 175\n','EXPECTED_INSTALLED_SKILLS = 175\n'+upgraded+'\n',1)

    # Find V17's skill-name loop by the source/installed byte comparison.
    loop_pattern=re.compile(r'(?m)^(?P<indent>[ \t]*)for (?P<variable>[A-Za-z_]\w*) in [^\n:]+:\s*$')
    source_parity_loops=[]
    lines=content.splitlines(keepends=True)
    offset=0
    for index,line in enumerate(lines):
        raw=line.rstrip('\r\n')
        match=loop_pattern.fullmatch(raw)
        if match:
            base_indent=len(match.group('indent'))
            body_lines=[]
            for body_line in lines[index+1:]:
                if body_line.strip():
                    body_indent=len(body_line)-len(body_line.lstrip(' \t'))
                    if body_indent<=base_indent:
                        break
                body_lines.append(body_line)
            body=''.join(body_lines)
            if re.search(r'\bsource\.read_bytes\(\)',body) and re.search(r'\binstalled\.read_bytes\(\)',body):
                source_parity_loops.append((offset,offset+len(line),match))
        offset+=len(line)
    if len(source_parity_loops)!=1:
        raise ValueError(f'Expected exactly one V17 source/installed byte-parity loop; found {len(source_parity_loops)}')
    loop_start,loop_end,loop_match=source_parity_loops[0]
    indent=loop_match.group('indent')
    variable=loop_match.group('variable')
    replacement=(loop_match.group(0)+'\n'
                 f'{indent}    if {variable} in V18_UPGRADED_SKILLS:\n'
                 f'{indent}        continue\n')
    content=content[:loop_start]+replacement+content[loop_end:]

    old='''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V17_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
    new='''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V18_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V18_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''
    if content.count(old)!=1:
        raise ValueError('Could not uniquely migrate the V17 current-manifest contract')
    content=content.replace(old,new,1)
    audit_path.write_text(content,encoding='utf-8')


def mark_remote_validation_example(root: Path):
    """Clearly label the inherited incomplete remote-validation teaching sample."""
    sample=root/'examples/luau-patterns/RemoteRequestValidation.server.luau'
    if not sample.is_file():
        raise ValueError(f'Missing expected teaching example: {sample}')
    content=sample.read_text(encoding='utf-8')
    marker='-- V18 SAFETY NOTE: TEACHING EXAMPLE ONLY'
    if marker in content:
        return False
    warning='''-- V18 SAFETY NOTE: TEACHING EXAMPLE ONLY — NOT PRODUCTION-READY.
-- This sample intentionally leaves authoritative world-state, ownership,
-- distance, cooldown, and duplicate-request checks incomplete.
-- Do not copy it into a live experience as-is. Implement and test each check
-- on the server for your specific game before granting any result.

'''
    sample.write_text(warning+content.lstrip('\n'),encoding='utf-8')
    return True

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
    # Migrate the inherited audit to 175 installed skills and exempt only the four V18 upgrades.
    migrate_v17_audit(root/'v17/tools/audit_cumulative_package.py')
    mark_remote_validation_example(root)
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

## Requirements
- Python 3.13 is the supported and CI-validated runtime. The inherited package uses `tomllib` (standard library since Python 3.11).
- From the package root, install validation dependencies with `python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt`.
- The basic `doctor` and `route` commands use only the Python standard library; schema validation and full verification require the installed packages.

## Start with Codex
1. Extract this archive and open the extracted folder in Codex.
2. Read `AGENTS.md` and `INDEX_V18.md`.
3. Start substantial tasks with `$roblox-end-to-end-development-orchestrator`.
4. Inspect projects with `python v18/tools/v18.py doctor --root .`.
5. Route specialists with `python v18/tools/v18.py route --root . --task "..."`.
6. Create a task packet with `python v18/tools/v18.py plan --root . --task "..." --write`.

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
