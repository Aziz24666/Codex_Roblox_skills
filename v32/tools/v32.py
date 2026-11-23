#!/usr/bin/env python3
"""Offline Roblox player-safety, text-filtering, and moderation-record checks."""
from __future__ import annotations
import argparse, json, os, re, shutil, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "32.0.0"
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_JSON_BYTES, MAX_FINDINGS = 10_000, 2*1024*1024, 128*1024*1024, 2*1024*1024, 500
MAX_REGISTER_CASES = 10_000
SKIP_DIRS = {".git",".agents",".codex",".venv","venv","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache","node_modules","target","build","dist",".idea",".vscode"}
SEVERITIES = {"low","standard","high","critical"}
ROLES = {"moderator","senior_moderator","safety_lead"}
SOURCES = {"platform_report","in_experience_report","moderator_observation","safety_dashboard"}
CATEGORIES = {"harassment","privacy","scam_or_deception","spam","inappropriate_content","exploit_abuse","other"}
CHANNELS = {"text","voice","avatar_or_asset","audio","experience","gameplay","other"}
STATUSES = {"open","in_review","escalated","resolved","closed","appeal_pending","appeal_resolved"}
DECISIONS = {"no_action","policy_reminder","temporary_feature_restriction","temporary_ban","permanent_ban","refer_to_platform","insufficient_evidence"}
SUMMARY_CODES = {"user_report_submitted","trusted_moderator_observation","safety_dashboard_signal","content_review_request","other"}
CASE_REF=re.compile(r"^case-[a-z0-9]{12}$"); EVIDENCE_REF=re.compile(r"^ev-[a-z0-9]{12}$"); APPEAL_REF=re.compile(r"^appeal-[a-z0-9]{12}$")
DEFAULT_POLICY=".codex/moderation/moderation-policy.json"
DEFAULT_CASE=".codex/moderation/moderation-case.json"
DEFAULT_REGISTER=".codex/moderation/moderation-register.json"
DEFAULT_AUDIT=".codex/reports/v32-player-safety-audit.json"
POLICY_REQUIRED={"schema_version","review_sla_hours","evidence_retention_days","appeal_window_days","require_second_review_for","automated_enforcement"}
CASE_REQUIRED={"schema_version","case_ref","created_at","source","category","channel","severity","status","summary_code","evidence_refs"}
CASE_OPTIONAL={"reviewed_at","reviewer_role","decision_code","appeal_ref","appeal_outcome","second_reviewer_role"}

def resolve_root(raw:str)->Path:
    try: root=Path(raw).expanduser().resolve(strict=True)
    except (OSError,RuntimeError) as exc: raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir(): raise ValueError("Project root must be an existing directory.")
    return root

def safe_project_path(root:Path,raw:str,*,must_exist:bool=False)->Path:
    if not isinstance(raw,str) or not raw.strip() or "\x00" in raw: raise ValueError("Project-relative path must be a non-empty string.")
    if "\\" in raw or raw.startswith("/") or re.match(r"^[A-Za-z]:",raw): raise ValueError("Path must be project-relative and use forward slashes.")
    parts=raw.split("/")
    if any(p in {"",".",".."} for p in parts): raise ValueError("Path must stay inside the selected project root.")
    candidate=root.joinpath(*parts); probe=root
    for part in parts:
        probe=probe/part
        if probe.is_symlink(): raise ValueError("Path cannot traverse a symlink.")
    try:
        resolved=candidate.resolve(strict=must_exist); resolved.relative_to(root.resolve(strict=True))
    except (OSError,RuntimeError,ValueError) as exc: raise ValueError("Path resolves outside the selected project root or does not exist.") from exc
    if must_exist and not resolved.is_file(): raise ValueError("Path must identify an existing regular file.")
    return resolved

def safe_output_path(root:Path,raw:str)->Path:
    target=safe_project_path(root,raw); target.parent.mkdir(parents=True,exist_ok=True); parent=target.parent.resolve(strict=True)
    if not parent.is_relative_to(root.resolve(strict=True)): raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()): raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent/target.name

def atomic_write_json(path:Path,payload:dict[str,Any])->None:
    encoded=json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    fd,temp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        try: os.unlink(temp)
        except FileNotFoundError: pass

def load_json(root:Path,raw:str)->tuple[Path,Any]:
    path=safe_project_path(root,raw,must_exist=True)
    try:
        if path.stat().st_size>MAX_JSON_BYTES: raise ValueError(f"{path.relative_to(root)} exceeds the {MAX_JSON_BYTES}-byte JSON input limit.")
        data=json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path,data

def positive_integer(value:Any)->bool: return isinstance(value,int) and not isinstance(value,bool) and value>0

def parse_timestamp(value:Any)->datetime|None:
    if not isinstance(value,str) or not value.strip(): return None
    try: parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError: return None
    if parsed.tzinfo is None or parsed.utcoffset() is None: return None
    return parsed.astimezone(timezone.utc)

def allowed(value:Any,values:set[str])->bool: return isinstance(value,str) and value in values

def validate_policy(data:Any)->list[str]:
    errors=[]
    if not isinstance(data,dict): return ["Moderation policy must be a JSON object."]
    extra=set(data)-POLICY_REQUIRED; missing=POLICY_REQUIRED-set(data)
    if extra: errors.append("Moderation policy contains unsupported fields.")
    if missing: errors.append("Moderation policy is missing required fields: "+", ".join(sorted(missing))+".")
    if data.get("schema_version")!=1: errors.append("schema_version must equal 1.")
    sla=data.get("review_sla_hours")
    if not isinstance(sla,dict) or set(sla)!=SEVERITIES: errors.append("review_sla_hours must define exactly low, standard, high, and critical.")
    else:
        for severity,hours in sla.items():
            if not positive_integer(hours) or hours>720: errors.append(f"review_sla_hours.{severity} must be a positive integer no greater than 720.")
    retention=data.get("evidence_retention_days")
    if not positive_integer(retention) or retention>365: errors.append("evidence_retention_days must be a positive integer no greater than 365.")
    appeal=data.get("appeal_window_days")
    if not positive_integer(appeal) or appeal>365: errors.append("appeal_window_days must be a positive integer no greater than 365.")
    second=data.get("require_second_review_for")
    if not isinstance(second,list): errors.append("require_second_review_for must be an array.")
    else:
        strings=[x for x in second if isinstance(x,str)]
        if len(strings)!=len(second) or len(strings)!=len(set(strings)): errors.append("require_second_review_for must contain unique severity strings only.")
        if any(x not in {"high","critical"} for x in strings): errors.append("Second review may only be required for high or critical cases.")
    if data.get("automated_enforcement") is not False: errors.append("automated_enforcement must be false; V32 requires human decisions.")
    return errors

def validate_case(data:Any,policy:Any|None=None)->list[str]:
    errors=[]
    if not isinstance(data,dict): return ["Moderation case must be a JSON object."]
    extra=set(data)-CASE_REQUIRED-CASE_OPTIONAL; missing=CASE_REQUIRED-set(data)
    if extra: errors.append("Moderation case contains unsupported fields; do not add player identifiers, usernames, raw text, or arbitrary notes.")
    if missing: errors.append("Moderation case is missing required fields: "+", ".join(sorted(missing))+".")
    if data.get("schema_version")!=1: errors.append("schema_version must equal 1.")
    ref=data.get("case_ref")
    if not isinstance(ref,str) or not CASE_REF.fullmatch(ref): errors.append("case_ref must be an opaque case- followed by 12 lowercase letters or digits.")
    if parse_timestamp(data.get("created_at")) is None: errors.append("created_at must be an ISO-8601 timestamp with a timezone.")
    if not allowed(data.get("source"),SOURCES): errors.append("source is not a supported source code.")
    if not allowed(data.get("category"),CATEGORIES): errors.append("category is not a supported category code.")
    if not allowed(data.get("channel"),CHANNELS): errors.append("channel is not a supported channel code.")
    if not allowed(data.get("severity"),SEVERITIES): errors.append("severity must be low, standard, high, or critical.")
    if not allowed(data.get("status"),STATUSES): errors.append("status is not a supported review state.")
    if not allowed(data.get("summary_code"),SUMMARY_CODES): errors.append("summary_code must be a predefined code; free-text summaries are not accepted.")
    evidence=data.get("evidence_refs")
    if not isinstance(evidence,list) or len(evidence)>8: errors.append("evidence_refs must be an array of at most eight opaque evidence references.")
    else:
        strings=[x for x in evidence if isinstance(x,str)]
        if len(strings)!=len(evidence) or len(strings)!=len(set(strings)): errors.append("evidence_refs must contain unique opaque references only.")
        if any(not EVIDENCE_REF.fullmatch(x) for x in strings): errors.append("evidence_refs may contain only opaque ev- references; paths, URLs, and content are prohibited.")
    reviewed_raw=data.get("reviewed_at"); reviewer=data.get("reviewer_role"); decision=data.get("decision_code")
    status=data.get("status"); appeal_outcome=data.get("appeal_outcome"); appeal_ref=data.get("appeal_ref"); second_role=data.get("second_reviewer_role")
    final_states={"resolved","closed","appeal_pending","appeal_resolved"}; valid_status=allowed(status,STATUSES)
    if reviewed_raw is not None and parse_timestamp(reviewed_raw) is None: errors.append("reviewed_at must be an ISO-8601 timestamp with a timezone.")
    created=parse_timestamp(data.get("created_at")); reviewed=parse_timestamp(reviewed_raw)
    if created is not None and reviewed is not None and reviewed<created: errors.append("reviewed_at cannot be earlier than created_at.")
    if reviewer is not None and not allowed(reviewer,ROLES): errors.append("reviewer_role must be moderator, senior_moderator, or safety_lead.")
    if decision is not None and not allowed(decision,DECISIONS): errors.append("decision_code is not a supported decision code.")
    if valid_status and status in final_states:
        if reviewed is None: errors.append("A resolved, closed, or appeal case requires reviewed_at.")
        if not allowed(reviewer,ROLES): errors.append("A resolved, closed, or appeal case requires a reviewer_role.")
        if not allowed(decision,DECISIONS): errors.append("A resolved, closed, or appeal case requires a decision_code.")
    elif any(x is not None for x in (decision,reviewed_raw,reviewer,appeal_ref,appeal_outcome,second_role)):
        errors.append("Review/decision fields may only be present after a case has reached a review or resolution state.")
    if valid_status and status in {"appeal_pending","appeal_resolved"}:
        if not isinstance(appeal_ref,str) or not APPEAL_REF.fullmatch(appeal_ref): errors.append("Appeal states require an opaque appeal- reference.")
        if status=="appeal_pending" and appeal_outcome!="pending": errors.append("appeal_pending cases must set appeal_outcome to pending.")
        if status=="appeal_resolved" and not allowed(appeal_outcome,{"upheld","modified","overturned"}): errors.append("appeal_resolved cases require an upheld, modified, or overturned appeal_outcome.")
    elif appeal_ref is not None or appeal_outcome is not None: errors.append("appeal_ref and appeal_outcome may only be set for appeal states.")
    if second_role is not None:
        if not allowed(second_role,{"senior_moderator","safety_lead"}): errors.append("second_reviewer_role must be senior_moderator or safety_lead.")
        if second_role==reviewer: errors.append("The second reviewer must have a different role from the primary reviewer.")
    if isinstance(policy,dict):
        req=policy.get("require_second_review_for",[])
        if isinstance(req,list) and isinstance(data.get("severity"),str) and data.get("severity") in req:
            if valid_status and status in final_states and not allowed(second_role,{"senior_moderator","safety_lead"}):
                errors.append("This severity requires a recorded second reviewer before resolution or appeal closure.")
    return errors

def validate_register(data:Any,policy:Any|None=None)->list[str]:
    if not isinstance(data,dict): return ["Moderation register must be a JSON object."]
    errors=[]
    if set(data)!={"schema_version","cases"}: errors.append("Moderation register must contain only schema_version and cases.")
    if data.get("schema_version")!=1: errors.append("Moderation register schema_version must equal 1.")
    cases=data.get("cases")
    if not isinstance(cases,list): return errors+["cases must be an array."]
    if len(cases)>MAX_REGISTER_CASES: return errors+[f"Moderation register exceeds the {MAX_REGISTER_CASES}-case input limit."]
    refs=set()
    for i,case in enumerate(cases):
        errors.extend(f"cases[{i}]: {e}" for e in validate_case(case,policy))
        if isinstance(case,dict):
            ref=case.get("case_ref")
            if isinstance(ref,str) and CASE_REF.fullmatch(ref):
                if ref in refs: errors.append(f"Duplicate case_ref: {ref}.")
                refs.add(ref)
    return errors

def iter_luau_files(root:Path,max_files:int,warnings:list[str])->list[Path]:
    result=[]; total=0
    for directory,dirnames,filenames in os.walk(root,topdown=True,followlinks=False):
        current=Path(directory); kept=[]
        for name in sorted(dirnames):
            child=current/name
            if name in SKIP_DIRS: continue
            if child.is_symlink() or not child.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root directory: {child.relative_to(root)}"); continue
            kept.append(name)
        dirnames[:]=kept
        for name in sorted(filenames):
            path=current/name
            if path.suffix.lower() not in {".lua",".luau"}: continue
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                warnings.append(f"Skipped symlinked or out-of-root source: {path.relative_to(root)}"); continue
            try: size=path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat source file: {path.relative_to(root)}"); continue
            if size>MAX_FILE_BYTES:
                warnings.append(f"Skipped oversized source file ({size} bytes): {path.relative_to(root)}"); continue
            if total+size>MAX_TOTAL_BYTES:
                warnings.append("Stopped at the 128 MiB aggregate Luau scan limit."); return result
            result.append(path); total+=size
            if len(result)>=max_files:
                warnings.append(f"Stopped at the configured {max_files}-file scan limit."); return result
    return result

def is_client_context(path:Path,root:Path)->bool:
    rel=path.relative_to(root); parts={p.lower() for p in rel.parts}; name=path.name.lower()
    return name.endswith((".client.lua",".client.luau")) or bool(parts & {"starterplayerscripts","startercharacterscripts","playerscripts"})

def audit_project(root:Path,max_files:int=MAX_FILES)->dict[str,Any]:
    findings=[]; warnings=[]; files=iter_luau_files(root,max(1,min(max_files,MAX_FILES)),warnings)
    filt=re.compile(r"\bTextService\s*:\s*FilterStringAsync\s*\(")
    legacy=re.compile(r"\bChat\s*:\s*FilterStringAsync\s*\(")
    native=re.compile(r"\bgame\s*:\s*GetService\s*\(\s*["']TextChatService["']\s*\)")
    sink=re.compile(r"\b[A-Za-z_][A-Za-z0-9_\.]*\.Text\s*=\s*(?:rawText|unfilteredText|inputText|submittedText|userText|playerText|messageText|petName|signText|customName)\b",re.I)
    filter_calls=legacy_calls=native_refs=raw_sinks=readable=0
    for path in files:
        rel=path.relative_to(root).as_posix()
        try: source=path.read_text(encoding="utf-8-sig")
        except (OSError,UnicodeError):
            warnings.append(f"Skipped unreadable Luau source: {rel}"); continue
        readable+=1; client=is_client_context(path,root)
        for match in filt.finditer(source):
            filter_calls+=1
            if client: findings.append({"severity":"high","code":"text_filter_call_in_client_context","file":rel,"line":source.count("\n",0,match.start())+1,"message":"TextService filtering must be performed by a server Script; verify this call is moved to a server-owned path."})
        for match in legacy.finditer(source):
            legacy_calls+=1
            findings.append({"severity":"high","code":"legacy_chat_filter_api","file":rel,"line":source.count("\n",0,match.start())+1,"message":"Legacy Chat:FilterStringAsync usage detected; migrate deliberately to server-side TextService filtering or native TextChatService."})
        native_refs+=len(native.findall(source))
        for match in sink.finditer(source):
            raw_sinks+=1
            findings.append({"severity":"high","code":"possible_unfiltered_text_display","file":rel,"line":source.count("\n",0,match.start())+1,"message":"A variable with a raw-input name is assigned to a Text property. Trace its origin and prove it was filtered before display; this text scan is only a review lead."})
        if len(findings)>=MAX_FINDINGS:
            warnings.append(f"Stopped recording at the {MAX_FINDINGS}-finding report limit."); break
    counts={level:sum(1 for item in findings if item["severity"]==level) for level in ("high","medium","low")}
    return {
        "report_type":"v32_player_safety_source_audit","schema_version":1,"version":VERSION,
        "project_root_name":root.name,
        "inventory":{"luau_files_discovered":len(files),"files_read":readable,"text_service_filter_calls":filter_calls,"legacy_chat_filter_calls":legacy_calls,"text_chat_service_get_service_calls":native_refs,"possible_raw_text_sinks":raw_sinks},
        "finding_counts":counts,"findings":findings[:MAX_FINDINGS],"warnings":warnings,
        "execution_status":"static_local_audit_only",
        "limitations":[
            "This bounded text-pattern scan is not a Luau parser, dataflow analysis, or proof that all text paths were found.",
            "It cannot prove TextFilterResult output is the exact value displayed to each audience.",
            "TextChatService provides platform filtering for its native chat flow; this audit does not inspect message contents.",
            "No Roblox service is contacted, no player data or raw chat is collected, and no source file is modified."
        ]
    }

def command_doctor(args:argparse.Namespace)->int:
    root=resolve_root(args.root); warnings=[]; files=iter_luau_files(root,MAX_FILES,warnings)
    print(f"Project: {root}"); print(f"Luau/Lua source files discovered: {len(files)}")
    print("Optional local tools:")
    for exe in ("git","rojo","luau-analyze"): print(f"  {exe}: {shutil.which(exe) or 'not found on PATH'}")
    print("No configured command is executed and no Roblox connection is attempted.")
    for warning in warnings: print(f"WARNING: {warning}")
    return 0

def command_validate_policy(args:argparse.Namespace)->int:
    root=resolve_root(args.root); path,policy=load_json(root,args.policy); errors=validate_policy(policy)
    if errors:
        for e in errors: print(f"FAIL: {e}")
        return 1
    print(f"PASS: moderation policy validated: {path.relative_to(root)}")
    print("Policy validation is structural; it does not certify legal compliance or authorize moderation actions.")
    return 0

def command_validate_case(args:argparse.Namespace)->int:
    root=resolve_root(args.root); _,policy=load_json(root,args.policy); _,case=load_json(root,args.case)
    policy_errors=validate_policy(policy)
    if policy_errors: raise ValueError("Invalid moderation policy: "+" ".join(policy_errors))
    errors=validate_case(case,policy)
    if errors:
        for e in errors: print(f"FAIL: {e}")
        return 1
    print(f"PASS: privacy-minimal moderation case validated: {case['case_ref']}")
    print("The case contains only opaque references and codes; keep identity/evidence details in authorized platform systems.")
    return 0

def command_validate_register(args:argparse.Namespace)->int:
    root=resolve_root(args.root); _,policy=load_json(root,args.policy); _,register=load_json(root,args.register)
    policy_errors=validate_policy(policy)
    if policy_errors: raise ValueError("Invalid moderation policy: "+" ".join(policy_errors))
    errors=validate_register(register,policy)
    if errors:
        for e in errors: print(f"FAIL: {e}")
        return 1
    print(f"PASS: validated {len(register['cases'])} privacy-minimal moderation case records.")
    print("Duplicate case references are not permitted.")
    return 0

def command_audit(args:argparse.Namespace)->int:
    root=resolve_root(args.root); report=audit_project(root,args.max_files)
    output=safe_output_path(root,args.output); atomic_write_json(output,report)
    print(f"Read-only player-safety audit written to: {output}")
    print(f"Files: {report['inventory']['files_read']}; TextService filters: {report['inventory']['text_service_filter_calls']}; possible raw sinks: {report['inventory']['possible_raw_text_sinks']}; findings: {sum(report['finding_counts'].values())}")
    print("Static audit only; inspect call sites manually and verify actual filtered display behavior in an authorized test experience.")
    return 0

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest="command",required=True)
    doctor=sub.add_parser("doctor",help="Inspect local Luau source inventory and optional tools."); doctor.add_argument("--root",required=True); doctor.set_defaults(func=command_doctor)
    policy=sub.add_parser("validate-policy",help="Validate a human-reviewed moderation policy."); policy.add_argument("--root",required=True); policy.add_argument("--policy",default=DEFAULT_POLICY); policy.set_defaults(func=command_validate_policy)
    case=sub.add_parser("validate-case",help="Validate one privacy-minimal moderation case."); case.add_argument("--root",required=True); case.add_argument("--policy",default=DEFAULT_POLICY); case.add_argument("--case",default=DEFAULT_CASE); case.set_defaults(func=command_validate_case)
    register=sub.add_parser("validate-register",help="Validate a batch of moderation case records."); register.add_argument("--root",required=True); register.add_argument("--policy",default=DEFAULT_POLICY); register.add_argument("--register",default=DEFAULT_REGISTER); register.set_defaults(func=command_validate_register)
    audit=sub.add_parser("audit",help="Create a bounded read-only user-text safety audit."); audit.add_argument("--root",required=True); audit.add_argument("--output",default=DEFAULT_AUDIT); audit.add_argument("--max-files",type=int,default=MAX_FILES); audit.set_defaults(func=command_audit)
    args=parser.parse_args()
    try: return args.func(args)
    except (OSError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
