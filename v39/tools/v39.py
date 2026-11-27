#!/usr/bin/env python3
"""Offline deterministic simulator for synthetic Roblox gameplay economies."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION="39.0.0"
MAX_BYTES=1024*1024
MAX_HORIZON=365
MAX_CURRENCIES=8
MAX_COHORTS=6
MAX_COMPONENTS=20
TOP={"schema_version","model_id","horizon_days","currencies","progression","cohorts"}
CURRENCY_FIELDS={"currency_id","kind","starting_balance","healthy_balance_ceiling","sources","sinks"}
COMPONENT_FIELDS={"component_id","amount_per_active_day"}
PROGRESSION_FIELDS={"xp_per_active_day","level_gap_warning","levels"}
LEVEL_FIELDS={"level","xp_required","rewards"}
REWARD_FIELDS={"currency_id","amount"}
COHORT_FIELDS={"cohort_id","active_days_per_week","activity_multiplier_bps"}
KINDS={"soft","event_token"}
SLUG=re.compile(r"^[a-z][a-z0-9_-]{1,39}$")

def is_int(value:Any,minimum:int,maximum:int)->bool:
    return isinstance(value,int) and not isinstance(value,bool) and minimum<=value<=maximum

def is_slug(value:Any)->bool:
    return isinstance(value,str) and bool(SLUG.fullmatch(value))

def check_fields(value:dict,expected:set[str],label:str)->list[str]:
    missing=sorted(expected-value.keys())
    extra=sorted(value.keys()-expected)
    result=[]
    if missing: result.append(f"{label} missing: {', '.join(missing)}.")
    if extra: result.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return result

def validate_model(data:Any)->list[str]:
    errors=[]
    if not isinstance(data,dict): return ["Model must be a JSON object."]
    errors+=check_fields(data,TOP,"model")
    if data.get("schema_version")!=1 or isinstance(data.get("schema_version"),bool): errors.append("schema_version must be integer 1.")
    if not is_slug(data.get("model_id")): errors.append("model_id must be a lowercase slug (2-40 characters).")
    if not is_int(data.get("horizon_days"),1,MAX_HORIZON): errors.append(f"horizon_days must be an integer from 1 to {MAX_HORIZON}.")
    currencies=data.get("currencies")
    currency_ids=set()
    if not isinstance(currencies,list) or not 1<=len(currencies)<=MAX_CURRENCIES:
        errors.append(f"currencies must contain 1-{MAX_CURRENCIES} items.")
        currencies=[]
    for i,item in enumerate(currencies):
        label=f"currencies[{i}]"
        if not isinstance(item,dict): errors.append(f"{label} must be an object."); continue
        errors+=check_fields(item,CURRENCY_FIELDS,label)
        cid=item.get("currency_id")
        if not is_slug(cid): errors.append(f"{label}.currency_id must be a valid lowercase slug.")
        elif cid in currency_ids: errors.append(f"Duplicate currency_id: {cid}.")
        else: currency_ids.add(cid)
        if item.get("kind") not in KINDS: errors.append(f"{label}.kind must be soft or event_token.")
        if not is_int(item.get("starting_balance"),0,1_000_000_000): errors.append(f"{label}.starting_balance must be an integer from 0 to 1,000,000,000.")
        if not is_int(item.get("healthy_balance_ceiling"),1,1_000_000_000): errors.append(f"{label}.healthy_balance_ceiling must be an integer from 1 to 1,000,000,000.")
        for group in ("sources","sinks"):
            entries=item.get(group)
            if not isinstance(entries,list) or len(entries)>MAX_COMPONENTS:
                errors.append(f"{label}.{group} must be a list of at most {MAX_COMPONENTS} items."); continue
            seen=set()
            for j,entry in enumerate(entries):
                elabel=f"{label}.{group}[{j}]"
                if not isinstance(entry,dict): errors.append(f"{elabel} must be an object."); continue
                errors+=check_fields(entry,COMPONENT_FIELDS,elabel)
                eid=entry.get("component_id")
                if not is_slug(eid): errors.append(f"{elabel}.component_id must be a valid lowercase slug.")
                elif eid in seen: errors.append(f"{elabel} duplicates component_id {eid}.")
                else: seen.add(eid)
                if not is_int(entry.get("amount_per_active_day"),0,100_000_000): errors.append(f"{elabel}.amount_per_active_day must be an integer from 0 to 100,000,000.")

    progression=data.get("progression")
    if not isinstance(progression,dict):
        errors.append("progression must be an object.")
        progression={}
    else:
        errors+=check_fields(progression,PROGRESSION_FIELDS,"progression")
        if not is_int(progression.get("xp_per_active_day"),1,1_000_000): errors.append("progression.xp_per_active_day must be an integer from 1 to 1,000,000.")
        if not is_int(progression.get("level_gap_warning"),1,20): errors.append("progression.level_gap_warning must be an integer from 1 to 20.")
        levels=progression.get("levels")
        if not isinstance(levels,list) or len(levels)>50: errors.append("progression.levels must be a list of at most 50 levels."); levels=[]
        previous_xp=0
        for i,item in enumerate(levels):
            label=f"progression.levels[{i}]"
            if not isinstance(item,dict): errors.append(f"{label} must be an object."); continue
            errors+=check_fields(item,LEVEL_FIELDS,label)
            if not is_int(item.get("level"),2,51) or item.get("level")!=i+2: errors.append(f"{label}.level must be sequential, beginning at 2.")
            xp=item.get("xp_required")
            if not is_int(xp,1,100_000_000): errors.append(f"{label}.xp_required must be a positive integer.")
            elif xp<=previous_xp: errors.append(f"{label}.xp_required thresholds must increase strictly.")
            else: previous_xp=xp
            rewards=item.get("rewards")
            if not isinstance(rewards,list) or len(rewards)>MAX_CURRENCIES: errors.append(f"{label}.rewards must be a list of at most {MAX_CURRENCIES} items."); continue
            reward_ids=set()
            for j,reward in enumerate(rewards):
                rlabel=f"{label}.rewards[{j}]"
                if not isinstance(reward,dict): errors.append(f"{rlabel} must be an object."); continue
                errors+=check_fields(reward,REWARD_FIELDS,rlabel)
                rid=reward.get("currency_id")
                if not is_slug(rid): errors.append(f"{rlabel}.currency_id must be a valid slug.")
                elif rid not in currency_ids: errors.append(f"{rlabel} references unknown currency {rid}.")
                elif rid in reward_ids: errors.append(f"{rlabel} duplicates currency reward {rid}.")
                else: reward_ids.add(rid)
                if not is_int(reward.get("amount"),0,100_000_000): errors.append(f"{rlabel}.amount must be an integer from 0 to 100,000,000.")

    cohorts=data.get("cohorts")
    cohort_ids=set()
    if not isinstance(cohorts,list) or not 2<=len(cohorts)<=MAX_COHORTS:
        errors.append(f"cohorts must contain 2-{MAX_COHORTS} synthetic archetypes.")
        cohorts=[]
    for i,item in enumerate(cohorts):
        label=f"cohorts[{i}]"
        if not isinstance(item,dict): errors.append(f"{label} must be an object."); continue
        errors+=check_fields(item,COHORT_FIELDS,label)
        cid=item.get("cohort_id")
        if not is_slug(cid): errors.append(f"{label}.cohort_id must be a valid slug.")
        elif cid in cohort_ids: errors.append(f"Duplicate cohort_id: {cid}.")
        else: cohort_ids.add(cid)
        if not is_int(item.get("active_days_per_week"),1,7): errors.append(f"{label}.active_days_per_week must be an integer from 1 to 7.")
        if not is_int(item.get("activity_multiplier_bps"),1000,20000): errors.append(f"{label}.activity_multiplier_bps must be an integer from 1000 to 20000.")
    return sorted(set(errors))

def simulate_model(model:dict)->dict:
    currencies=model["currencies"]
    currency_by_id={x["currency_id"]:x for x in currencies}
    progression=model["progression"]
    results=[]
    warnings=[]
    for cohort in model["cohorts"]:
        multiplier=cohort["activity_multiplier_bps"]
        active_days=0
        xp=0
        level=1
        next_level_index=0
        balances={x["currency_id"]:x["starting_balance"] for x in currencies}
        earned={x["currency_id"]:0 for x in currencies}
        paid={x["currency_id"]:0 for x in currencies}
        shortfall={x["currency_id"]:0 for x in currencies}
        rewards_total={x["currency_id"]:0 for x in currencies}
        for day in range(model["horizon_days"]):
            if day%7>=cohort["active_days_per_week"]: continue
            active_days+=1
            for currency in currencies:
                cid=currency["currency_id"]
                for source in currency["sources"]:
                    amount=source["amount_per_active_day"]*multiplier//10000
                    balances[cid]+=amount
                    earned[cid]+=amount
                for sink in currency["sinks"]:
                    requested=sink["amount_per_active_day"]*multiplier//10000
                    spent=min(balances[cid],requested)
                    balances[cid]-=spent
                    paid[cid]+=spent
                    shortfall[cid]+=requested-spent
            xp+=progression["xp_per_active_day"]*multiplier//10000
            while next_level_index<len(progression["levels"]) and xp>=progression["levels"][next_level_index]["xp_required"]:
                level=progression["levels"][next_level_index]["level"]
                for reward in progression["levels"][next_level_index]["rewards"]:
                    cid=reward["currency_id"]
                    balances[cid]+=reward["amount"]
                    rewards_total[cid]+=reward["amount"]
                next_level_index+=1
        currency_results=[]
        for currency in currencies:
            cid=currency["currency_id"]
            closing=balances[cid]
            cap=currency["healthy_balance_ceiling"]
            if closing>cap:
                warnings.append(f"{cohort['cohort_id']}: {cid} closing balance {closing} exceeds review ceiling {cap}.")
            if shortfall[cid]>0:
                warnings.append(f"{cohort['cohort_id']}: {cid} modeled sinks have an unpaid shortfall of {shortfall[cid]}.")
            if currency["sources"] and not currency["sinks"]:
                warnings.append(f"{cid} has modeled sources but no sinks; review potential accumulation.")
            currency_results.append({
                "currency_id":cid,"opening_balance":currency["starting_balance"],
                "source_earned":earned[cid],"progression_rewards":rewards_total[cid],
                "sink_paid":paid[cid],"sink_shortfall":shortfall[cid],"closing_balance":closing,
                "healthy_balance_ceiling":cap,"above_healthy_ceiling":closing>cap
            })
        results.append({
            "cohort_id":cohort["cohort_id"],"active_days":active_days,
            "activity_multiplier_bps":multiplier,"total_xp":xp,"final_level":level,
            "currencies":currency_results
        })
    levels=[x["final_level"] for x in results]
    gap=max(levels)-min(levels) if levels else 0
    if gap>=progression["level_gap_warning"]:
        warnings.append(f"Synthetic cohort progression gap is {gap} levels, meeting or exceeding the review threshold {progression['level_gap_warning']}.")
    return {
        "schema_version":1,"model_id":model["model_id"],"horizon_days":model["horizon_days"],
        "simulation":"deterministic_integer_model","status":"review_required" if warnings else "no_structural_warnings",
        "summary":{"cohort_count":len(results),"currency_count":len(currencies),"warning_count":len(warnings),"progression_level_gap":gap},
        "cohorts":results,"warnings":sorted(set(warnings)),
        "limitations":[
            "Synthetic assumptions only; this report is not observed player behavior or proof of live economy balance.",
            "No Roblox telemetry, player records, purchases, retention, revenue, or Studio execution is accessed.",
            "No random reward, paid random outcome, wagering, or gambling mechanics are modeled."
        ]
    }

def duplicate_keys(pairs:list[tuple[str,Any]])->dict:
    output={}
    for key,value in pairs:
        if key in output: raise ValueError(f"Duplicate JSON key: {key}")
        output[key]=value
    return output

def reject_constant(value:str)->None:
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")

def resolve_root(raw:str)->Path:
    root=Path(raw).expanduser().resolve(strict=True)
    if not root.is_dir(): raise ValueError("Project root must be an existing directory.")
    return root

def safe_path(root:Path,raw:str,must_exist:bool=False)->Path:
    if not isinstance(raw,str) or not raw or len(raw)>240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw)>1 and raw[1:2]==":"):
        raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts=raw.split("/")
    if any(part in {"",".",".."} for part in parts): raise ValueError("Empty, dot, and parent path segments are forbidden.")
    probe=root
    for part in parts:
        probe=probe/part
        if probe.is_symlink(): raise ValueError("Symlink traversal is not allowed.")
    resolved=probe.resolve(strict=must_exist)
    try: resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc: raise ValueError("Path escapes the project root.") from exc
    if must_exist and not resolved.is_file(): raise ValueError("Input must be an existing regular file.")
    return resolved

def load_model(root:Path,raw:str)->Any:
    path=safe_path(root,raw,True)
    if path.stat().st_size>MAX_BYTES: raise ValueError("Model JSON exceeds the 1 MiB input limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"),object_pairs_hook=duplicate_keys,parse_constant=reject_constant)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid model JSON: {exc}") from exc

def write_report(root:Path,raw:str,report:dict)->None:
    path=safe_path(root,raw)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()): raise ValueError("Output must be a regular file.")
    descriptor,temp=tempfile.mkstemp(prefix=".v39-",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(descriptor,"w",encoding="utf-8") as stream:
            json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        Path(temp).replace(path)
    finally:
        try: Path(temp).unlink()
        except FileNotFoundError: pass

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("doctor"); p.add_argument("--root",required=True)
    p=sub.add_parser("validate"); p.add_argument("--root",required=True); p.add_argument("--model",required=True)
    p=sub.add_parser("simulate"); p.add_argument("--root",required=True); p.add_argument("--model",required=True); p.add_argument("--output",required=True)
    args=parser.parse_args()
    try:
        root=resolve_root(args.root)
        if args.command=="doctor":
            print(f"V{VERSION} ready | project={root}"); return 0
        model=load_model(root,args.model)
        errors=validate_model(model)
        if errors:
            for error in errors: print("FAIL: "+error)
            return 1
        if args.command=="validate":
            print("PASS: economy model structure and constraints are valid."); return 0
        report=simulate_model(model)
        write_report(root,args.output,report)
        print(f"PASS: deterministic simulation written; cohorts={report['summary']['cohort_count']}; warnings={report['summary']['warning_count']}.")
        return 0
    except (OSError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
