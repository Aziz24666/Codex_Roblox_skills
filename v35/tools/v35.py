#!/usr/bin/env python3
"""Offline V35 asset catalog, dependency, provenance, and budget validators."""
from __future__ import annotations
import argparse, json, math, re, shutil, sys, tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "35.0.0"
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_ASSETS = 5000
ASSET_KEY = re.compile(r"^[a-z0-9][a-z0-9-]{2,62}$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
OPAQUE_REF = re.compile(r"^ev-[a-z0-9]{12}$")
PROJECT_KEY = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
PROVIDER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
CATALOG_FIELDS = {"schema_version","catalog_id","project_key","generated_at","assets"}
ASSET_FIELDS = {"asset_key","kind","source_kind","source_path","provider_asset_id","ownership_scope","rights_status","moderation_status","lifecycle","version","dependencies","targets","measurements","provenance_ref","review_ref"}
MEASUREMENT_FIELDS = {"file_size_bytes","texture_width_px","texture_height_px","mesh_triangles","audio_duration_seconds","animation_keyframes"}
POLICY_FIELDS = {"schema_version","policy_id","profiles","release_requires_cleared_rights","release_requires_approved_moderation","release_requires_approved_dependencies"}
PROFILE_FIELDS = {"max_file_size_bytes","max_texture_pixels","max_mesh_triangles","max_audio_duration_seconds","max_animation_keyframes"}
KINDS = {"model","mesh","texture","image","audio","animation","package","other"}
SOURCES = {"local_source","studio_created","creator_store","external"}
OWNERSHIP = {"group","account","third_party","unknown"}
RIGHTS = {"cleared","pending","restricted","unknown"}
MODERATION = {"approved","pending","rejected","not_applicable"}
LIFECYCLE = {"draft","review","approved","released","deprecated"}
TARGETS = {"low_end_mobile","mobile","desktop","console","vr","server"}

def resolve_root(raw: str) -> Path:
    try: root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc: raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir(): raise ValueError("Project root must be an existing directory.")
    return root

def safe_project_path(root: Path, raw: str, *, must_exist: bool=False) -> Path:
    if not isinstance(raw,str) or not raw.strip() or "\x00" in raw: raise ValueError("Project-relative path must be a non-empty string.")
    if "\\" in raw or raw.startswith("/") or len(raw)>240 or (len(raw)>=3 and raw[1:3]==":/"): raise ValueError("Path must be project-relative, bounded, and use forward slashes.")
    parts=raw.split("/")
    if any(p in {"",".",".."} for p in parts): raise ValueError("Path must remain inside the selected project root.")
    probe=root
    for part in parts:
        probe=probe/part
        if probe.is_symlink(): raise ValueError("Path cannot traverse a symlink.")
    try:
        resolved=root.joinpath(*parts).resolve(strict=must_exist)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError,RuntimeError,ValueError) as exc: raise ValueError("Path resolves outside the selected project root or does not exist.") from exc
    if must_exist and not resolved.is_file(): raise ValueError("Path must identify an existing regular file.")
    return resolved

def safe_output_path(root: Path, raw: str) -> Path:
    target=safe_project_path(root,raw)
    target.parent.mkdir(parents=True,exist_ok=True)
    parent=target.parent.resolve(strict=True)
    if not parent.is_relative_to(root.resolve(strict=True)): raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()): raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent/target.name

def reject_constant(value: str) -> None: raise ValueError(f"Invalid JSON numeric constant: {value}")

def load_json(root: Path, raw: str) -> tuple[Path,Any]:
    path=safe_project_path(root,raw,must_exist=True)
    try:
        if path.stat().st_size>MAX_JSON_BYTES: raise ValueError(f"{path.relative_to(root)} exceeds the {MAX_JSON_BYTES}-byte JSON limit.")
        data=json.loads(path.read_text(encoding="utf-8-sig"),parse_constant=reject_constant)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path,data

def write_json(path: Path, value: dict[str,Any]) -> None:
    rendered=json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    fd,temp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=path.parent)
    try:
        with open(fd,"w",encoding="utf-8",closefd=True) as stream: stream.write(rendered); stream.flush()
        Path(temp).replace(path)
    finally:
        try: Path(temp).unlink()
        except FileNotFoundError: pass

def valid_int(value: Any, minimum: int=0, maximum: int=2**63-1) -> bool:
    return isinstance(value,int) and not isinstance(value,bool) and minimum<=value<=maximum

def valid_number(value: Any, minimum: float=0.0) -> bool:
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(float(value)) and float(value)>=minimum

def valid_ref(value: Any) -> bool: return isinstance(value,str) and OPAQUE_REF.fullmatch(value) is not None

def valid_time(value: Any) -> bool:
    if not isinstance(value,str) or len(value)>40: return False
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError: return False

def exact_fields(data: dict, required: set[str], allowed: set[str], label: str) -> list[str]:
    out=[]; missing=sorted(required-data.keys()); unknown=sorted(data.keys()-allowed)
    if missing: out.append(f"{label} is missing required field(s): {', '.join(missing)}.")
    if unknown: out.append(f"{label} has unsupported field(s): {', '.join(unknown)}.")
    return out

def validate_catalog(data: Any, root: Path) -> list[str]:
    problems=[]
    if not isinstance(data,dict): return ["Catalog must be a JSON object."]
    problems.extend(exact_fields(data,CATALOG_FIELDS,CATALOG_FIELDS,"Catalog"))
    if data.get("schema_version")!=1 or isinstance(data.get("schema_version"),bool): problems.append("Catalog schema_version must be integer 1.")
    if not isinstance(data.get("catalog_id"),str) or not re.fullmatch(r"asset-catalog-[a-z0-9]{8,24}",data["catalog_id"]): problems.append("catalog_id must use asset-catalog- followed by 8-24 lowercase letters or digits.")
    if not isinstance(data.get("project_key"),str) or not PROJECT_KEY.fullmatch(data["project_key"]): problems.append("project_key must be a lowercase project slug (2-63 characters).")
    if not valid_time(data.get("generated_at")): problems.append("generated_at must be an ISO-8601 timestamp with a timezone.")
    assets=data.get("assets")
    if not isinstance(assets,list) or not 1<=len(assets)<=MAX_ASSETS: return problems+[f"assets must contain 1-{MAX_ASSETS} records."]
    records={}
    for i,item in enumerate(assets):
        label=f"assets[{i}]"
        if not isinstance(item,dict): problems.append(f"{label} must be an object."); continue
        required=ASSET_FIELDS-{"source_path","provider_asset_id","review_ref"}
        problems.extend(exact_fields(item,required,ASSET_FIELDS,label))
        key=item.get("asset_key")
        if not isinstance(key,str) or not ASSET_KEY.fullmatch(key): problems.append(f"{label}.asset_key must be a lowercase stable key (3-63 characters).")
        elif key in records: problems.append(f"Duplicate asset_key: {key}.")
        else: records[key]=item
        enum_fields={"kind":KINDS,"source_kind":SOURCES,"ownership_scope":OWNERSHIP,"rights_status":RIGHTS,"moderation_status":MODERATION,"lifecycle":LIFECYCLE}
        for field,allowed in enum_fields.items():
            value=item.get(field)
            if not isinstance(value,str) or value not in allowed: problems.append(f"{label}.{field} must be one of: {', '.join(sorted(allowed))}.")
        if not isinstance(item.get("version"),str) or not SEMVER.fullmatch(item["version"]): problems.append(f"{label}.version must use MAJOR.MINOR.PATCH numeric format.")
        if not valid_ref(item.get("provenance_ref")): problems.append(f"{label}.provenance_ref must be an opaque ev- reference.")
        if "review_ref" in item and not valid_ref(item["review_ref"]): problems.append(f"{label}.review_ref must be an opaque ev- reference when supplied.")
        if "provider_asset_id" in item and (not isinstance(item["provider_asset_id"],str) or not PROVIDER_ID.fullmatch(item["provider_asset_id"])): problems.append(f"{label}.provider_asset_id contains unsupported characters or length.")
        source_kind=item.get("source_kind")
        if source_kind=="local_source":
            if not isinstance(item.get("source_path"),str): problems.append(f"{label}.source_path is required for local_source assets.")
            else:
                try:
                    path=safe_project_path(root,item["source_path"],must_exist=True)
                    measured=item.get("measurements",{})
                    recorded=measured.get("file_size_bytes") if isinstance(measured,dict) else None
                    if recorded is not None and valid_int(recorded,1) and path.stat().st_size!=recorded: problems.append(f"{label}.measurements.file_size_bytes does not match the local source file.")
                except (ValueError,OSError) as exc: problems.append(f"{label}.source_path is invalid: {exc}")
        elif "source_path" in item: problems.append(f"{label}.source_path is only allowed for local_source assets.")
        targets=item.get("targets")
        if not isinstance(targets,list) or not targets or len(targets)>len(TARGETS): problems.append(f"{label}.targets must be a non-empty list of supported device profiles.")
        elif any(not isinstance(t,str) or t not in TARGETS for t in targets) or len(set(targets))!=len(targets): problems.append(f"{label}.targets contains duplicate or unsupported profiles.")
        deps=item.get("dependencies")
        if not isinstance(deps,list) or len(deps)>200: problems.append(f"{label}.dependencies must be a list of at most 200 asset keys.")
        elif any(not isinstance(d,str) or not ASSET_KEY.fullmatch(d) for d in deps) or len(set(deps))!=len(deps): problems.append(f"{label}.dependencies contains invalid or duplicate asset keys.")
        elif key in deps: problems.append(f"{label} cannot depend on itself.")
        measurements=item.get("measurements",{})
        if not isinstance(measurements,dict): problems.append(f"{label}.measurements must be an object.")
        else:
            for field in measurements.keys()-MEASUREMENT_FIELDS: problems.append(f"{label}.measurements has unsupported field: {field}.")
            for field,value in measurements.items():
                if field in {"file_size_bytes","texture_width_px","texture_height_px","mesh_triangles","animation_keyframes"}:
                    if not valid_int(value,1): problems.append(f"{label}.measurements.{field} must be a positive integer.")
                elif not valid_number(value,0.000001): problems.append(f"{label}.measurements.{field} must be a finite positive number.")
    for key,item in records.items():
        for dep in item.get("dependencies",[]) if isinstance(item.get("dependencies"),list) else []:
            if isinstance(dep,str) and dep not in records: problems.append(f"Asset {key} references missing dependency {dep}.")
    # Iterative depth-first traversal avoids recursion failure on large dependency chains.
    state={}; reported=set()
    for start in records:
        if state.get(start,0): continue
        stack=[(start,0)]; route=[]
        while stack:
            key,index=stack[-1]
            if state.get(key,0)==0: state[key]=1; route.append(key)
            deps=records[key].get("dependencies",[])
            deps=deps if isinstance(deps,list) else []
            if index>=len(deps):
                state[key]=2; stack.pop()
                if route and route[-1]==key: route.pop()
                continue
            dep=deps[index]; stack[-1]=(key,index+1)
            if not isinstance(dep,str) or dep not in records: continue
            if state.get(dep,0)==0: stack.append((dep,0))
            elif state.get(dep)==1:
                cycle=tuple(route[route.index(dep):]+[dep]) if dep in route else (dep,key,dep)
                if cycle not in reported: reported.add(cycle); problems.append("Asset dependency cycle: "+" -> ".join(cycle)+".")
    return problems

def validate_policy(data: Any) -> list[str]:
    if not isinstance(data,dict): return ["Budget policy must be a JSON object."]
    problems=exact_fields(data,POLICY_FIELDS,POLICY_FIELDS,"Budget policy")
    if data.get("schema_version")!=1 or isinstance(data.get("schema_version"),bool): problems.append("Budget policy schema_version must be integer 1.")
    if not isinstance(data.get("policy_id"),str) or not re.fullmatch(r"asset-policy-[a-z0-9]{8,24}",data["policy_id"]): problems.append("policy_id must use asset-policy- followed by 8-24 lowercase letters or digits.")
    for flag in ("release_requires_cleared_rights","release_requires_approved_moderation","release_requires_approved_dependencies"):
        if not isinstance(data.get(flag),bool): problems.append(f"{flag} must be boolean.")
    profiles=data.get("profiles")
    if not isinstance(profiles,dict) or not profiles: return problems+["profiles must be a non-empty object."]
    if any(not isinstance(name,str) or name not in TARGETS for name in profiles): problems.append("profiles contains unsupported device profile(s).")
    for name,limits in profiles.items():
        if not isinstance(limits,dict): problems.append(f"profiles.{name} must be an object."); continue
        if limits.keys()-PROFILE_FIELDS: problems.append(f"profiles.{name} contains unsupported budget fields.")
        for field,value in limits.items():
            if field in {"max_file_size_bytes","max_texture_pixels","max_mesh_triangles","max_animation_keyframes"}:
                if not valid_int(value,1): problems.append(f"profiles.{name}.{field} must be a positive integer.")
            elif not valid_number(value,0.000001): problems.append(f"profiles.{name}.{field} must be a finite positive number.")
    return problems

def catalog_audit(catalog: dict, policy: dict, *, release_ready: bool=False) -> dict[str,Any]:
    issues=[]; records={x["asset_key"]:x for x in catalog.get("assets",[]) if isinstance(x,dict) and isinstance(x.get("asset_key"),str)}
    profiles=policy.get("profiles",{})
    for key,item in records.items():
        life=item.get("lifecycle"); rights=item.get("rights_status"); moderation=item.get("moderation_status")
        def add(severity,code,message): issues.append({"asset_key":key,"severity":severity,"code":code,"message":message})
        if rights!="cleared":
            required=policy.get("release_requires_cleared_rights",True)
            add("blocker" if required and (release_ready or life in {"approved","released"}) else "warning","rights_not_cleared","Rights status has not been confirmed as cleared by an authorized reviewer.")
        if moderation=="rejected": add("blocker","moderation_rejected","Asset review is marked rejected; do not ship this asset.")
        elif moderation=="pending":
            required=policy.get("release_requires_approved_moderation",True)
            add("blocker" if required and (release_ready or life=="released") else "warning","moderation_pending","Asset moderation review is pending.")
        if item.get("ownership_scope")=="unknown": add("blocker" if release_ready or life in {"approved","released"} else "warning","ownership_unknown","Record group, account, or third-party ownership scope.")
        if life in {"approved","released"} and not valid_ref(item.get("review_ref")): add("blocker" if release_ready else "warning","review_evidence_missing","Approved/released asset has no opaque review evidence reference.")
        for dep in item.get("dependencies",[]):
            dependency=records.get(dep)
            if dependency and life in {"approved","released"} and dependency.get("lifecycle") not in {"approved","released"}:
                required=policy.get("release_requires_approved_dependencies",True)
                add("blocker" if required and (release_ready or life=="released") else "warning","dependency_not_ready",f"Dependency {dep} is not approved or released.")
        measurements=item.get("measurements",{})
        for target in item.get("targets",[]):
            limits=profiles.get(target,{})
            checks=[]
            if "max_file_size_bytes" in limits and "file_size_bytes" in measurements: checks.append(("file_size_bytes","max_file_size_bytes"))
            kind=item.get("kind")
            if kind in {"texture","image"} and "max_texture_pixels" in limits:
                width,height=measurements.get("texture_width_px"),measurements.get("texture_height_px")
                if valid_int(width,1) and valid_int(height,1): checks.append(("__texture_pixels__","max_texture_pixels"))
                else: add("warning","measurement_missing",f"Texture dimensions are missing for target {target}.")
            if kind in {"mesh","model","package"} and "max_mesh_triangles" in limits:
                if "mesh_triangles" in measurements: checks.append(("mesh_triangles","max_mesh_triangles"))
                else: add("warning","measurement_missing",f"Mesh triangle count is missing for target {target}.")
            if kind=="audio" and "max_audio_duration_seconds" in limits:
                if "audio_duration_seconds" in measurements: checks.append(("audio_duration_seconds","max_audio_duration_seconds"))
                else: add("warning","measurement_missing",f"Audio duration is missing for target {target}.")
            if kind=="animation" and "max_animation_keyframes" in limits:
                if "animation_keyframes" in measurements: checks.append(("animation_keyframes","max_animation_keyframes"))
                else: add("warning","measurement_missing",f"Animation keyframe count is missing for target {target}.")
            for metric,budget in checks:
                actual=measurements["texture_width_px"]*measurements["texture_height_px"] if metric=="__texture_pixels__" else measurements[metric]
                if actual>limits[budget]: add("blocker","budget_exceeded",f"{metric}={actual} exceeds {target} budget {budget}={limits[budget]}.")
    issues.sort(key=lambda x:({"blocker":0,"warning":1,"info":2}.get(x["severity"],3),x["asset_key"],x["code"]))
    return {"schema_version":1,"catalog_id":catalog.get("catalog_id"),"policy_id":policy.get("policy_id"),"release_ready_mode":release_ready,"asset_count":len(records),"issue_count":len(issues),"blocker_count":sum(x["severity"]=="blocker" for x in issues),"warning_count":sum(x["severity"]=="warning" for x in issues),"issues":issues,"disclaimer":"This report validates supplied metadata and project policy; it does not determine legal rights, Roblox moderation approval, or asset-store permissions."}

def compare_catalogs(baseline: dict,candidate: dict) -> dict[str,Any]:
    old={x["asset_key"]:x for x in baseline["assets"]}; new={x["asset_key"]:x for x in candidate["assets"]}
    added=sorted(new.keys()-old.keys()); removed=sorted(old.keys()-new.keys()); changed=[]; regressions=[]
    fields=("kind","source_kind","source_path","provider_asset_id","ownership_scope","rights_status","moderation_status","lifecycle","version","dependencies","targets","measurements","provenance_ref","review_ref")
    for key in sorted(old.keys()&new.keys()):
        delta=[field for field in fields if old[key].get(field)!=new[key].get(field)]
        if delta: changed.append({"asset_key":key,"changed_fields":delta})
        if old[key].get("rights_status")=="cleared" and new[key].get("rights_status")!="cleared": regressions.append({"asset_key":key,"code":"rights_status_regressed"})
        if old[key].get("moderation_status")=="approved" and new[key].get("moderation_status") in {"pending","rejected"}: regressions.append({"asset_key":key,"code":"moderation_status_regressed"})
        if old[key].get("lifecycle")=="released" and new[key].get("lifecycle") not in {"released","deprecated"}: regressions.append({"asset_key":key,"code":"released_asset_lifecycle_regressed"})
    dependents=[]
    for key in removed:
        used_by=sorted(x["asset_key"] for x in new.values() if key in x.get("dependencies",[]))
        if used_by: dependents.append({"asset_key":key,"required_by":used_by}); regressions.append({"asset_key":key,"code":"removed_asset_still_referenced"})
    return {"schema_version":1,"baseline_catalog_id":baseline.get("catalog_id"),"candidate_catalog_id":candidate.get("catalog_id"),"added":added,"removed":removed,"changed":changed,"removal_dependents":dependents,"regressions":regressions,"summary":{"added_count":len(added),"removed_count":len(removed),"changed_count":len(changed),"regression_count":len(regressions)},"disclaimer":"A catalog diff is a review aid; it does not publish, delete, transfer, or grant permissions to any Roblox asset."}

def main_with_args(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest="command",required=True)
    d=sub.add_parser("doctor"); d.add_argument("--root",required=True)
    v=sub.add_parser("validate-catalog"); v.add_argument("--root",required=True); v.add_argument("--catalog",required=True)
    a=sub.add_parser("audit-catalog"); a.add_argument("--root",required=True); a.add_argument("--catalog",required=True); a.add_argument("--policy",required=True); a.add_argument("--output"); a.add_argument("--release-ready",action="store_true")
    c=sub.add_parser("compare-catalogs"); c.add_argument("--root",required=True); c.add_argument("--baseline",required=True); c.add_argument("--candidate",required=True); c.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=="doctor":
            root=resolve_root(args.root); print(f"V35 {VERSION}; Python {sys.version.split()[0]}; project root: {root}")
            print("Asset evidence directory: "+("present" if (root/".codex"/"assets").is_dir() else "not initialized (optional)")); return 0
        root=resolve_root(args.root)
        if args.command=="validate-catalog":
            _,data=load_json(root,args.catalog); errors=validate_catalog(data,root)
            if errors:
                for e in errors: print("FAIL: "+e)
                return 1
            print(f"PASS: asset catalog valid ({len(data['assets'])} assets)."); return 0
        if args.command=="audit-catalog":
            _,data=load_json(root,args.catalog); _,policy=load_json(root,args.policy); errors=validate_catalog(data,root)+validate_policy(policy)
            if errors:
                for e in errors: print("FAIL: "+e)
                return 1
            report=catalog_audit(data,policy,release_ready=args.release_ready)
            if args.output: write_json(safe_output_path(root,args.output),report)
            print(json.dumps({k:report[k] for k in ("asset_count","issue_count","blocker_count","warning_count")},sort_keys=True))
            return 1 if args.release_ready and report["blocker_count"] else 0
        if args.command=="compare-catalogs":
            _,old=load_json(root,args.baseline); _,new=load_json(root,args.candidate); errors=validate_catalog(old,root)+validate_catalog(new,root)
            if errors:
                for e in errors: print("FAIL: "+e)
                return 1
            report=compare_catalogs(old,new); write_json(safe_output_path(root,args.output),report); print(json.dumps(report["summary"],sort_keys=True)); return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2
    return 2

def main() -> int: return main_with_args()
if __name__=="__main__": raise SystemExit(main())
