#!/usr/bin/env python3
"""Offline V38 incident-response record validator and readiness auditor."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "38.0.0"
MAX_BYTES = 1024 * 1024
MAX_EVENTS = 100
MAX_ACTIONS = 50
REFS = {
    "signal": re.compile(r"^sig-[a-z0-9]{8,24}$"),
    "evidence": re.compile(r"^ev-[a-z0-9]{12}$"),
    "approval": re.compile(r"^apr-[a-z0-9]{8,24}$"),
    "message": re.compile(r"^msg-[a-z0-9]{8,24}$"),
    "postmortem": re.compile(r"^pm-[a-z0-9]{8,24}$"),
    "followup": re.compile(r"^issue-[a-z0-9]{8,24}$"),
}
ID = re.compile(r"^inc-[a-z0-9]{8,24}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
TOP = {"schema_version","incident_id","project_key","opened_at","detected_at","severity","status","summary","impact","detection","roles","timeline","actions","communications","resolution"}
FIELDS = {
 "impact":{"services","audience_scope","impact_summary","privacy_reviewed"},
 "detection":{"source","signal_refs","privacy_safe"},
 "role":{"role","acknowledged"},
 "event":{"event_id","occurred_at","event_type","summary","evidence_refs"},
 "action":{"action_id","category","description","risk","status","requires_approval","approval_ref","approved_at","created_at","verification_status","verification_ref"},
 "communications":{"player_notice_required","player_notice_reviewed","privacy_safe","player_notice_ref"},
 "resolution":{"resolved_at","verification_ref","postmortem_ref","follow_up_ref","customer_impact_closed"},
}
SERVICES = {"data_store","economy","matchmaking","networking","gameplay","content_delivery","publishing","analytics","moderation","unknown"}
SEVERITIES = {"critical","high","moderate","low"}
STATUSES = {"investigating","mitigating","monitoring","resolved"}
ROLES = {"incident_commander","technical_lead","data_owner","communications_lead"}
EVENT_TYPES = {"detected","triaged","investigation","mitigation","verification","communication","resolved"}
CATEGORIES = {"observe","mitigate","rollback","restore","communicate"}
RISKS = {"low","medium","high"}
ACTION_STATUSES = {"proposed","approved","applied","rejected","reverted"}
VERIFY = {"not_run","pass","fail"}

def enum(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices

def is_time(value: Any) -> bool:
    if not isinstance(value,str) or len(value)>40: return False
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except (ValueError,OverflowError): return False

def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z","+00:00"))

def fields(value: dict, expected: set[str], label: str) -> list[str]:
    missing=sorted(expected-value.keys()); extra=sorted(value.keys()-expected)
    out=[]
    if missing: out.append(f"{label} missing: {', '.join(missing)}.")
    if extra: out.append(f"{label} has unsupported fields: {', '.join(extra)}.")
    return out

def text_value(value: Any, label: str, maximum: int, minimum: int=1) -> list[str]:
    if not isinstance(value,str) or len(value.strip())<minimum or len(value)>maximum:
        return [f"{label} must be {minimum}-{maximum} non-empty characters."]
    return []

def refs(value: Any, key: str, label: str, minimum: int=0, maximum: int=30) -> list[str]:
    if not isinstance(value,list) or not minimum<=len(value)<=maximum:
        return [f"{label} must contain {minimum}-{maximum} references."]
    out=[]; seen=set()
    for i,item in enumerate(value):
        if not isinstance(item,str) or not REFS[key].fullmatch(item): out.append(f"{label}[{i}] has an invalid opaque reference.")
        elif item in seen: out.append(f"{label} contains duplicate reference {item}.")
        else: seen.add(item)
    return out

def validate_incident(data: Any) -> list[str]:
    out=[]
    if not isinstance(data,dict): return ["Incident record must be a JSON object."]
    out += fields(data,TOP,"incident")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"),bool): out.append("schema_version must be integer 1.")
    if not isinstance(data.get("incident_id"),str) or not ID.fullmatch(data["incident_id"]): out.append("incident_id must be inc- plus 8-24 lowercase letters/digits.")
    if not isinstance(data.get("project_key"),str) or not SLUG.fullmatch(data["project_key"]): out.append("project_key must be a lowercase project slug.")
    for key in ("opened_at","detected_at"):
        if not is_time(data.get(key)): out.append(f"{key} must be ISO-8601 with timezone.")
    if all(is_time(data.get(k)) for k in ("opened_at","detected_at")) and dt(data["detected_at"])<dt(data["opened_at"]): out.append("detected_at cannot precede opened_at.")
    if not enum(data.get("severity"), SEVERITIES): out.append("severity is unsupported.")
    if not enum(data.get("status"), STATUSES): out.append("status is unsupported.")
    out += text_value(data.get("summary"),"summary",500,10)

    impact=data.get("impact")
    if not isinstance(impact,dict): out.append("impact must be an object.")
    else:
        out += fields(impact,FIELDS["impact"],"impact")
        services=impact.get("services")
        if not isinstance(services,list) or not 1<=len(services)<=10 or any(x not in SERVICES for x in services if isinstance(x,str)) or any(not isinstance(x,str) for x in services): out.append("impact.services must contain 1-10 supported service categories.")
        elif len(set(services))!=len(services): out.append("impact.services contains duplicates.")
        if not enum(impact.get("audience_scope"), {"all_players","aggregate_subset","unknown"}): out.append("impact.audience_scope is unsupported.")
        out += text_value(impact.get("impact_summary"),"impact.impact_summary",800,10)
        if impact.get("privacy_reviewed") is not True: out.append("impact.privacy_reviewed must be true.")
    detection=data.get("detection")
    if not isinstance(detection,dict): out.append("detection must be an object.")
    else:
        out += fields(detection,FIELDS["detection"],"detection")
        if not enum(detection.get("source"), {"aggregate_telemetry","aggregated_player_reports","developer_observation","platform_status","other"}): out.append("detection.source is unsupported.")
        out += refs(detection.get("signal_refs"),"signal","detection.signal_refs",1,20)
        if detection.get("privacy_safe") is not True: out.append("detection.privacy_safe must be true.")

    roles=data.get("roles"); role_set=set()
    if not isinstance(roles,list) or not 1<=len(roles)<=4: out.append("roles must contain 1-4 role assignments.")
    else:
        for i,item in enumerate(roles):
            label=f"roles[{i}]"
            if not isinstance(item,dict): out.append(f"{label} must be an object."); continue
            out += fields(item,FIELDS["role"],label)
            role=item.get("role")
            if not enum(role, ROLES): out.append(f"{label}.role is unsupported.")
            elif role in role_set: out.append(f"duplicate role assignment: {role}.")
            else: role_set.add(role)
            if not isinstance(item.get("acknowledged"),bool): out.append(f"{label}.acknowledged must be boolean.")
        if "incident_commander" not in role_set: out.append("roles must include an incident_commander.")
        if enum(data.get("severity"), {"critical","high"}) and "technical_lead" not in role_set: out.append("critical/high incidents require a technical_lead.")

    timeline=data.get("timeline"); event_ids=set(); times=[]; types=[]
    if not isinstance(timeline,list) or not 1<=len(timeline)<=MAX_EVENTS: out.append(f"timeline must contain 1-{MAX_EVENTS} events.")
    else:
        for i,item in enumerate(timeline):
            label=f"timeline[{i}]"
            if not isinstance(item,dict): out.append(f"{label} must be an object."); continue
            out += fields(item,FIELDS["event"],label)
            event_id=item.get("event_id")
            if not isinstance(event_id,str) or not re.fullmatch(r"evt-[a-z0-9]{8,24}",event_id): out.append(f"{label}.event_id is invalid.")
            elif event_id in event_ids: out.append(f"duplicate event_id: {event_id}.")
            else: event_ids.add(event_id)
            moment=item.get("occurred_at")
            if not is_time(moment): out.append(f"{label}.occurred_at needs a timezone-aware timestamp.")
            else:
                current=dt(moment); times.append(current)
                if len(times)>1 and current<times[-2]: out.append("timeline events must be chronological.")
            if not enum(item.get("event_type"), EVENT_TYPES): out.append(f"{label}.event_type is unsupported.")
            else: types.append(item["event_type"])
            out += text_value(item.get("summary"),f"{label}.summary",500,5)
            out += refs(item.get("evidence_refs"),"evidence",f"{label}.evidence_refs",0,10)
        if isinstance(timeline[0],dict) and timeline[0].get("event_type")!="detected": out.append("the first timeline event must be detected.")
        if is_time(data.get("detected_at")) and times and times[0]<dt(data["detected_at"]): out.append("the first timeline event cannot precede detected_at.")

    actions=data.get("actions"); action_ids=set()
    if not isinstance(actions,list) or len(actions)>MAX_ACTIONS: out.append(f"actions must be a list of at most {MAX_ACTIONS} items.")
    else:
        for i,item in enumerate(actions):
            label=f"actions[{i}]"
            if not isinstance(item,dict): out.append(f"{label} must be an object."); continue
            out += fields(item,FIELDS["action"],label)
            aid=item.get("action_id")
            if not isinstance(aid,str) or not re.fullmatch(r"act-[a-z0-9]{8,24}",aid): out.append(f"{label}.action_id is invalid.")
            elif aid in action_ids: out.append(f"duplicate action_id: {aid}.")
            else: action_ids.add(aid)
            if not enum(item.get("category"), CATEGORIES): out.append(f"{label}.category is unsupported.")
            out += text_value(item.get("description"),f"{label}.description",500,5)
            risk=item.get("risk"); status=item.get("status")
            if not enum(risk, RISKS): out.append(f"{label}.risk is unsupported.")
            if not enum(status, ACTION_STATUSES): out.append(f"{label}.status is unsupported.")
            required=item.get("requires_approval")
            if not isinstance(required,bool): out.append(f"{label}.requires_approval must be boolean.")
            elif (risk=="high" or enum(item.get("category"), {"rollback","restore"})) and required is not True: out.append(f"{label} high-risk/recovery action requires human approval.")
            approval=item.get("approval_ref"); approved_at=item.get("approved_at")
            if required is True and status in {"approved","applied","reverted"}:
                if not isinstance(approval,str) or not REFS["approval"].fullmatch(approval): out.append(f"{label} requires a valid approval_ref.")
                if not is_time(approved_at): out.append(f"{label} requires approved_at timestamp.")
            elif approval is not None and (not isinstance(approval,str) or not REFS["approval"].fullmatch(approval)): out.append(f"{label}.approval_ref must be null or valid.")
            elif approved_at is not None and not is_time(approved_at): out.append(f"{label}.approved_at must be null or timezone-aware.")
            created=item.get("created_at")
            if not is_time(created): out.append(f"{label}.created_at needs a timezone-aware timestamp.")
            elif is_time(approved_at) and dt(approved_at)<dt(created): out.append(f"{label}.approved_at cannot precede created_at.")
            verification=item.get("verification_status"); vref=item.get("verification_ref")
            if not enum(verification, VERIFY): out.append(f"{label}.verification_status is unsupported.")
            if status in {"applied","reverted"}:
                if verification!="pass": out.append(f"{label} must pass verification before applied/reverted status.")
                if not isinstance(vref,str) or not REFS["evidence"].fullmatch(vref): out.append(f"{label} needs a verification_ref.")
            elif vref is not None and (not isinstance(vref,str) or not REFS["evidence"].fullmatch(vref)): out.append(f"{label}.verification_ref must be null or valid.")

    comm=data.get("communications")
    if not isinstance(comm,dict): out.append("communications must be an object.")
    else:
        out += fields(comm,FIELDS["communications"],"communications")
        for key in ("player_notice_required","player_notice_reviewed","privacy_safe"):
            if not isinstance(comm.get(key),bool): out.append(f"communications.{key} must be boolean.")
        if comm.get("privacy_safe") is not True: out.append("communications.privacy_safe must be true.")
        mref=comm.get("player_notice_ref")
        if comm.get("player_notice_reviewed") is True and (not isinstance(mref,str) or not REFS["message"].fullmatch(mref)): out.append("reviewed player notices need a valid player_notice_ref.")
        if mref is not None and (not isinstance(mref,str) or not REFS["message"].fullmatch(mref)): out.append("communications.player_notice_ref must be null or valid.")
        if comm.get("player_notice_required") is False and (comm.get("player_notice_reviewed") is True or mref is not None): out.append("notice review/reference must be empty when no notice is required.")

    resolution=data.get("resolution")
    if not isinstance(resolution,dict): out.append("resolution must be an object.")
    else:
        out += fields(resolution,FIELDS["resolution"],"resolution")
        resolved=data.get("status")=="resolved"
        r_at=resolution.get("resolved_at"); vref=resolution.get("verification_ref")
        pm=resolution.get("postmortem_ref"); follow=resolution.get("follow_up_ref")
        if resolved:
            if not is_time(r_at): out.append("resolved incidents need resolution.resolved_at.")
            if not isinstance(vref,str) or not REFS["evidence"].fullmatch(vref): out.append("resolved incidents need resolution.verification_ref.")
            if resolution.get("customer_impact_closed") is not True: out.append("resolved incidents must set customer_impact_closed=true.")
            if "resolved" not in types or (types and types[-1]!="resolved"): out.append("resolved incidents need a final resolved timeline event.")
            if is_time(r_at) and times and dt(r_at)<times[-1]: out.append("resolved_at cannot precede the final timeline event.")
            if enum(data.get("severity"), {"critical","high"}):
                if not isinstance(pm,str) or not REFS["postmortem"].fullmatch(pm): out.append("critical/high incidents require a postmortem_ref.")
                if not isinstance(follow,str) or not REFS["followup"].fullmatch(follow): out.append("critical/high incidents require follow_up_ref.")
            if comm_is_required(comm) and (not isinstance(comm,dict) or comm.get("player_notice_reviewed") is not True): out.append("required player notice must be reviewed before closure.")
        else:
            if r_at is not None or vref is not None or resolution.get("customer_impact_closed") is not False: out.append("unresolved incidents must keep closure fields empty and customer_impact_closed=false.")
            if pm is not None and (not isinstance(pm,str) or not REFS["postmortem"].fullmatch(pm)): out.append("postmortem_ref must be null or valid.")
            if follow is not None and (not isinstance(follow,str) or not REFS["followup"].fullmatch(follow)): out.append("follow_up_ref must be null or valid.")
            if "resolved" in types: out.append("unresolved incidents cannot include a resolved event.")
    return sorted(set(out))

def comm_is_required(comm: Any) -> bool:
    return isinstance(comm,dict) and comm.get("player_notice_required") is True

def audit_incident(data: dict) -> dict:
    roles=data.get("roles",[]); actions=data.get("actions",[]); comm=data.get("communications",{})
    unack=sorted(x.get("role","unknown") for x in roles if isinstance(x,dict) and x.get("acknowledged") is not True)
    pending=sorted(x.get("action_id","unknown") for x in actions if isinstance(x,dict) and x.get("requires_approval") is True and x.get("status")=="proposed")
    warnings=[]; steps=[]
    if unack: warnings.append("One or more response roles have not acknowledged the incident."); steps.append("Confirm ownership and acknowledgement for every response role.")
    if pending: warnings.append("One or more proposed actions are awaiting human approval."); steps.append("Review blast radius, recovery point, and approval record before a recovery operation.")
    if comm.get("player_notice_required") is True and comm.get("player_notice_reviewed") is not True: warnings.append("A required player notice is awaiting review."); steps.append("Have the communications lead review a concise, privacy-safe notice.")
    if data["status"]=="resolved": steps.append("Preserve evidence and schedule the post-incident review.")
    else: steps.append("Continue monitoring aggregate service health and record timestamped verification evidence.")
    if data["severity"] in {"critical","high"}: steps.insert(0,"Keep an incident commander and technical lead assigned until impact is contained.")
    return {"schema_version":1,"incident_id":data["incident_id"],"status":"resolved" if data["status"]=="resolved" else "human_action_required","severity":data["severity"],"summary":{"timeline_event_count":len(data["timeline"]),"action_count":len(actions),"pending_approval_count":len(pending),"unacknowledged_role_count":len(unack),"player_notice_required":comm.get("player_notice_required",False)},"warnings":warnings,"recommended_next_steps":steps,"limitations":["Offline metadata audit only; no live Roblox telemetry, service calls, alerting, mitigation, rollback, restore, or messaging.","Opaque references are not authenticated or inspected.","Privacy attestations are human assertions, not PII scans; never store player-level personal information."]}

def resolve_root(raw: str) -> Path:
    root=Path(raw).expanduser().resolve(strict=True)
    if not root.is_dir(): raise ValueError("Project root must be an existing directory.")
    return root

def safe_path(root: Path, raw: str, must_exist: bool=False) -> Path:
    if not isinstance(raw,str) or not raw.strip() or len(raw)>240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw)>=3 and raw[1:3]==":/"): raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts=raw.split("/")
    if any(p in {"",".",".."} for p in parts): raise ValueError("Empty, dot, and parent path segments are not allowed.")
    probe=root
    for part in parts:
        probe=probe/part
        if probe.is_symlink(): raise ValueError("Symlink traversal is not allowed.")
    path=root.joinpath(*parts).resolve(strict=must_exist)
    try: path.relative_to(root.resolve(strict=True))
    except ValueError as exc: raise ValueError("Path resolves outside the project root.") from exc
    if must_exist and not path.is_file(): raise ValueError("Input must be an existing regular file.")
    return path

def duplicate_keys(pairs: list[tuple[str,Any]]) -> dict:
    result={}
    for key,value in pairs:
        if key in result: raise ValueError(f"Duplicate JSON key: {key}")
        result[key]=value
    return result

def load_json(root: Path, raw: str) -> Any:
    path=safe_path(root,raw,True)
    if path.stat().st_size>MAX_BYTES: raise ValueError("Incident JSON exceeds the 1 MiB limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"),object_pairs_hook=duplicate_keys,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid JSON constant: {x}")))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"Could not read valid JSON: {exc}") from exc

def write_json(root: Path, raw: str, value: dict) -> None:
    path=safe_path(root,raw); path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()): raise ValueError("Output must be a regular file.")
    fd,tmp=tempfile.mkstemp(prefix=".v38-",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        Path(tmp).replace(path)
    finally:
        try: Path(tmp).unlink()
        except FileNotFoundError: pass

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("doctor"); p.add_argument("--root",required=True)
    p=sub.add_parser("validate"); p.add_argument("--root",required=True); p.add_argument("--incident",required=True)
    p=sub.add_parser("audit"); p.add_argument("--root",required=True); p.add_argument("--incident",required=True); p.add_argument("--output",required=True)
    args=parser.parse_args()
    try:
        root=resolve_root(args.root)
        if args.command=="doctor": print(f"V{VERSION} ready | project={root}"); return 0
        data=load_json(root,args.incident); issues=validate_incident(data)
        if issues:
            for issue in issues: print("FAIL: "+issue)
            return 1
        if args.command=="validate": print("PASS: incident metadata and recovery gates are valid."); return 0
        result=audit_incident(data); write_json(root,args.output,result)
        print(f"PASS: incident audit written; status={result['status']}; warnings={len(result['warnings'])}."); return 0
    except (OSError,ValueError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
