#!/usr/bin/env python3
"""Offline V36 accessibility, responsive UI, and localization readiness audit."""
from __future__ import annotations
import argparse, json, re, sys, tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "36.0.0"
MAX_BYTES = 2 * 1024 * 1024
MAX_SURFACES = 500
SURFACE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
OPAQUE_REF = re.compile(r"^ev-[a-z0-9]{12}$")
PLATFORMS = {"desktop","mobile","tablet","console","vr"}
INPUTS = {"keyboard_mouse","touch","gamepad","gaze"}
KINDS = {"menu","hud","prompt","tutorial","dialogue","notification","other"}
ROOT_FIELDS = {"schema_version","project_key","generated_at","target_locales","surfaces"}
SURFACE_FIELDS = {"surface_id","kind","platforms","input_methods","uses_motion","critical_audio","localization","accessibility","evidence_refs"}
LOCALIZATION_FIELDS = {"strings_externalized","text_expansion_tested","rtl_reviewed"}
ACCESSIBILITY_FIELDS = {"focus_navigation","text_scaling","non_color_cues","contrast_reviewed","critical_audio_captions","reduced_motion_option"}

def resolve_root(raw: str) -> Path:
    try: root=Path(raw).expanduser().resolve(strict=True)
    except (OSError,RuntimeError) as exc: raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir(): raise ValueError("Project root must be an existing directory.")
    return root

def safe_path(root: Path, raw: str, *, exists: bool=False) -> Path:
    if not isinstance(raw,str) or not raw or len(raw)>240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw)>2 and raw[1:3]==":/"): raise ValueError("Path must be a bounded project-relative path using forward slashes.")
    parts=raw.split("/")
    if any(p in {"",".",".."} for p in parts): raise ValueError("Path traversal is not allowed.")
    probe=root
    for part in parts:
        probe=probe/part
        if probe.is_symlink(): raise ValueError("Symlink traversal is not allowed.")
    try:
        result=root.joinpath(*parts).resolve(strict=exists)
        result.relative_to(root.resolve(strict=True))
    except (OSError,RuntimeError,ValueError) as exc: raise ValueError("Path resolves outside the selected project root.") from exc
    if exists and not result.is_file(): raise ValueError("Manifest must be an existing regular file.")
    return result

def load_manifest(root: Path, raw: str) -> Any:
    path=safe_path(root,raw,exists=True)
    if path.stat().st_size>MAX_BYTES: raise ValueError("Manifest exceeds the 2 MiB limit.")
    try: return json.loads(path.read_text(encoding="utf-8-sig"),parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid JSON constant: {x}")))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"Could not read valid JSON: {exc}") from exc

def valid_time(value: Any) -> bool:
    if not isinstance(value,str) or len(value)>40: return False
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError: return False

def exact(obj: dict, required: set[str], allowed: set[str], label: str) -> list[str]:
    out=[]
    missing=sorted(required-obj.keys()); unknown=sorted(obj.keys()-allowed)
    if missing: out.append(f"{label} missing required fields: {', '.join(missing)}.")
    if unknown: out.append(f"{label} has unsupported fields: {', '.join(unknown)}.")
    return out

def validate_manifest(data: Any) -> list[str]:
    issues=[]
    if not isinstance(data,dict): return ["Manifest must be a JSON object."]
    issues += exact(data,ROOT_FIELDS,ROOT_FIELDS,"Manifest")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"),bool): issues.append("schema_version must be integer 1.")
    if not isinstance(data.get("project_key"),str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,62}",data["project_key"]): issues.append("project_key must be a lowercase project slug.")
    if not valid_time(data.get("generated_at")): issues.append("generated_at must be an ISO-8601 timestamp with timezone.")
    locales=data.get("target_locales")
    if not isinstance(locales,list) or not locales or len(locales)>100 or any(not isinstance(x,str) or not re.fullmatch(r"[a-z]{2,3}(-[a-z0-9]{2,8})*",x) for x in locales): issues.append("target_locales must be a non-empty list of locale tags.")
    surfaces=data.get("surfaces")
    if not isinstance(surfaces,list) or not 1<=len(surfaces)<=MAX_SURFACES: return issues+[f"surfaces must contain 1-{MAX_SURFACES} entries."]
    seen=set()
    for i,s in enumerate(surfaces):
        label=f"surfaces[{i}]"
        if not isinstance(s,dict): issues.append(f"{label} must be an object."); continue
        issues += exact(s,SURFACE_FIELDS,SURFACE_FIELDS,label)
        sid=s.get("surface_id")
        if not isinstance(sid,str) or not SURFACE_ID.fullmatch(sid): issues.append(f"{label}.surface_id must be a lowercase stable ID.")
        elif sid in seen: issues.append(f"Duplicate surface_id: {sid}.")
        else: seen.add(sid)
        if s.get("kind") not in KINDS: issues.append(f"{label}.kind is unsupported.")
        for field,allowed in (("platforms",PLATFORMS),("input_methods",INPUTS)):
            values=s.get(field)
            if not isinstance(values,list) or not values or any(not isinstance(v,str) or v not in allowed for v in values) or len(set(values))!=len(values): issues.append(f"{label}.{field} must be a non-empty unique list of supported values.")
        for field in ("uses_motion","critical_audio"):
            if not isinstance(s.get(field),bool): issues.append(f"{label}.{field} must be boolean.")
        loc=s.get("localization")
        if not isinstance(loc,dict): issues.append(f"{label}.localization must be an object.")
        else:
            issues += exact(loc,LOCALIZATION_FIELDS,LOCALIZATION_FIELDS,f"{label}.localization")
            for field in LOCALIZATION_FIELDS:
                if not isinstance(loc.get(field),bool): issues.append(f"{label}.localization.{field} must be boolean.")
        acc=s.get("accessibility")
        if not isinstance(acc,dict): issues.append(f"{label}.accessibility must be an object.")
        else:
            issues += exact(acc,ACCESSIBILITY_FIELDS,ACCESSIBILITY_FIELDS,f"{label}.accessibility")
            for field in ACCESSIBILITY_FIELDS:
                if not isinstance(acc.get(field),bool): issues.append(f"{label}.accessibility.{field} must be boolean.")
        refs=s.get("evidence_refs")
        if not isinstance(refs,list) or any(not isinstance(x,str) or not OPAQUE_REF.fullmatch(x) for x in refs): issues.append(f"{label}.evidence_refs must contain only opaque ev- references.")
    return issues

def audit_manifest(data: dict) -> dict:
    findings=[]
    locales=data.get("target_locales",[])
    has_rtl=any(isinstance(x,str) and x.split("-")[0] in {"ar","fa","he","ur"} for x in locales)
    for s in data.get("surfaces",[]):
        if not isinstance(s,dict): continue
        sid=s.get("surface_id","unknown")
        loc=s.get("localization",{}) if isinstance(s.get("localization"),dict) else {}
        acc=s.get("accessibility",{}) if isinstance(s.get("accessibility"),dict) else {}
        def add(code,severity,message): findings.append({"surface_id":sid,"code":code,"severity":severity,"message":message})
        if loc.get("strings_externalized") is not True: add("strings_not_externalized","blocker","Player-facing strings are not confirmed as externalized.")
        if loc.get("text_expansion_tested") is not True: add("text_expansion_unverified","warning","Long translated strings and text expansion have not been verified.")
        if has_rtl and loc.get("rtl_reviewed") is not True: add("rtl_review_missing","warning","At least one target locale is RTL but this surface has no recorded RTL review.")
        if acc.get("text_scaling") is not True: add("text_scaling_unverified","warning","Text scaling support has not been verified.")
        if acc.get("non_color_cues") is not True: add("non_color_cues_missing","blocker","Important information may rely on color alone.")
        if acc.get("contrast_reviewed") is not True: add("contrast_review_missing","warning","Contrast review has not been recorded.")
        if acc.get("focus_navigation") is not True and ({"keyboard_mouse","gamepad"} & set(s.get("input_methods",[]))): add("focus_navigation_missing","blocker","Keyboard/gamepad input is listed but focus navigation is not confirmed.")
        if s.get("critical_audio") is True and acc.get("critical_audio_captions") is not True: add("critical_audio_alternative_missing","blocker","Critical audio has no confirmed caption or equivalent visual/text alternative.")
        if s.get("uses_motion") is True and acc.get("reduced_motion_option") is not True: add("reduced_motion_unverified","warning","Motion is used but a reduced-motion alternative is not confirmed.")
    blockers=sum(x["severity"]=="blocker" for x in findings)
    warnings=sum(x["severity"]=="warning" for x in findings)
    return {"schema_version":1,"status":"needs_review" if findings else "reviewed_no_findings","summary":{"surfaces":len(data.get("surfaces",[])),"blockers":blockers,"warnings":warnings,"findings":len(findings)},"findings":findings,"limitations":["Offline metadata review only; no Roblox Studio inspection, runtime testing, screenshot analysis, or accessibility certification."]}
    
def write_json(root: Path, raw: str, value: dict) -> None:
    path=safe_path(root,raw); path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()): raise ValueError("Output must be a regular file.")
    fd,tmp=tempfile.mkstemp(prefix=".v36-",suffix=".tmp",dir=path.parent)
    try:
        with open(fd,"w",encoding="utf-8",closefd=True) as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False); f.write("\n"); f.flush()
        Path(tmp).replace(path)
    finally:
        try: Path(tmp).unlink()
        except FileNotFoundError: pass

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
    d=sub.add_parser("doctor"); d.add_argument("--root",required=True)
    v=sub.add_parser("validate-manifest"); v.add_argument("--root",required=True); v.add_argument("--manifest",required=True)
    a=sub.add_parser("audit"); a.add_argument("--root",required=True); a.add_argument("--manifest",required=True); a.add_argument("--output",required=True)
    args=p.parse_args()
    try:
        root=resolve_root(args.root)
        if args.command=="doctor": print(f"V{VERSION} ready | project={root}"); return 0
        data=load_manifest(root,args.manifest); errors=validate_manifest(data)
        if errors:
            for e in errors: print("FAIL: "+e)
            return 1
        if args.command=="validate-manifest": print("PASS: quality manifest is structurally valid."); return 0
        report=audit_manifest(data); write_json(root,args.output,report)
        print(f"{report['status']}: {report['summary']['blockers']} blocker(s), {report['summary']['warnings']} warning(s).")
        return 1 if report["summary"]["blockers"] else 0
    except (OSError,ValueError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
