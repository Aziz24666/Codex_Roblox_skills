#!/usr/bin/env python3
"""V18 read-only-first Roblox Codex workflow CLI."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

V18_SKILLS = {
 'roblox-end-to-end-development-orchestrator','roblox-task-intake-and-requirements',
 'roblox-project-reconnaissance-automation','roblox-impact-aware-skill-routing',
 'roblox-cross-system-contract-governance','roblox-dependency-aware-workstream-planning',
 'roblox-autonomous-implementation-loop','roblox-agent-delegation-and-coordination',
 'roblox-continuous-validation-and-repair','roblox-risk-and-approval-gating',
 'roblox-workflow-state-and-context-handoff','roblox-evidence-first-completion',
 'roblox-player-friendly-monetization','roblox-deterministic-progression-shop',
 'roblox-tiered-catalog-progression','roblox-earned-currency-economy'}
CONTRACT = '## V18 shared workflow and handoff contract'
EXCLUDED = {'.git','.venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','target','build'}

def _require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError('PyYAML is required for skill/schema validation. From the package root run: python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt') from exc
    return yaml

def _require_jsonschema():
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError('jsonschema is required for schema validation. From the package root run: python -m pip install -r requirements-ci.txt -r v18/requirements-ci.txt') from exc
    return jsonschema

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def read_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write_json(p, obj): Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def skill_files(root):
    p=Path(root)/'.agents'/'skills'
    if not p.is_dir(): raise ValueError(f'Missing installed skills directory: {p}')
    return sorted(p.glob('*/SKILL.md'))
def parse_skill(path):
    text=path.read_text(encoding='utf-8')
    if not text.startswith('---\n'): raise ValueError(f'{path}: missing YAML frontmatter')
    end=text.find('\n---\n',4)
    if end<0: raise ValueError(f'{path}: unterminated YAML frontmatter')
    yaml=_require_yaml()
    meta=yaml.safe_load(text[4:end])
    if not isinstance(meta,dict): raise ValueError(f'{path}: frontmatter is not a mapping')
    name,desc=meta.get('name'),meta.get('description')
    if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9-]{1,64}',name): raise ValueError(f'{path}: invalid name')
    if name!=path.parent.name: raise ValueError(f'{path}: skill name/folder mismatch')
    if not isinstance(desc,str) or not desc.strip() or len(desc)>160: raise ValueError(f'{path}: description must be 1..160 characters')
    if not text[end+5:].strip(): raise ValueError(f'{path}: empty skill body')
    return name,desc,text[end+5:]
def domains(root): return read_json(Path(root)/'v18/workflow/skill-routing.json')['domains']
def installed_names(root): return {p.parent.name for p in skill_files(root)}
def infer_domains(name,desc,dm):
    hay=(name.replace('-',' ')+' '+desc).lower()
    return [k for k,cfg in dm.items() if any(s.lower() in hay for s in cfg['signals'])] or ['general']
def build_registry(root):
    files=skill_files(root); dm=domains(root); items=[]; memberships={}
    for p in files:
        n,d,_=parse_skill(p); ds=infer_domains(n,d,dm); memberships[n]=set(ds)
        items.append({'name':n,'description':d,'path':p.relative_to(root).as_posix(),'domains':ds,'role':'orchestrator' if 'orchestrator' in n else 'specialist'})
    for item in items:
        peers=[]
        for other in items:
            if other['name']==item['name']: continue
            overlap=len(memberships[item['name']] & memberships[other['name']])
            if overlap: peers.append((overlap,other['name']))
        item['related_skills']=[n for _,n in sorted(peers,key=lambda x:(-x[0],x[1]))[:6]]
    return {'schema_version':1,'generated_at':now(),'skill_count':len(items),'skills':items}
def scan_project(root):
    root=Path(root).resolve()
    if not root.is_dir(): raise ValueError(f'Not a directory: {root}')
    known=['AGENTS.md','default.project.json','wally.toml','aftman.toml','selene.toml','stylua.toml','rokit.toml','project.json','foreman.toml','sourcemap.json']
    markers=[x for x in known if (root/x).exists()]
    for pat in ('*.project.json','*.rbxlx','*.rbxl','*.place.json'): markers += [p.name for p in sorted(root.glob(pat))[:20]]
    rojo=any('project.json' in x for x in markers); place=any(x.lower().endswith(('.rbxl','.rbxlx')) for x in markers)
    source='hybrid' if rojo and place else 'rojo-managed' if rojo else 'studio-native' if place else 'unknown'
    tools={}
    for cmd in ('python','git','rojo','luau-analyze','luau','selene','stylua','wally','aftman','rokit','lune'):
        exe=shutil.which(cmd); item={'available':bool(exe)}
        if exe:
            try:
                q=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=3,check=False)
                item['path']=exe; version=(q.stdout or q.stderr).strip().splitlines()
                if version: item['version']=version[0][:160]
            except (OSError,subprocess.TimeoutExpired): item['version']='version probe unavailable'
        tools[cmd]=item
    count=len(list((root/'.agents/skills').glob('*/SKILL.md'))) if (root/'.agents/skills').is_dir() else 0
    nested=[]
    for p in root.rglob('AGENTS.md'):
        if len(nested)>=100: break
        if not any(part in EXCLUDED for part in p.relative_to(root).parts) and p!=root/'AGENTS.md': nested.append(p.relative_to(root).as_posix())
    git=[]
    if (root/'.git').exists() and shutil.which('git'):
        q=subprocess.run([shutil.which('git'),'status','--short'],cwd=root,capture_output=True,text=True,timeout=5,check=False)
        if q.returncode==0: git=q.stdout.splitlines()[:100]
    confidence='high' if source=='rojo-managed' else 'medium' if source in {'hybrid','studio-native'} else 'low'
    return {'schema_version':1,'root':str(root),'detected_at':now(),'source_of_truth':source,'markers':sorted(set(markers)),'tools':tools,'skills_count':count,'git_status':git,'nested_guidance':sorted(nested),'confidence':confidence,'notes':['Read-only inspection; project scripts were not executed.','Source-of-truth classification uses markers and requires human review.']}
def route_task(root,task,max_specialists=8):
    if not task.strip(): raise ValueError('Task cannot be empty')
    root=Path(root); dm=domains(root); installed=installed_names(root) if (root/'.agents/skills').is_dir() else set(V18_SKILLS)
    text=task.lower(); scores=[]
    for dom,cfg in dm.items():
        hits=[s for s in cfg['signals'] if s.lower() in text]
        if hits: scores.append((len(hits),dom,hits))
    scores.sort(key=lambda x:(-x[0],x[1])); selected=[]; why={}
    def add(n,reason):
        if n in installed and n not in selected: selected.append(n); why[n]=reason
    add('roblox-end-to-end-development-orchestrator','Owns the task lifecycle and integration.')
    add('roblox-task-intake-and-requirements','Turns the request into observable acceptance criteria.')
    add('roblox-impact-aware-skill-routing','Checks specialist scope and avoids duplication.')
    add('roblox-evidence-first-completion','Connects completion claims to evidence.')
    if (root/'AGENTS.md').exists() or any(root.glob('*.project.json')) or any(root.glob('*.rbxl*')):
        add('roblox-project-reconnaissance-automation','Inspect source of truth, project structure, and tools.')
        add('roblox-project-intelligence','Map existing architecture and entry points.')
    specialist_count=0; chosen=scores[:4]
    for _,dom,hits in chosen:
        for name in dm[dom]['skills']:
            if specialist_count>=max_specialists: break
            before=len(selected); add(name,f"Domain {dom!r} matched: {', '.join(hits[:5])}.")
            if len(selected)>before: specialist_count+=1
        if specialist_count>=max_specialists: break
    if len(chosen)>=3:
        add('roblox-game-builder','Task spans multiple systems.')
        add('roblox-cross-system-contract-governance','Define shared interfaces before coupled edits.')
        add('roblox-dependency-aware-workstream-planning','Order dependent work and prevent file conflicts.')
    if any(x in text for x in ('remote','multiplayer','network','client input','exploit','publish','deploy','production','live data')):
        add('roblox-risk-and-approval-gating','Review security and external-effect approval boundaries.')
    return {'schema_version':1,'task':task,'primary_skill':selected[0],'selected_skills':selected,'domains':[{'name':d,'score':s,'matched_signals':h} for s,d,h in chosen],'rationale':why,'selection_note':'Deterministic recommendation. Inspect actual impact and revise; do not load all skills by default.'}
def topo(streams):
    ids=[x.get('id') for x in streams]
    if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)): raise ValueError('Workstream IDs must be unique non-empty strings')
    known=set(ids); outgoing={x:[] for x in ids}; degree={x:0 for x in ids}; paths=[]
    for st in streams:
        sid=st['id']
        for dep in st.get('depends_on',[]):
            if dep not in known: raise ValueError(f'{sid} references missing dependency {dep}')
            if dep==sid: raise ValueError(f'{sid} depends on itself')
            outgoing[dep].append(sid); degree[sid]+=1
        for raw in st.get('owned_paths',[]):
            p=Path(raw)
            if p.is_absolute() or '..' in p.parts: raise ValueError(f'Unsafe owned path: {raw}')
            norm=p.as_posix().rstrip('/')
            for owner,other in paths:
                if norm==other or norm.startswith(other+'/') or other.startswith(norm+'/'): raise ValueError(f'Owned path overlap: {owner}:{other} and {sid}:{norm}')
            paths.append((sid,norm))
    ready=sorted(x for x,d in degree.items() if d==0); order=[]
    while ready:
        cur=ready.pop(0); order.append(cur)
        for child in sorted(outgoing[cur]):
            degree[child]-=1
            if degree[child]==0: ready.append(child); ready.sort()
    if len(order)!=len(ids): raise ValueError('Dependency graph contains a cycle')
    return order
def make_work_item(root,task,task_id=None):
    route=route_task(root,task); slug=re.sub(r'[^a-z0-9]+','-',(task_id or task).lower()).strip('-')[:56] or 'roblox-task'
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,63}',slug): raise ValueError('Invalid task ID')
    streams=[
      {'id':'discovery','title':'Inspect project and source of truth','owner':'roblox-project-reconnaissance-automation','depends_on':[],'owned_paths':[],'status':'PENDING','outputs':['project profile','affected-system map']},
      {'id':'requirements','title':'Define scope and acceptance criteria','owner':'roblox-task-intake-and-requirements','depends_on':['discovery'],'owned_paths':[],'status':'PENDING','outputs':['acceptance criteria']},
      {'id':'contracts','title':'Define cross-system contracts','owner':'roblox-cross-system-contract-governance','depends_on':['requirements'],'owned_paths':[],'status':'PENDING','outputs':['reviewed interfaces']},
      {'id':'implementation','title':'Implement bounded vertical slices','owner':'domain-specialists','depends_on':['contracts'],'owned_paths':[],'status':'PENDING','outputs':['working feature']},
      {'id':'integration','title':'Integrate and resolve cross-system behavior','owner':'roblox-end-to-end-development-orchestrator','depends_on':['implementation'],'owned_paths':[],'status':'PENDING','outputs':['integrated feature']},
      {'id':'verification','title':'Run impact-selected checks','owner':'roblox-continuous-validation-and-repair','depends_on':['integration'],'owned_paths':[],'status':'PENDING','outputs':['verification evidence']},
      {'id':'review','title':'Review risks, scope, and evidence','owner':'roblox-evidence-first-completion','depends_on':['verification'],'owned_paths':[],'status':'PENDING','outputs':['completion report']}]
    return {'schema_version':1,'task_id':slug,'title':task[:160],'task':task,'status':'DRAFT','phase':'intake','goals':['Deliver the requested player-visible or developer-visible outcome.'],'non_goals':['Unrequested architecture migrations and external side effects.'],'assumptions':['Project-specific architecture will be confirmed during discovery.'],'impacted_domains':[x['name'] for x in route['domains']],'selected_skills':route['selected_skills'],'workstreams':streams,'acceptance_criteria':[{'id':'AC-01','description':'The delivered behavior satisfies the requested outcome and constraints.','verification':'Run the agreed acceptance scenario and record expected and actual behavior.','owner':'integration','status':'PENDING','evidence':[]},{'id':'AC-02','description':'Changed interfaces have documented ownership and compatible producer/consumer behavior.','verification':'Review contracts and run relevant schema, unit, and integration tests.','owner':'contracts','status':'PENDING','evidence':[]},{'id':'AC-03','description':'Verification results are recorded honestly and unexecuted checks remain visible.','verification':'Validate evidence and inspect final diff and risks.','owner':'verification','status':'PENDING','evidence':[]}],'approvals':[],'evidence':[],'created_at':now(),'updated_at':now()}
def validate_task(root,data):
    jsonschema=_require_jsonschema()
    schema=read_json(Path(root)/'v18/schemas/work-item.schema.json')
    jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)
    order=topo(data['workstreams']); known={x['id'] for x in data['workstreams']}
    for c in data['acceptance_criteria']:
        if c['owner'] not in known and c['owner'] not in {'integration-owner','orchestrator'}: raise ValueError(f"Unknown criterion owner: {c['owner']}")
        if c['status']=='PASS' and not c.get('evidence'): raise ValueError(f"{c['id']} cannot pass without evidence")
    if data['status']=='DONE' and any(x['status'] not in {'PASS','NOT_APPLICABLE'} for x in data['acceptance_criteria']): raise ValueError('DONE requires all criteria to pass or be not applicable')
    return order
def validate(root):
    jsonschema=_require_jsonschema()
    root=Path(root); files=skill_files(root); names={}; missing=[]
    for p in files:
        name,_,body=parse_skill(p)
        if name in names: raise ValueError(f'Duplicate skill: {name}')
        names[name]=p
        if CONTRACT not in body: missing.append(name)
    if missing: raise ValueError(f'Skills missing V18 shared contract: {missing[:25]}')
    if V18_SKILLS-set(names): raise ValueError(f'Missing V18 skills: {sorted(V18_SKILLS-set(names))}')
    source=root/'v18/codex-skills'
    for p in sorted(source.glob('*/SKILL.md')):
        n,_,_=parse_skill(p)
        if n not in names or p.read_bytes()!=names[n].read_bytes(): raise ValueError(f'Source/install mismatch: {n}')
    schema_dir=root/'v18/schemas'; schemas=list(schema_dir.glob('*.schema.json'))
    if len(schemas)!=4: raise ValueError(f'Expected four V18 schemas, found {len(schemas)}')
    for p in schemas: jsonschema.Draft202012Validator.check_schema(read_json(p))
    for example,schema in [('work-item.example.json','work-item.schema.json'),('project-profile.example.json','project-profile.schema.json'),('workflow-evidence.example.json','workflow-evidence.schema.json')]:
        obj=read_json(root/'v18/examples'/example); sch=read_json(schema_dir/schema)
        jsonschema.Draft202012Validator(sch,format_checker=jsonschema.FormatChecker()).validate(obj)
        if example=='work-item.example.json': topo(obj['workstreams'])
    dm=domains(root)
    for domain,cfg in dm.items():
        missing_refs=set(cfg['skills'])-set(names)
        if missing_refs: raise ValueError(f'Routing domain {domain} references absent skills: {sorted(missing_refs)}')
    reg=build_registry(root)
    if len(reg['skills'])!=len(files): raise ValueError('Registry skill count mismatch')
    return {'status':'PASS','installed_skills':len(files),'v18_skills':len(V18_SKILLS),'schemas':len(schemas),'routing_domains':len(dm),'registry_skills':len(reg['skills'])}
def verify(root):
    cmds=[
      ['v15/tools/v15_validate.py','--root','v15'],['-m','unittest','discover','-s','v15/tests','-v'],
      ['v16/tools/v16_validate.py','--root','v16'],['-m','unittest','discover','-s','v16/tests','-v'],
      ['v17/tools/v17_validate.py','--root','v17'],['-m','unittest','discover','-s','v17/tests','-v'],
      ['v18/tools/v18.py','validate','--root',str(root)],['-m','unittest','discover','-s','v18/tests','-v']]
    for n,cmd in enumerate(cmds,1):
        full=[sys.executable]+cmd; print(f'[{n}/{len(cmds)+2}] {" ".join(full)}')
        result=subprocess.run(full,cwd=root,check=False)
        if result.returncode: return result.returncode
    # Generate fresh package manifests after version-specific validators and tests.
    final=subprocess.run([sys.executable,'v18/tools/patch_cumulative_package.py','--package-root',str(root),'--finalize-only'],cwd=root,check=False)
    if final.returncode: return final.returncode
    # The inherited tools test suite contains V13/V14 pack-doctor tests, so it must
    # run only after the package manifests have been regenerated.
    tool_tests=['-m','unittest','discover','-s','tools/tests','-v']
    print(f'[legacy tools unit tests] {" ".join([sys.executable]+tool_tests)}')
    result=subprocess.run([sys.executable]+tool_tests,cwd=root,check=False)
    if result.returncode: return result.returncode
    # Refresh once more in case tests generated package-local cache/artifact files.
    final=subprocess.run([sys.executable,'v18/tools/patch_cumulative_package.py','--package-root',str(root),'--finalize-only'],cwd=root,check=False)
    if final.returncode: return final.returncode
    for label,cmd in (
      ('V13 package doctor',['tools/v13_pack_doctor.py',str(root)]),
      ('V14 package doctor',['tools/v14_pack_doctor.py',str(root)])):
        print(f'[{label}] {" ".join([sys.executable]+cmd)}')
        result=subprocess.run([sys.executable]+cmd,cwd=root,check=False)
        if result.returncode: return result.returncode
    v18_audit=subprocess.run([sys.executable,'v18/tools/audit_cumulative_package.py','--root',str(root)],cwd=root,check=False)
    if v18_audit.returncode: return v18_audit.returncode
    legacy_audit_cmd=[sys.executable,'v17/tools/audit_cumulative_package.py','--root',str(root)]
    print(f'[V17 migrated cumulative audit] {" ".join(legacy_audit_cmd)}')
    return subprocess.run(legacy_audit_cmd,cwd=root,check=False).returncode
def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    d=sub.add_parser('doctor'); d.add_argument('--root',type=Path,default=Path('.')); d.add_argument('--json',action='store_true'); d.add_argument('--write-profile',action='store_true'); d.add_argument('--force',action='store_true')
    r=sub.add_parser('route'); r.add_argument('--root',type=Path,default=Path('.')); r.add_argument('--task',required=True); r.add_argument('--max-specialists',type=int,default=8)
    pl=sub.add_parser('plan'); pl.add_argument('--root',type=Path,default=Path('.')); pl.add_argument('--task',required=True); pl.add_argument('--id'); pl.add_argument('--write',action='store_true')
    vt=sub.add_parser('validate-task'); vt.add_argument('--root',type=Path,default=Path('.')); vt.add_argument('--file',required=True)
    for name in ('validate','audit-skills'): q=sub.add_parser(name); q.add_argument('--root',type=Path,default=Path('.'))
    br=sub.add_parser('build-registry'); br.add_argument('--root',type=Path,default=Path('.')); br.add_argument('--write',action='store_true')
    vf=sub.add_parser('verify'); vf.add_argument('--root',type=Path,default=Path('.'))
    args=p.parse_args(); root=args.root.resolve()
    try:
        if args.cmd=='doctor':
            result=scan_project(root)
            if args.write_profile:
                target=root/'.codex/workflows/project-profile.json'
                if target.exists() and not args.force: raise FileExistsError(f'Refusing to overwrite {target}; pass --force after review')
                target.parent.mkdir(parents=True,exist_ok=True); write_json(target,{k:v for k,v in result.items() if k!='nested_guidance'})
                result['profile_written']=str(target.relative_to(root))
        elif args.cmd=='route': result=route_task(root,args.task,max(1,min(args.max_specialists,20)))
        elif args.cmd=='plan':
            result=make_work_item(root,args.task,args.id)
            if args.write:
                target=root/'.codex/workflows/tasks'/result['task_id']/'work-item.json'
                if target.exists(): raise FileExistsError(f'Refusing to overwrite {target}')
                target.parent.mkdir(parents=True,exist_ok=True); write_json(target,result); print(f'Created {target.relative_to(root)}')
        elif args.cmd=='validate-task':
            path=Path(args.file); path=path if path.is_absolute() else root/path; item=read_json(path)
            result={'status':'PASS','task_id':item['task_id'],'execution_order':validate_task(root,item)}
        elif args.cmd in ('validate','audit-skills'): result=validate(root)
        elif args.cmd=='build-registry':
            reg=build_registry(root)
            if args.write: write_json(root/'v18/data/skill-registry.json',reg)
            result={'skill_count':reg['skill_count'],'written':args.write}
        elif args.cmd=='verify': return verify(root)
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except Exception as exc:
        print(f'V18 {args.cmd} failed: {exc}',file=sys.stderr); return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
