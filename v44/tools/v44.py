#!/usr/bin/env python3
"""Offline validator and descriptive summarizer for privacy-minimized Roblox feedback."""
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

VERSION = "44.0.0"
MAX_INPUT_BYTES = 1024 * 1024
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
RESPONSE_REF = re.compile(r"^fb_[a-z0-9]{8,24}$")
TOPICS = {"onboarding", "core_loop", "progression", "interface", "controls", "performance", "social", "accessibility", "monetization", "other"}
METHODS = {"moderated_playtest", "structured_survey", "support_summary"}
SOURCES = METHODS
SENTIMENTS = {"positive", "neutral", "mixed", "negative"}
IMPACTS = {"low", "medium", "high", "critical"}
STAGES = {"tutorial", "first_session", "repeat_session", "progression", "social", "store", "technical", "other"}
COHORTS = {"new_players", "returning_players", "mobile", "desktop", "console", "unknown"}
TAGS = {"confusing", "friction", "delight", "feature_request", "bug_report", "accessibility", "blocker"}
STUDY_FIELDS = {"schema_version", "study_id", "title", "purpose", "method", "build", "window", "target", "notice", "questions"}
RECORD_FIELDS = {"response_ref", "collected_at", "source", "topic", "sentiment", "impact", "stage", "tags", "cohort"}
DATA_FIELDS = {"schema_version", "study_id", "build_id", "records"}
NOTICE_FIELDS = {"purpose_disclosed", "voluntary", "skip_allowed", "data_minimized", "no_identifiers", "no_free_text", "retention_days", "owner_role"}


def _choice(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def _fields(value: dict, expected: set[str], label: str) -> list[str]:
    errors = []
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return errors


def _string(value: Any, low: int, high: int) -> bool:
    return isinstance(value, str) and low <= len(value) <= high and bool(value.strip())


def _int(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def _timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be an ISO 8601 timestamp with an explicit timezone.")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be a valid ISO 8601 timestamp.")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label} must include a timezone or UTC offset.")
        return None
    return parsed


def validate_study(study: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(study, dict):
        return ["Study must be a JSON object."]
    errors += _fields(study, STUDY_FIELDS, "study")
    if study.get("schema_version") != 1 or isinstance(study.get("schema_version"), bool):
        errors.append("schema_version must be integer 1.")
    if not isinstance(study.get("study_id"), str) or not SLUG.fullmatch(study.get("study_id", "")):
        errors.append("study_id must be a lowercase slug of 2-40 characters.")
    if not _string(study.get("title"), 4, 100):
        errors.append("title must contain 4-100 non-whitespace characters.")
    if not _string(study.get("purpose"), 20, 500):
        errors.append("purpose must contain 20-500 non-whitespace characters.")
    if not _choice(study.get("method"), METHODS):
        errors.append("method must be moderated_playtest, structured_survey, or support_summary.")

    build = study.get("build")
    if not isinstance(build, dict):
        errors.append("build must be an object.")
        build = {}
    else:
        errors += _fields(build, {"build_id", "environment"}, "build")
    if not _string(build.get("build_id"), 1, 60):
        errors.append("build.build_id must contain 1-60 non-whitespace characters.")
    if not _choice(build.get("environment"), {"private_test", "staging", "published"}):
        errors.append("build.environment must be private_test, staging, or published.")

    window = study.get("window")
    if not isinstance(window, dict):
        errors.append("window must be an object.")
        window = {}
    else:
        errors += _fields(window, {"starts_at", "ends_at"}, "window")
    start = _timestamp(window.get("starts_at"), "window.starts_at", errors)
    end = _timestamp(window.get("ends_at"), "window.ends_at", errors)
    if start and end:
        if end <= start:
            errors.append("window.ends_at must be later than window.starts_at.")
        elif (end - start).total_seconds() > 90 * 86400:
            errors.append("Study window must not exceed 90 days.")

    target = study.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object.")
        target = {}
    else:
        errors += _fields(target, {"minimum_responses", "maximum_responses", "small_cell_threshold"}, "target")
    minimum = target.get("minimum_responses")
    maximum = target.get("maximum_responses")
    threshold = target.get("small_cell_threshold")
    if not _int(minimum, 5, 5000):
        errors.append("target.minimum_responses must be an integer from 5 to 5000.")
    if not _int(maximum, 5, 10000):
        errors.append("target.maximum_responses must be an integer from 5 to 10000.")
    if _int(minimum, 5, 5000) and _int(maximum, 5, 10000) and minimum > maximum:
        errors.append("target.minimum_responses must not exceed target.maximum_responses.")
    if not _int(threshold, 3, 20):
        errors.append("target.small_cell_threshold must be an integer from 3 to 20.")

    notice = study.get("notice")
    if not isinstance(notice, dict):
        errors.append("notice must be an object.")
        notice = {}
    else:
        errors += _fields(notice, NOTICE_FIELDS, "notice")
    for flag in ("purpose_disclosed", "voluntary", "skip_allowed", "data_minimized", "no_identifiers", "no_free_text"):
        if notice.get(flag) is not True:
            errors.append(f"notice.{flag} must be true.")
    if not _int(notice.get("retention_days"), 1, 90):
        errors.append("notice.retention_days must be an integer from 1 to 90.")
    if not _string(notice.get("owner_role"), 2, 60):
        errors.append("notice.owner_role must contain 2-60 non-whitespace characters.")

    questions = study.get("questions")
    if not isinstance(questions, list) or not 1 <= len(questions) <= 20:
        errors.append("questions must contain 1-20 structured prompts.")
        questions = []
    seen: set[str] = set()
    for index, question in enumerate(questions):
        label = f"questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += _fields(question, {"question_id", "topic", "prompt"}, label)
        question_id = question.get("question_id")
        if not isinstance(question_id, str) or not SLUG.fullmatch(question_id):
            errors.append(f"{label}.question_id must be a lowercase slug.")
        elif question_id in seen:
            errors.append(f"Duplicate question_id: {question_id}.")
        else:
            seen.add(question_id)
        if not _choice(question.get("topic"), TOPICS):
            errors.append(f"{label}.topic is not in the supported topic vocabulary.")
        if not _string(question.get("prompt"), 8, 240):
            errors.append(f"{label}.prompt must contain 8-240 non-whitespace characters.")
    return errors


def validate_data(study: Any, data: Any) -> list[str]:
    errors = validate_study(study)
    if not isinstance(data, dict):
        return errors + ["Feedback data must be a JSON object."]
    errors += _fields(data, DATA_FIELDS, "feedback data")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        errors.append("feedback data schema_version must be integer 1.")
    study_id = study.get("study_id") if isinstance(study, dict) else None
    if data.get("study_id") != study_id:
        errors.append("feedback data study_id must match the study.")
    build_obj = study.get("build", {}) if isinstance(study, dict) else {}
    build_id = build_obj.get("build_id") if isinstance(build_obj, dict) else None
    if data.get("build_id") != build_id:
        errors.append("feedback data build_id must match the study build.")
    records = data.get("records")
    if not isinstance(records, list) or not 1 <= len(records) <= 10000:
        errors.append("records must contain 1-10000 coded feedback records.")
        return errors

    start = end = None
    window = study.get("window", {}) if isinstance(study, dict) else {}
    if isinstance(window, dict):
        start_value, end_value = window.get("starts_at"), window.get("ends_at")
        if isinstance(start_value, str) and isinstance(end_value, str):
            try:
                parsed_start = datetime.fromisoformat(start_value.replace("Z", "+00:00"))
                parsed_end = datetime.fromisoformat(end_value.replace("Z", "+00:00"))
                if parsed_start.tzinfo is not None and parsed_end.tzinfo is not None:
                    start, end = parsed_start, parsed_end
            except ValueError:
                pass

    seen: set[str] = set()
    for index, record in enumerate(records):
        label = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += _fields(record, RECORD_FIELDS, label)
        ref = record.get("response_ref")
        if not isinstance(ref, str) or not RESPONSE_REF.fullmatch(ref):
            errors.append(f"{label}.response_ref must be a study-scoped opaque reference like fb_00000001.")
        elif ref in seen:
            errors.append(f"Duplicate response_ref: {ref}.")
        else:
            seen.add(ref)
        timestamp_errors: list[str] = []
        collected = _timestamp(record.get("collected_at"), f"{label}.collected_at", timestamp_errors)
        errors.extend(timestamp_errors)
        if collected and start and end and (collected < start or collected > end):
            errors.append(f"{label}.collected_at is outside the declared study window.")
        for field, choices in (
            ("source", SOURCES), ("topic", TOPICS), ("sentiment", SENTIMENTS),
            ("impact", IMPACTS), ("stage", STAGES), ("cohort", COHORTS),
        ):
            if not _choice(record.get(field), choices):
                errors.append(f"{label}.{field} is not supported.")
        tags = record.get("tags")
        if (
            not isinstance(tags, list) or len(tags) > 5
            or any(not _choice(tag, TAGS) for tag in tags)
            or (isinstance(tags, list) and len({tag for tag in tags if isinstance(tag, str)}) != len(tags))
        ):
            errors.append(f"{label}.tags must contain up to five unique supported tags.")
    return errors


def audit_study(study: dict) -> dict:
    errors = validate_study(study)
    warnings: list[str] = []
    leading = re.compile(r"\b(always|never|obviously|best|worst|much better|don't you agree)\b", re.I)
    for index, question in enumerate(study.get("questions", []) if isinstance(study, dict) else []):
        if isinstance(question, dict) and isinstance(question.get("prompt"), str) and leading.search(question["prompt"]):
            warnings.append(f"questions[{index}] may be leading; review the wording with a human.")
    if errors:
        status = "blocked"
    else:
        status = "ready_for_human_review"
        warnings.append("Readiness checks validate declared metadata only; verify actual notice, consent, collection controls, and deletion.")
    return {
        "schema_version": 1,
        "tool_version": VERSION,
        "study_id": study.get("study_id") if isinstance(study, dict) else None,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "human_approval_required": True,
    }


def _count_band(count: int) -> str:
    if count < 3:
        raise ValueError("Counts below three must be suppressed.")
    if count <= 5:
        return "3-5"
    if count <= 10:
        return "6-10"
    if count <= 20:
        return "11-20"
    if count <= 50:
        return "21-50"
    return "51+"


def _suppressed_bands(records: list[dict], field: str, threshold: int) -> dict:
    counts: dict[str, int] = {}
    for record in records:
        key = record[field]
        counts[key] = counts.get(key, 0) + 1
    visible = {key: _count_band(value) for key, value in sorted(counts.items()) if value >= threshold}
    return {"count_bands": visible, "has_suppressed_categories": any(value < threshold for value in counts.values())}


def summarize(study: dict, data: dict) -> dict:
    errors = validate_data(study, data)
    if errors:
        raise ValueError("Invalid study/data: " + " | ".join(errors))
    records = data["records"]
    threshold = study["target"]["small_cell_threshold"]
    return {
        "schema_version": 1,
        "tool_version": VERSION,
        "study_id": study["study_id"],
        "build_id": study["build"]["build_id"],
        "topic_counts": _suppressed_bands(records, "topic", threshold),
        "sentiment_counts": _suppressed_bands(records, "sentiment", threshold),
        "impact_counts": _suppressed_bands(records, "impact", threshold),
        "stage_counts": _suppressed_bands(records, "stage", threshold),
        "cohort_counts": _suppressed_bands(records, "cohort", threshold),
        "interpretation": "Broad count bands of coded submissions only. Exact total and small-cell counts are withheld. This sample is not presumed representative; the output does not establish prevalence, causation, or unique-player totals.",
        "status": "candidate_for_human_review",
        "human_decision_required": True,
    }


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str):
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")


def safe_path(root: Path, relative: str) -> Path:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Project root must exist and be a directory.")
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("Path must be a non-empty project-relative path using forward slashes.")
    candidate = Path(relative)
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("Absolute paths, empty paths/segments, and traversal are not allowed.")
    current = root
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink paths are not allowed.")
    resolved = current.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Path escapes the project root.")
    return resolved


def load_json(root: Path, relative: str) -> Any:
    path = safe_path(root, relative)
    if not path.is_file():
        raise ValueError(f"Input file does not exist: {relative}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"Input exceeds the {MAX_INPUT_BYTES}-byte limit: {relative}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates, parse_constant=_reject_constant)


def write_report(root: Path, relative: str, report: dict) -> None:
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temp_name = handle.name
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("doctor")
    cmd.add_argument("--root", required=True, type=Path)
    for name in ("validate-study", "audit"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", required=True, type=Path)
        cmd.add_argument("--study", required=True)
        if name == "audit":
            cmd.add_argument("--output", required=True)
    for name in ("validate-data", "summarize"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", required=True, type=Path)
        cmd.add_argument("--study", required=True)
        cmd.add_argument("--data", required=True)
        if name == "summarize":
            cmd.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        root = args.root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError("Project root must exist and be a directory.")
        if args.command == "doctor":
            print(f"V44 doctor: root={root}; Python={sys.version_info.major}.{sys.version_info.minor}; offline mode.")
            return 0
        study = load_json(root, args.study)
        errors = validate_study(study)
        if args.command == "validate-study":
            for error in errors:
                print("FAIL: " + error)
            if errors:
                return 1
            print("PASS: feedback study metadata is valid.")
            return 0
        if args.command == "audit":
            report = audit_study(study)
            write_report(root, args.output, report)
            for error in errors:
                print("FAIL: " + error)
            for warning in report["warnings"]:
                print("WARN: " + warning)
            print(f"Study audit: {report['status']}.")
            return 1 if errors else 0
        data = load_json(root, args.data)
        if args.command == "validate-data":
            errors = validate_data(study, data)
            for error in errors:
                print("FAIL: " + error)
            if errors:
                return 1
            print(f"PASS: {len(data['records'])} coded feedback records validated.")
            return 0
        report = summarize(study, data)
        write_report(root, args.output, report)
        print(f"PASS: privacy-conscious summary written; status={report['status']}.")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
