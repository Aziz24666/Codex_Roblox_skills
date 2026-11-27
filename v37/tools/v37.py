#!/usr/bin/env python3
"""Offline V37 implementation-plan, scope, dependency, and handoff validator."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "37.0.0"
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_TASKS = 300
MAX_PATHS = 100
MAX_CRITERIA = 40
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
PLAN_ID_RE = re.compile(r"^impl-plan-[a-z0-9]{8,24}$")
PROJECT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
CRITERION_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
EVIDENCE_RE = re.compile(r"^ev-[a-z0-9]{12}$")
RISK_LEVELS = {"low", "medium", "high"}
VERIFICATION_KINDS = {"static", "automated_test", "studio_manual", "runtime_manual"}
TASK_STATUSES = {"completed", "in_progress", "blocked", "not_started"}
CRITERION_RESULTS = {"pass", "fail", "not_run"}
PLAN_FIELDS = {"schema_version", "plan_id", "project_key", "generated_at", "goal", "scope", "tasks"}
SCOPE_FIELDS = {"included_paths", "excluded_paths"}
TASK_FIELDS = {"task_id", "title", "objective", "depends_on", "allowed_paths", "risk", "human_review_required", "acceptance_criteria"}
CRITERION_FIELDS = {"criterion_id", "description", "verification_kind"}
REPORT_FIELDS = {"schema_version", "plan_id", "generated_at", "task_results"}
RESULT_FIELDS = {"task_id", "status", "changed_files", "evidence_refs", "criteria_results"}
CRITERION_RESULT_FIELDS = {"criterion_id", "result"}


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_project_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    if (
        not isinstance(raw, str) or not raw.strip() or len(raw) > 240
        or "\x00" in raw or "\\" in raw or raw.startswith("/")
        or (len(raw) >= 3 and raw[1:3] == ":/")
    ):
        raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Empty, dot, and parent path segments are not allowed.")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Symlink traversal is not allowed.")
    try:
        resolved = root.joinpath(*parts).resolve(strict=must_exist)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Path resolves outside the selected project root.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Input path must identify an existing regular file.")
    return resolved


def load_json(root: Path, raw: str) -> Any:
    path = safe_project_path(root, raw, must_exist=True)
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("JSON input exceeds the 4 MiB limit.")
    try:
        return json.loads(
            path.read_text(encoding="utf-8-sig"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Invalid JSON constant: {value}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON: {exc}") from exc


def valid_time(value: Any) -> bool:
    if not isinstance(value, str) or len(value) > 40:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError:
        return False


def exact_fields(data: dict, required: set[str], allowed: set[str], label: str) -> list[str]:
    issues = []
    missing = sorted(required - data.keys())
    unknown = sorted(data.keys() - allowed)
    if missing:
        issues.append(f"{label} is missing required field(s): {', '.join(missing)}.")
    if unknown:
        issues.append(f"{label} has unsupported field(s): {', '.join(unknown)}.")
    return issues


def valid_path_value(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 200:
        return False
    if "\x00" in value or "\\" in value or value.startswith("/") or (len(value) >= 3 and value[1:3] == ":/"):
        return False
    parts = value.split("/")
    return not any(part in {"", ".", ".."} for part in parts) and not any(ch in value for ch in "*?[]{}")


def within(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def overlaps(left: str, right: str) -> bool:
    return within(left, right) or within(right, left)


def path_is_included(path: str, included: list[str]) -> bool:
    return any(within(path, prefix) for prefix in included)


def path_is_excluded(path: str, excluded: list[str]) -> bool:
    return any(overlaps(path, prefix) for prefix in excluded)


def topological_order(tasks: list[dict]) -> tuple[list[str], bool]:
    by_id = {task["task_id"]: task for task in tasks if isinstance(task, dict) and isinstance(task.get("task_id"), str)}
    indegree = {task_id: 0 for task_id in by_id}
    outgoing = {task_id: [] for task_id in by_id}
    for task_id, task in by_id.items():
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            dependencies = []
        for dependency in dependencies:
            if isinstance(dependency, str) and dependency in by_id and dependency != task_id:
                indegree[task_id] += 1
                outgoing[dependency].append(task_id)
    ready = sorted(task_id for task_id, count in indegree.items() if count == 0)
    order = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for child in sorted(outgoing[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
                ready.sort()
    return order, len(order) == len(by_id)


def dependency_reaches(start: str, target: str, by_id: dict[str, dict]) -> bool:
    initial = by_id.get(start, {}).get("depends_on", [])
    pending = list(initial) if isinstance(initial, list) else []
    visited = set()
    while pending:
        current = pending.pop()
        if not isinstance(current, str) or current in visited:
            continue
        if current == target:
            return True
        visited.add(current)
        if current in by_id:
            next_dependencies = by_id[current].get("depends_on", [])
            if isinstance(next_dependencies, list):
                pending.extend(next_dependencies)
    return False


def validate_plan(data: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["Plan must be a JSON object."]
    issues += exact_fields(data, PLAN_FIELDS, PLAN_FIELDS, "Plan")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        issues.append("schema_version must be integer 1.")
    if not isinstance(data.get("plan_id"), str) or not PLAN_ID_RE.fullmatch(data["plan_id"]):
        issues.append("plan_id must use impl-plan- followed by 8-24 lowercase letters or digits.")
    if not isinstance(data.get("project_key"), str) or not PROJECT_RE.fullmatch(data["project_key"]):
        issues.append("project_key must be a lowercase project slug.")
    if not valid_time(data.get("generated_at")):
        issues.append("generated_at must be an ISO-8601 timestamp with timezone.")
    if not isinstance(data.get("goal"), str) or not data["goal"].strip() or len(data["goal"]) > 1500:
        issues.append("goal must be a non-empty string of at most 1500 characters.")

    scope = data.get("scope")
    included: list[str] = []
    excluded: list[str] = []
    if not isinstance(scope, dict):
        issues.append("scope must be an object.")
    else:
        issues += exact_fields(scope, SCOPE_FIELDS, SCOPE_FIELDS, "scope")
        for field, output in (("included_paths", included), ("excluded_paths", excluded)):
            values = scope.get(field)
            minimum = 1 if field == "included_paths" else 0
            if not isinstance(values, list) or not minimum <= len(values) <= MAX_PATHS:
                issues.append(f"scope.{field} must be a list containing {minimum}-{MAX_PATHS} paths.")
                continue
            for index, value in enumerate(values):
                if not valid_path_value(value):
                    issues.append(f"scope.{field}[{index}] is not a safe project-relative path.")
                elif value in output:
                    issues.append(f"scope.{field} contains duplicate path {value}.")
                else:
                    output.append(value)
    for include in included:
        if any(within(include, excluded_path) for excluded_path in excluded):
            issues.append(f"Included path {include} is entirely within an excluded path.")

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
        return issues + [f"tasks must contain 1-{MAX_TASKS} task objects."]
    ids: set[str] = set()
    by_id: dict[str, dict] = {}
    for index, task in enumerate(tasks):
        label = f"tasks[{index}]"
        if not isinstance(task, dict):
            issues.append(f"{label} must be an object.")
            continue
        issues += exact_fields(task, TASK_FIELDS, TASK_FIELDS, label)
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not ID_RE.fullmatch(task_id):
            issues.append(f"{label}.task_id must be a lowercase stable ID.")
        elif task_id in ids:
            issues.append(f"Duplicate task_id: {task_id}.")
        else:
            ids.add(task_id)
            by_id[task_id] = task
        for field, limit in (("title", 140), ("objective", 800)):
            value = task.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                issues.append(f"{label}.{field} must be a non-empty string of at most {limit} characters.")
        if not isinstance(task.get("risk"), str) or task.get("risk") not in RISK_LEVELS:
            issues.append(f"{label}.risk must be low, medium, or high.")
        if not isinstance(task.get("human_review_required"), bool):
            issues.append(f"{label}.human_review_required must be boolean.")

        dependencies = task.get("depends_on")
        if not isinstance(dependencies, list) or len(dependencies) > MAX_TASKS:
            issues.append(f"{label}.depends_on must be a list of task IDs.")
        else:
            if any(not isinstance(dep, str) or not ID_RE.fullmatch(dep) for dep in dependencies):
                issues.append(f"{label}.depends_on contains an invalid task ID.")
            elif len(set(dependencies)) != len(dependencies):
                issues.append(f"{label}.depends_on contains duplicate IDs.")
            if isinstance(task_id, str) and task_id in dependencies:
                issues.append(f"{label} cannot depend on itself.")

        allowed_paths = task.get("allowed_paths")
        if not isinstance(allowed_paths, list) or not 1 <= len(allowed_paths) <= MAX_PATHS:
            issues.append(f"{label}.allowed_paths must contain 1-{MAX_PATHS} safe project-relative paths.")
            allowed_paths = []
        else:
            safe_paths = []
            for path_index, path in enumerate(allowed_paths):
                if not valid_path_value(path):
                    issues.append(f"{label}.allowed_paths[{path_index}] is not a safe project-relative path.")
                elif path in safe_paths:
                    issues.append(f"{label}.allowed_paths contains duplicate path {path}.")
                else:
                    safe_paths.append(path)
                    if included and not path_is_included(path, included):
                        issues.append(f"{label}.allowed_paths entry {path} is outside included_paths.")
                    if any(within(path, excluded_path) for excluded_path in excluded):
                        issues.append(f"{label}.allowed_paths entry {path} is inside excluded_paths.")
            allowed_paths = safe_paths

        criteria = task.get("acceptance_criteria")
        manual_required = False
        if not isinstance(criteria, list) or not 1 <= len(criteria) <= MAX_CRITERIA:
            issues.append(f"{label}.acceptance_criteria must contain 1-{MAX_CRITERIA} criteria.")
        else:
            criterion_ids = set()
            for criterion_index, criterion in enumerate(criteria):
                criterion_label = f"{label}.acceptance_criteria[{criterion_index}]"
                if not isinstance(criterion, dict):
                    issues.append(f"{criterion_label} must be an object.")
                    continue
                issues += exact_fields(criterion, CRITERION_FIELDS, CRITERION_FIELDS, criterion_label)
                criterion_id = criterion.get("criterion_id")
                if not isinstance(criterion_id, str) or not CRITERION_RE.fullmatch(criterion_id):
                    issues.append(f"{criterion_label}.criterion_id must be a lowercase stable ID.")
                elif criterion_id in criterion_ids:
                    issues.append(f"{criterion_label} duplicates criterion_id {criterion_id}.")
                else:
                    criterion_ids.add(criterion_id)
                description = criterion.get("description")
                if not isinstance(description, str) or not description.strip() or len(description) > 500:
                    issues.append(f"{criterion_label}.description must be a non-empty string of at most 500 characters.")
                kind = criterion.get("verification_kind")
                if not isinstance(kind, str) or kind not in VERIFICATION_KINDS:
                    issues.append(f"{criterion_label}.verification_kind is unsupported.")
                elif kind in {"studio_manual", "runtime_manual"}:
                    manual_required = True
        if task.get("risk") == "high" and task.get("human_review_required") is not True:
            issues.append(f"{label} is high risk and must require human review.")
        if manual_required and task.get("human_review_required") is not True:
            issues.append(f"{label} has Studio/runtime criteria and must require human review.")

    for task in by_id.values():
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if isinstance(dependency, str) and dependency not in by_id:
                issues.append(f"Task {task.get('task_id')} references missing dependency {dependency}.")

    _, acyclic = topological_order(tasks)
    if not acyclic:
        issues.append("Task dependency graph contains a cycle.")

    # Independent tasks must not claim overlapping paths; sequence the tasks if they share a change surface.
    valid_tasks = [task for task in tasks if isinstance(task, dict) and isinstance(task.get("task_id"), str)]
    for index, left in enumerate(valid_tasks):
        left_paths = left.get("allowed_paths", [])
        if not isinstance(left_paths, list):
            continue
        for right in valid_tasks[index + 1:]:
            right_paths = right.get("allowed_paths", [])
            if not isinstance(right_paths, list):
                continue
            shared = any(
                isinstance(a, str) and isinstance(b, str) and overlaps(a, b)
                for a in left_paths for b in right_paths
            )
            if not shared:
                continue
            left_id, right_id = left.get("task_id"), right.get("task_id")
            if not isinstance(left_id, str) or not isinstance(right_id, str):
                continue
            ordered = dependency_reaches(left_id, right_id, by_id) or dependency_reaches(right_id, left_id, by_id)
            if not ordered:
                issues.append(f"Tasks {left_id} and {right_id} have overlapping allowed_paths without a dependency order.")
    return sorted(set(issues))


def audit_plan(data: dict) -> dict:
    order, acyclic = topological_order(data.get("tasks", []))
    tasks = data.get("tasks", [])
    risk_counts = {risk: sum(1 for task in tasks if task.get("risk") == risk) for risk in sorted(RISK_LEVELS)}
    overlap_count = 0
    for index, left in enumerate(tasks):
        for right in tasks[index + 1:]:
            if any(overlaps(a, b) for a in left.get("allowed_paths", []) for b in right.get("allowed_paths", [])):
                overlap_count += 1
    return {
        "schema_version": 1,
        "plan_id": data["plan_id"],
        "status": "ready_for_implementation",
        "summary": {
            "task_count": len(tasks),
            "dependency_graph_acyclic": acyclic,
            "scope_overlap_pairs": overlap_count,
            "risk_counts": risk_counts,
        },
        "execution_order": order,
        "limitations": ["Offline plan metadata audit only; this does not inspect the source tree, execute tasks, or verify implementation feasibility."],
    }


def validate_report(plan: dict, report: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(report, dict):
        return ["Implementation report must be a JSON object."]
    issues += exact_fields(report, REPORT_FIELDS, REPORT_FIELDS, "Report")
    if report.get("schema_version") != 1 or isinstance(report.get("schema_version"), bool):
        issues.append("Report schema_version must be integer 1.")
    if report.get("plan_id") != plan.get("plan_id"):
        issues.append("Report plan_id does not match the supplied plan.")
    if not valid_time(report.get("generated_at")):
        issues.append("Report generated_at must be an ISO-8601 timestamp with timezone.")
    planned_tasks = {task["task_id"]: task for task in plan["tasks"]}
    results = report.get("task_results")
    if not isinstance(results, list) or len(results) != len(planned_tasks):
        return issues + ["task_results must contain exactly one result for every planned task."]
    result_by_id: dict[str, dict] = {}
    for index, result in enumerate(results):
        label = f"task_results[{index}]"
        if not isinstance(result, dict):
            issues.append(f"{label} must be an object.")
            continue
        issues += exact_fields(result, RESULT_FIELDS, RESULT_FIELDS, label)
        task_id = result.get("task_id")
        if not isinstance(task_id, str) or task_id not in planned_tasks:
            issues.append(f"{label}.task_id is not present in the plan.")
            continue
        if task_id in result_by_id:
            issues.append(f"Duplicate task result for {task_id}.")
            continue
        result_by_id[task_id] = result
        status = result.get("status")
        if not isinstance(status, str) or status not in TASK_STATUSES:
            issues.append(f"{label}.status is unsupported.")
        changed_files = result.get("changed_files")
        if not isinstance(changed_files, list) or len(changed_files) > 1000:
            issues.append(f"{label}.changed_files must be a list of at most 1000 paths.")
            changed_files = []
        task = planned_tasks[task_id]
        allowed = task.get("allowed_paths", [])
        included = plan.get("scope", {}).get("included_paths", [])
        excluded = plan.get("scope", {}).get("excluded_paths", [])
        seen_files = set()
        for file_index, path in enumerate(changed_files):
            if not valid_path_value(path):
                issues.append(f"{label}.changed_files[{file_index}] is not a safe relative path.")
                continue
            if path in seen_files:
                issues.append(f"{label}.changed_files contains duplicate path {path}.")
            seen_files.add(path)
            if not path_is_included(path, included) or path_is_excluded(path, excluded):
                issues.append(f"{label} changed path {path} is outside project scope or is excluded.")
            if not any(within(path, prefix) for prefix in allowed):
                issues.append(f"{label} changed path {path} is outside task {task_id} allowed_paths.")

        evidence = result.get("evidence_refs")
        if not isinstance(evidence, list) or len(evidence) > 100:
            issues.append(f"{label}.evidence_refs must be a list of at most 100 opaque references.")
            evidence = []
        else:
            if any(not isinstance(ref, str) or not EVIDENCE_RE.fullmatch(ref) for ref in evidence):
                issues.append(f"{label}.evidence_refs may contain only opaque ev- references.")
            if len(set(x for x in evidence if isinstance(x, str))) != len(evidence):
                issues.append(f"{label}.evidence_refs contains duplicates.")

        planned_criteria = {
            item["criterion_id"]: item for item in task.get("acceptance_criteria", [])
            if isinstance(item, dict) and isinstance(item.get("criterion_id"), str)
        }
        criterion_results = result.get("criteria_results")
        if not isinstance(criterion_results, list) or len(criterion_results) > MAX_CRITERIA:
            issues.append(f"{label}.criteria_results must be a list of at most {MAX_CRITERIA} items.")
            criterion_results = []
        seen_criteria = set()
        for criterion_index, criterion_result in enumerate(criterion_results):
            criterion_label = f"{label}.criteria_results[{criterion_index}]"
            if not isinstance(criterion_result, dict):
                issues.append(f"{criterion_label} must be an object.")
                continue
            issues += exact_fields(criterion_result, CRITERION_RESULT_FIELDS, CRITERION_RESULT_FIELDS, criterion_label)
            criterion_id = criterion_result.get("criterion_id")
            if not isinstance(criterion_id, str) or criterion_id not in planned_criteria:
                issues.append(f"{criterion_label}.criterion_id is not present in task {task_id}.")
                continue
            if criterion_id in seen_criteria:
                issues.append(f"{criterion_label} duplicates criterion {criterion_id}.")
                continue
            seen_criteria.add(criterion_id)
            outcome = criterion_result.get("result")
            if not isinstance(outcome, str) or outcome not in CRITERION_RESULTS:
                issues.append(f"{criterion_label}.result must be pass, fail, or not_run.")
            elif outcome == "pass" and planned_criteria[criterion_id].get("verification_kind") in {"studio_manual", "runtime_manual"} and not evidence:
                issues.append(f"{criterion_label} needs an evidence_ref because its verification is manual.")
        if status == "completed":
            missing = sorted(set(planned_criteria) - seen_criteria)
            if missing:
                issues.append(f"Completed task {task_id} is missing acceptance result(s): {', '.join(missing)}.")
            if any(
                isinstance(item, dict) and item.get("result") != "pass"
                for item in criterion_results
            ):
                issues.append(f"Completed task {task_id} has a failed or unrun acceptance criterion.")
        if status == "not_started" and changed_files:
            issues.append(f"Not-started task {task_id} cannot report changed files.")

    missing_tasks = sorted(set(planned_tasks) - set(result_by_id))
    if missing_tasks:
        issues.append("Report is missing task result(s): " + ", ".join(missing_tasks) + ".")
    for task_id, result in result_by_id.items():
        if result.get("status") == "completed":
            for dependency in planned_tasks[task_id].get("depends_on", []):
                dep_result = result_by_id.get(dependency)
                if dep_result is None or dep_result.get("status") != "completed":
                    issues.append(f"Task {task_id} is completed before dependency {dependency}.")
    return sorted(set(issues))


def audit_report(plan: dict, report: dict) -> dict:
    planned = {task["task_id"]: task for task in plan["tasks"]}
    results = {item["task_id"]: item for item in report["task_results"]}
    counts = {status: sum(1 for item in results.values() if item["status"] == status) for status in sorted(TASK_STATUSES)}
    failed_criteria = []
    for task_id, item in results.items():
        failed = [criterion["criterion_id"] for criterion in item.get("criteria_results", []) if criterion.get("result") == "fail"]
        if failed:
            failed_criteria.append({"task_id": task_id, "criterion_ids": failed})
    return {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": "complete" if counts["completed"] == len(planned) and not failed_criteria else "needs_followup",
        "summary": {
            "task_count": len(planned),
            "status_counts": counts,
            "failed_criteria": len(failed_criteria),
        },
        "failed_criteria": failed_criteria,
        "limitations": ["The report validates recorded metadata and path scope only; evidence references are opaque and are not authenticated or inspected."],
    }


def write_json(root: Path, raw: str, value: dict) -> None:
    path = safe_project_path(root, raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Output path must be a regular file.")
    fd, temporary = tempfile.mkstemp(prefix=".v37-", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", closefd=True) as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor")
    doctor.add_argument("--root", required=True)
    validate = commands.add_parser("validate-plan")
    validate.add_argument("--root", required=True)
    validate.add_argument("--plan", required=True)
    audit = commands.add_parser("audit-plan")
    audit.add_argument("--root", required=True)
    audit.add_argument("--plan", required=True)
    audit.add_argument("--output", required=True)
    validate_result = commands.add_parser("validate-report")
    validate_result.add_argument("--root", required=True)
    validate_result.add_argument("--plan", required=True)
    validate_result.add_argument("--report", required=True)
    report_audit = commands.add_parser("audit-report")
    report_audit.add_argument("--root", required=True)
    report_audit.add_argument("--plan", required=True)
    report_audit.add_argument("--report", required=True)
    report_audit.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "doctor":
            print(f"V{VERSION} ready | project={root}")
            return 0
        plan = load_json(root, args.plan)
        plan_issues = validate_plan(plan)
        if plan_issues:
            for issue in plan_issues:
                print("FAIL: " + issue)
            return 1
        if args.command == "validate-plan":
            print("PASS: implementation plan is structurally and logically valid.")
            return 0
        if args.command == "audit-plan":
            result = audit_plan(plan)
            write_json(root, args.output, result)
            print(f"PASS: {result['summary']['task_count']} tasks; dependency graph acyclic; scope review passed.")
            return 0
        report = load_json(root, args.report)
        report_issues = validate_report(plan, report)
        if report_issues:
            for issue in report_issues:
                print("FAIL: " + issue)
            return 1
        if args.command == "validate-report":
            print("PASS: implementation report matches the plan and declared scope.")
            return 0
        result = audit_report(plan, report)
        write_json(root, args.output, result)
        print(f"{result['status']}: {result['summary']['status_counts']['completed']} of {result['summary']['task_count']} tasks completed.")
        return 0 if result["status"] == "complete" else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
