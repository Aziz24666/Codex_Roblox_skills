#!/usr/bin/env python3
"""Offline structural validator for Roblox quest and branching-dialogue content."""
from __future__ import annotations
import argparse,json,os,re,sys,tempfile
from pathlib import Path
from typing import Any

VERSION="45.0.0"
MAX_INPUT_BYTES=2*1024*1024
SLUG=re.compile(r"^[a-z][a-z0-9-]{1,47}$")
TEXT_KEY=re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
LOCALE=re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
ROOT_FIELDS={"schema_version","project_id","build_id","default_locale","supported_locales","quests","dialogues"}
QUEST_FIELDS={"quest_id","title","summary","repeat_policy","prerequisites","start_node_id","nodes"}
QUEST_NODE_FIELDS={"node_id","kind","title","objective_type","next_node_ids"}
DIALOGUE_FIELDS={"conversation_id","title","start_node_id","nodes"}
DIALOGUE_NODE_FIELDS={"node_id","kind","speaker","text_key","text","choices"}
CHOICE_FIELDS={"choice_id","label_key","label","next_node_id"}
OBJECTIVES={"talk","interact","collect","deliver","explore","wait","custom"}

def _fields(obj:dict,expected:set[str],label:str)->list[str]:
    missing,extra=sorted(expected-obj.keys()),sorted(obj.keys()-expected)
    out=[]
    if missing: out.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra: out.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return out

def _string(v:Any,lo:int,hi:int)->bool:
    return isinstance(v,str) and lo<=len(v.strip())<=hi

def _slug(v:Any)->bool:
    return isinstance(v,str) and bool(SLUG.fullmatch(v))

def _id_list(value:Any,label:str,errors:list[str],limit:int)->list[str]:
    if not isinstance(value,list) or len(value)>limit:
        errors.append(f"{label} must be a list with at most {limit} entries."); return []
    seen=set(); clean=[]
    for item in value:
        if not _slug(item): errors.append(f"{label} entries must be lowercase stable IDs.")
        elif item in seen: errors.append(f"{label} contains duplicate ID: {item}.")
        if isinstance(item,str): seen.add(item); clean.append(item)
    return clean

def _reachable(start:str,edges:dict[str,list[str]])->set[str]:
    seen=set(); stack=[start]
    while stack:
        node=stack.pop()
        if node in seen or node not in edges: continue
        seen.add(node); stack.extend(edges[node])
    return seen

def _has_cycle(edges:dict[str,list[str]])->bool:
    indegree={n:0 for n in edges}
    for targets in edges.values():
        for t in targets:
            if t in indegree: indegree[t]+=1
    queue=[n for n,d in indegree.items() if d==0]; done=0
    while queue:
        node=queue.pop(); done+=1
        for t in edges[node]:
            if t in indegree:
                indegree[t]-=1
                if indegree[t]==0: queue.append(t)
    return done!=len(edges)

def _can_reach_terminal(edges:dict[str,list[str]],terminals:set[str])->set[str]:
    can=set(terminals); changed=True
    while changed:
        changed=False
        for node,targets in edges.items():
            if node not in can and any(t in can for t in targets): can.add(node); changed=True
    return can

def validate_project(project:Any)->list[str]:
    errors=[]
    if not isinstance(project,dict): return ["Narrative project must be a JSON object."]
    errors+=_fields(project,ROOT_FIELDS,"project")
    if project.get("schema_version")!=1 or isinstance(project.get("schema_version"),bool): errors.append("schema_version must be integer 1.")
    if not _slug(project.get("project_id")): errors.append("project_id must be a lowercase stable ID.")
    if not _string(project.get("build_id"),1,80): errors.append("build_id must contain 1-80 characters.")
    default=project.get("default_locale")
    if not isinstance(default,str) or not LOCALE.fullmatch(default): errors.append("default_locale must be a locale tag such as en-US.")
    locales=project.get("supported_locales")
    if not isinstance(locales,list) or not 1<=len(locales)<=10:
        errors.append("supported_locales must contain 1-10 locale tags."); locales=[]
    else:
        seen=set()
        for locale in locales:
            if not isinstance(locale,str) or not LOCALE.fullmatch(locale): errors.append("supported_locales contains an invalid locale tag.")
            elif locale in seen: errors.append(f"Duplicate supported locale: {locale}.")
            if isinstance(locale,str): seen.add(locale)
        if default not in locales: errors.append("default_locale must be included in supported_locales.")

    quests=project.get("quests")
    if not isinstance(quests,list) or len(quests)>200: errors.append("quests must be a list with at most 200 entries."); quests=[]
    qids=set(); prereq={}
    for i,q in enumerate(quests):
        label=f"quests[{i}]"
        if not isinstance(q,dict): errors.append(f"{label} must be an object."); continue
        errors+=_fields(q,QUEST_FIELDS,label)
        qid=q.get("quest_id")
        if not _slug(qid): errors.append(f"{label}.quest_id must be a lowercase stable ID.")
        elif qid in qids: errors.append(f"Duplicate quest_id: {qid}.")
        else: qids.add(qid)
        if not _string(q.get("title"),4,100): errors.append(f"{label}.title must contain 4-100 characters.")
        if not _string(q.get("summary"),20,500): errors.append(f"{label}.summary must contain 20-500 characters.")
        if q.get("repeat_policy") not in {"once","repeatable"}: errors.append(f"{label}.repeat_policy must be once or repeatable.")
        deps=_id_list(q.get("prerequisites"),f"{label}.prerequisites",errors,200)
        if _slug(qid): prereq[qid]=deps
        nodes=q.get("nodes")
        if not isinstance(nodes,list) or not 1<=len(nodes)<=500: errors.append(f"{label}.nodes must contain 1-500 nodes."); continue
        ids=set(); raw=[]
        for j,n in enumerate(nodes):
            nl=f"{label}.nodes[{j}]"
            if not isinstance(n,dict): errors.append(f"{nl} must be an object."); continue
            errors+=_fields(n,QUEST_NODE_FIELDS,nl)
            nid=n.get("node_id")
            if not _slug(nid): errors.append(f"{nl}.node_id must be a lowercase stable ID.")
            elif nid in ids: errors.append(f"{label} has duplicate node_id: {nid}.")
            else: ids.add(nid)
            kind=n.get("kind")
            if kind not in {"objective","branch","complete"}: errors.append(f"{nl}.kind must be objective, branch, or complete.")
            if not _string(n.get("title"),3,100): errors.append(f"{nl}.title must contain 3-100 characters.")
            objective=n.get("objective_type")
            if kind=="objective" and objective not in OBJECTIVES: errors.append(f"{nl}.objective_type is required and must be supported.")
            if kind!="objective" and objective is not None: errors.append(f"{nl}.objective_type must be null for branch/complete nodes.")
            targets=_id_list(n.get("next_node_ids"),f"{nl}.next_node_ids",errors,4)
            if kind=="objective" and len(targets)!=1: errors.append(f"{nl} objective nodes must have exactly one outgoing edge.")
            if kind=="branch" and not 2<=len(targets)<=4: errors.append(f"{nl} branch nodes must have 2-4 outgoing edges.")
            if kind=="complete" and targets: errors.append(f"{nl} completion nodes must not have outgoing edges.")
            raw.append(n)
        start=q.get("start_node_id")
        if not _slug(start) or start not in ids: errors.append(f"{label}.start_node_id must reference a declared node.")
        edges={}; terminals=set()
        for n in raw:
            nid=n.get("node_id")
            if not isinstance(nid,str) or nid not in ids: continue
            targets=n.get("next_node_ids",[])
            edges[nid]=[t for t in targets if isinstance(t,str)] if isinstance(targets,list) else []
            if n.get("kind")=="complete": terminals.add(nid)
        for nid,targets in edges.items():
            for t in targets:
                if t not in ids: errors.append(f"{label} node {nid} references missing node {t}.")
        if not terminals: errors.append(f"{label} must contain at least one completion node.")
        if isinstance(start,str) and start in edges:
            unreachable=sorted(ids-_reachable(start,edges))
            if unreachable: errors.append(f"{label} has unreachable nodes: {', '.join(unreachable)}.")
            if _has_cycle(edges): errors.append(f"{label} quest progression graph contains a cycle.")
            stuck=sorted(ids-_can_reach_terminal(edges,terminals))
            if stuck: errors.append(f"{label} nodes cannot reach a completion: {', '.join(stuck)}.")

    for qid,deps in prereq.items():
        for dep in deps:
            if dep not in qids: errors.append(f"Quest {qid} references missing prerequisite {dep}.")
            if dep==qid: errors.append(f"Quest {qid} cannot require itself.")
    if prereq and _has_cycle(prereq): errors.append("Quest prerequisite graph contains a cycle.")

    dialogues=project.get("dialogues")
    if not isinstance(dialogues,list) or len(dialogues)>200: errors.append("dialogues must be a list with at most 200 conversations."); dialogues=[]
    cids=set(); textkeys=set()
    for i,d in enumerate(dialogues):
        label=f"dialogues[{i}]"
        if not isinstance(d,dict): errors.append(f"{label} must be an object."); continue
        errors+=_fields(d,DIALOGUE_FIELDS,label)
        cid=d.get("conversation_id")
        if not _slug(cid): errors.append(f"{label}.conversation_id must be a lowercase stable ID.")
        elif cid in cids: errors.append(f"Duplicate conversation_id: {cid}.")
        else: cids.add(cid)
        if not _string(d.get("title"),3,100): errors.append(f"{label}.title must contain 3-100 characters.")
        nodes=d.get("nodes")
        if not isinstance(nodes,list) or not 1<=len(nodes)<=500: errors.append(f"{label}.nodes must contain 1-500 nodes."); continue
        ids=set(); raw=[]
        for j,n in enumerate(nodes):
            nl=f"{label}.nodes[{j}]"
            if not isinstance(n,dict): errors.append(f"{nl} must be an object."); continue
            errors+=_fields(n,DIALOGUE_NODE_FIELDS,nl)
            nid=n.get("node_id")
            if not _slug(nid): errors.append(f"{nl}.node_id must be a lowercase stable ID.")
            elif nid in ids: errors.append(f"{label} has duplicate node_id: {nid}.")
            else: ids.add(nid)
            kind=n.get("kind")
            if kind not in {"line","end"}: errors.append(f"{nl}.kind must be line or end.")
            if not _string(n.get("speaker"),1,60): errors.append(f"{nl}.speaker must contain 1-60 characters.")
            key=n.get("text_key")
            if not isinstance(key,str) or not TEXT_KEY.fullmatch(key): errors.append(f"{nl}.text_key must be a stable localization key.")
            elif key in textkeys: errors.append(f"Duplicate localization key: {key}.")
            else: textkeys.add(key)
            if not _string(n.get("text"),1,400): errors.append(f"{nl}.text must contain 1-400 characters.")
            choices=n.get("choices")
            if not isinstance(choices,list) or len(choices)>4: errors.append(f"{nl}.choices must contain at most four choices."); choices=[]
            if kind=="line" and not 1<=len(choices)<=4: errors.append(f"{nl} line nodes must have 1-4 choices.")
            if kind=="end" and choices: errors.append(f"{nl} end nodes must not have choices.")
            choiceids=set(); clean=[]
            for k,c in enumerate(choices):
                cl=f"{nl}.choices[{k}]"
                if not isinstance(c,dict): errors.append(f"{cl} must be an object."); continue
                errors+=_fields(c,CHOICE_FIELDS,cl)
                choice=c.get("choice_id")
                if not _slug(choice): errors.append(f"{cl}.choice_id must be a lowercase stable ID.")
                elif choice in choiceids: errors.append(f"{nl} has duplicate choice_id: {choice}.")
                else: choiceids.add(choice)
                lk=c.get("label_key")
                if not isinstance(lk,str) or not TEXT_KEY.fullmatch(lk): errors.append(f"{cl}.label_key must be a stable localization key.")
                elif lk in textkeys: errors.append(f"Duplicate localization key: {lk}.")
                else: textkeys.add(lk)
                if not _string(c.get("label"),1,80): errors.append(f"{cl}.label must contain 1-80 characters.")
                if not _slug(c.get("next_node_id")): errors.append(f"{cl}.next_node_id must be a stable node ID.")
                clean.append(c)
            raw.append((n,clean))
        start=d.get("start_node_id")
        if not _slug(start) or start not in ids: errors.append(f"{label}.start_node_id must reference a declared node.")
        edges={}; endings=set()
        for n,choices in raw:
            nid=n.get("node_id")
            if not isinstance(nid,str) or nid not in ids: continue
            edges[nid]=[c.get("next_node_id") for c in choices if isinstance(c.get("next_node_id"),str)]
            if n.get("kind")=="end": endings.add(nid)
        for nid,targets in edges.items():
            for t in targets:
                if t not in ids: errors.append(f"{label} node {nid} references missing node {t}.")
        if not endings: errors.append(f"{label} must contain at least one end node.")
        if isinstance(start,str) and start in edges:
            unreachable=sorted(ids-_reachable(start,edges))
            if unreachable: errors.append(f"{label} has unreachable nodes: {', '.join(unreachable)}.")
            stuck=sorted(ids-_can_reach_terminal(edges,endings))
            if stuck: errors.append(f"{label} nodes cannot reach an ending: {', '.join(stuck)}.")
    return errors

def audit_project(project:Any)->dict:
    errors=validate_project(project)
    quests=project.get("quests",[]) if isinstance(project,dict) else []
    dialogs=project.get("dialogues",[]) if isinstance(project,dict) else []
    return {"schema_version":1,"tool_version":VERSION,"project_id":project.get("project_id") if isinstance(project,dict) else None,
      "status":"blocked" if errors else "ready_for_human_content_review","errors":errors,
      "warnings":["Structural validation does not establish that objectives are understandable, achievable, or fun.",
      "Review outcomes, localization, accessibility, and player safety with humans.",
      "Dialogue loops are allowed only when every authored node can still reach an ending.",
      "The CLI does not inspect Luau, player profiles, remote handlers, Roblox Studio, or live experiences."],
      "quest_count":len(quests) if isinstance(quests,list) else 0,"dialogue_count":len(dialogs) if isinstance(dialogs,list) else 0,
      "human_review_required":True}

def _pairs_no_duplicates(pairs:list[tuple[str,Any]])->dict:
    result={}
    for key,value in pairs:
        if key in result: raise ValueError(f"Duplicate JSON key: {key}")
        result[key]=value
    return result

def _reject_constant(value:str):
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")

def safe_path(root:Path,relative:str)->Path:
    root=root.expanduser().resolve()
    if not root.is_dir(): raise ValueError("Project root must exist and be a directory.")
    if not isinstance(relative,str) or not relative or "\\" in relative: raise ValueError("Path must be project-relative and use forward slashes.")
    candidate=Path(relative)
    if candidate.is_absolute() or not candidate.parts or any(p in {"",".",".."} for p in candidate.parts): raise ValueError("Absolute paths, empty segments, and traversal are not allowed.")
    current=root
    for part in candidate.parts:
        current=current/part
        if current.is_symlink(): raise ValueError("Symlink paths are not allowed.")
    resolved=current.resolve()
    if not resolved.is_relative_to(root): raise ValueError("Path escapes the project root.")
    return resolved

def load_json(root:Path,relative:str)->Any:
    path=safe_path(root,relative)
    if not path.is_file(): raise ValueError(f"Input file does not exist: {relative}")
    if path.stat().st_size>MAX_INPUT_BYTES: raise ValueError(f"Input exceeds the {MAX_INPUT_BYTES}-byte limit: {relative}")
    return json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=_pairs_no_duplicates,parse_constant=_reject_constant)

def write_report(root:Path,relative:str,report:dict)->None:
    path=safe_path(root,relative); path.parent.mkdir(parents=True,exist_ok=True); tmp=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=path.parent,delete=False) as handle:
            tmp=handle.name; json.dump(report,handle,indent=2,sort_keys=True,allow_nan=False); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        if tmp and os.path.exists(tmp): os.unlink(tmp)

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); subs=parser.add_subparsers(dest="command",required=True)
    doc=subs.add_parser("doctor"); doc.add_argument("--root",required=True,type=Path)
    for name in ("validate","audit"):
        cmd=subs.add_parser(name); cmd.add_argument("--root",required=True,type=Path); cmd.add_argument("--project",required=True)
        if name=="audit": cmd.add_argument("--output",required=True)
    args=parser.parse_args()
    try:
        root=args.root.expanduser().resolve()
        if not root.is_dir(): raise ValueError("Project root must exist and be a directory.")
        if args.command=="doctor": print(f"V45 doctor: root={root}; Python={sys.version_info.major}.{sys.version_info.minor}; offline mode."); return 0
        project=load_json(root,args.project); errors=validate_project(project)
        if args.command=="validate":
            for e in errors: print("FAIL: "+e)
            if errors: return 1
            print("PASS: quest and dialogue graphs are structurally valid."); return 0
        report=audit_project(project); write_report(root,args.output,report)
        for e in errors: print("FAIL: "+e)
        for warning in report["warnings"]: print("WARN: "+warning)
        print(f"Narrative audit: {report['status']}."); return 1 if errors else 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print("ERROR: "+str(exc)); return 2

if __name__=="__main__": raise SystemExit(main())
