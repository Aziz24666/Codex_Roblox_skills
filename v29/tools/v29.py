#!/usr/bin/env python3
"""Read-only Roblox performance review, budget validation, and capture comparison."""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "29.0.0"
MAX_FILES = 10_000
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
SKIP_DIRS = {".git", ".agents", ".codex", ".venv", "venv", "__pycache__", "node_modules", "target", "build", "dist"}
PROFILES = {"low_end_mobile", "high_end_mobile", "desktop"}
METRICS = {"frame_time_ms_p50", "frame_time_ms_p95", "memory_mb", "load_time_s", "script_cpu_ms", "replication_kbps"}
DEFAULT_AUDIT = ".codex/reports/v29-performance-audit.json"

FINDING_PATTERNS = (
    ("high", re.compile(r"\bwhile\s+true\s+do\b", re.I), "Unbounded while-true loop: confirm it yields, has a stop condition, and does not poll more often than needed."),
    ("medium", re.compile(r"\btask\.wait\s*\(\s*(?:0?\.\d+|[0-9]+)\s*\)", re.I), "Explicit task.wait interval: inspect very short polling intervals and prefer event-driven updates where possible."),
    ("medium", re.compile(r"\b(?:GetDescendants|GetChildren)\s*\(", re.I), "Hierarchy traversal: avoid repeatedly traversing large trees in hot paths; cache carefully and invalidate on relevant changes."),
    ("medium", re.compile(r"\bInstance\.new\s*\(", re.I), "Instance allocation: profile allocation frequency and reuse or pool only when lifecycle and cleanup are well-defined."),
    ("medium", re.compile(r":\s*Clone\s*\(", re.I), "Clone operation: profile clone frequency, asset size, and cleanup; avoid repeated bursts in latency-sensitive paths."),
    ("medium", re.compile(r"\b(?:Heartbeat|RenderStepped|Stepped)\s*:\s*Connect\b", re.I), "Per-frame callback: keep work bounded, avoid unnecessary connections, and disconnect when the owning system stops."),
    ("low", re.compile(r":\s*Connect\s*\(", re.I), "Event connection: verify connection lifetime, duplicate registration, and explicit cleanup."),
)

def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root

def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, RuntimeError, ValueError):
        return False

def safe_project_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    supplied = Path(raw).expanduser()
    candidate = supplied if supplied.is_absolute() else root / supplied
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Input/output path must stay inside the selected project root.") from exc
    if not relative.parts or ".." in relative.parts:
        raise ValueError("Input/output path must stay inside the selected project root.")
    probe = root
    for part in relative.parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Input/output path cannot traverse a symlink.")
    resolved = candidate.resolve(strict=must_exist)
    if not resolved.is_relative_to(root):
        raise ValueError("Input/output path resolves outside the selected project root.")
    if must_exist and not resolved.is_file():
        raise ValueError("Input path must be an existing regular file.")
    return resolved

def safe_output_path(root: Path, raw: str) -> Path:
    target = safe_project_path(root, raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve(strict=True)
    if not parent.is_relative_to(root):
        raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent / target.name

def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass

def iter_luau_files(root: Path, max_files: int, warnings: list[str]) -> list[Path]:
    result: list[Path] = []
    total_bytes = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept = []
        for name in sorted(dirnames):
            if name in SKIP_DIRS:
                continue
            child = current / name
            if child.is_symlink() or not is_within(child, root):
                warnings.append(f"Skipped symlinked or out-of-root directory: {child.relative_to(root)}")
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = current / name
            if path.suffix.lower() not in {".lua", ".luau"}:
                continue
            if path.is_symlink() or not is_within(path, root):
                warnings.append(f"Skipped symlinked or out-of-root source: {path.relative_to(root)}")
                continue
            try:
                size = path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat source file: {path.relative_to(root)}")
                continue
            if size > MAX_FILE_BYTES:
                warnings.append(f"Skipped oversized source file ({size} bytes): {path.relative_to(root)}")
                continue
            if total_bytes + size > MAX_TOTAL_BYTES:
                warnings.append("Stopped at the 256 MiB aggregate source-size safety limit.")
                return result
            result.append(path)
            total_bytes += size
            if len(result) >= max_files:
                warnings.append(f"Stopped at the configured {max_files}-file scan limit.")
                return result
    return result

def audit_source(root: Path, max_files: int = MAX_FILES) -> dict[str, Any]:
    warnings: list[str] = []
    files = iter_luau_files(root, max_files, warnings)
    findings: list[dict[str, Any]] = []
    read_failures: list[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            read_failures.append(relative)
            continue
        lines = source.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            for severity, pattern, message in FINDING_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                context = "\n".join(lines[index:min(index + 8, len(lines))])
                guidance = message
                if "while-true" in message.lower():
                    if re.search(r"\b(?:task\.)?wait\s*\(", context, re.I):
                        guidance += " A yield appears nearby, but verify its interval and actual scheduler cost."
                    else:
                        guidance += " No obvious wait/yield appears in the nearby lines; inspect this path first."
                if "task.wait interval" in message.lower():
                    interval = re.search(r"\btask\.wait\s*\(\s*([0-9]*\.?[0-9]+)\s*\)", line, re.I)
                    if interval and float(interval.group(1)) < 0.03:
                        severity = "high"
                        guidance += " The literal interval is below 30 ms; confirm this polling rate is genuinely required."
                if "per-frame callback" in message.lower() and re.search(r"\b(?:GetDescendants|GetChildren|Instance\.new)\s*\(", context, re.I):
                    severity = "high"
                    guidance += " A potentially costly operation appears in the nearby callback; profile the complete callback."
                findings.append({"file": relative, "line": index + 1, "severity": severity,
                                 "signal": match.group(0)[:100], "review_guidance": guidance})
                break
            if len(findings) >= 500:
                warnings.append("Stopped recording at the 500-finding report limit.")
                break
        if len(findings) >= 500:
            break
    counts = {level: sum(1 for item in findings if item["severity"] == level) for level in ("high", "medium", "low")}
    return {
        "report_type": "v29_static_performance_audit", "schema_version": 1, "version": VERSION,
        "project_root_name": root.name,
        "inventory": {"luau_files_discovered": len(files), "files_read": len(files) - len(read_failures)},
        "finding_counts": counts, "findings": findings, "read_failures": read_failures, "warnings": warnings,
        "measurement_status": "not_measured_by_static_scan",
        "limitations": [
            "This is a conservative text-pattern heuristic, not a Luau parser, profiler, benchmark, or proof of a performance defect.",
            "It does not measure frame time, FPS, memory, script CPU, replication, load time, or device-specific behavior.",
            "Findings need context review and confirmation with Roblox Studio MicroProfiler, Script Profiler, Developer Console, and representative hardware.",
            "The scanner does not execute scripts, modify source files, connect to Roblox services, or optimize the project automatically.",
        ],
    }

def positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and float(value) > 0

def validate_measurement(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Capture must be a JSON object."]
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")
    if not isinstance(data.get("build"), str) or not data["build"].strip() or len(data["build"]) > 120:
        errors.append("build must be a non-empty string of at most 120 characters.")
    if data.get("device_profile") not in PROFILES:
        errors.append("device_profile must be low_end_mobile, high_end_mobile, or desktop.")
    if not isinstance(data.get("measurement_source"), str) or not data["measurement_source"].strip():
        errors.append("measurement_source must identify where the measurements came from.")
    metrics = data.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        errors.append("metrics must be a non-empty object.")
        return errors
    unknown = set(metrics) - METRICS
    if unknown:
        errors.append("Unknown metrics: " + ", ".join(sorted(unknown)) + ".")
    for name, value in metrics.items():
        if name in METRICS and not positive_number(value):
            errors.append(f"metrics.{name} must be a finite positive number.")
    if positive_number(metrics.get("frame_time_ms_p50")) and positive_number(metrics.get("frame_time_ms_p95")):
        if float(metrics["frame_time_ms_p95"]) < float(metrics["frame_time_ms_p50"]):
            errors.append("frame_time_ms_p95 cannot be lower than frame_time_ms_p50.")
    return errors

def validate_budgets(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["Budget configuration must be a JSON object."]
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1.")
    budgets = data.get("budgets")
    if not isinstance(budgets, dict):
        return errors + ["budgets must be an object."]
    missing = PROFILES - set(budgets)
    extra = set(budgets) - PROFILES
    if missing:
        errors.append("Missing device profiles: " + ", ".join(sorted(missing)) + ".")
    if extra:
        errors.append("Unknown device profiles: " + ", ".join(sorted(extra)) + ".")
    for profile, limits in budgets.items():
        if profile not in PROFILES:
            continue
        if not isinstance(limits, dict) or not limits:
            errors.append(f"budgets.{profile} must be a non-empty object.")
            continue
        unknown = set(limits) - METRICS
        if unknown:
            errors.append(f"budgets.{profile} has unknown metrics: " + ", ".join(sorted(unknown)) + ".")
        for metric, value in limits.items():
            if metric in METRICS and not positive_number(value):
                errors.append(f"budgets.{profile}.{metric} must be a finite positive number.")
    return errors

def read_json_file(root: Path, raw: str) -> tuple[Path, Any]:
    path = safe_project_path(root, raw, must_exist=True)
    try:
        return path, json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc

def compare_measurements(baseline: Any, candidate: Any, budgets: Any = None, threshold_pct: float = 5.0) -> dict[str, Any]:
    errors = validate_measurement(baseline) + ["candidate: " + item for item in validate_measurement(candidate)]
    if errors:
        raise ValueError("Invalid capture data: " + " ".join(errors))
    if baseline["device_profile"] != candidate["device_profile"]:
        raise ValueError("Baseline and candidate must use the same device_profile.")
    if baseline["build"] == candidate["build"]:
        raise ValueError("Baseline and candidate build identifiers must differ.")
    if not isinstance(threshold_pct, (int, float)) or isinstance(threshold_pct, bool) or not math.isfinite(float(threshold_pct)) or threshold_pct < 0:
        raise ValueError("regression threshold must be a finite non-negative number.")
    if budgets is not None:
        budget_errors = validate_budgets(budgets)
        if budget_errors:
            raise ValueError("Invalid budget configuration: " + " ".join(budget_errors))
    profile = candidate["device_profile"]
    limits = budgets["budgets"].get(profile, {}) if budgets else {}
    common = sorted(set(baseline["metrics"]) & set(candidate["metrics"]))
    metric_results = []
    for metric in common:
        before = float(baseline["metrics"][metric])
        after = float(candidate["metrics"][metric])
        delta_pct = ((after - before) / before) * 100.0
        limit = limits.get(metric)
        metric_results.append({"metric": metric, "baseline": before, "candidate": after,
            "delta_pct": round(delta_pct, 4), "regression": delta_pct > float(threshold_pct),
            "budget_limit": limit, "over_budget": bool(limit is not None and after > float(limit))})
    return {
        "report_type": "v29_performance_comparison", "schema_version": 1,
        "baseline_build": baseline["build"], "candidate_build": candidate["build"], "device_profile": profile,
        "regression_threshold_pct": float(threshold_pct), "metrics": metric_results,
        "regression_count": sum(1 for item in metric_results if item["regression"]),
        "budget_violation_count": sum(1 for item in metric_results if item["over_budget"]),
        "missing_from_candidate": sorted(set(baseline["metrics"]) - set(candidate["metrics"])),
        "new_in_candidate": sorted(set(candidate["metrics"]) - set(baseline["metrics"])),
        "measurement_source": {"baseline": baseline["measurement_source"], "candidate": candidate["measurement_source"]},
        "limitations": [
            "Comparisons are only as reliable as the supplied captures and their matching test conditions.",
            "The tool does not capture profiler data, launch Roblox, or infer measurements from source code.",
            "Repeat captures and compare equivalent scenes, device classes, player counts, and runtime conditions.",
        ],
    }

def build_summary(audit: dict[str, Any] | None, comparison: dict[str, Any] | None) -> dict[str, Any]:
    return {"report_type": "v29_performance_review", "schema_version": 1,
        "static_audit": audit, "measurement_comparison": comparison,
        "interpretation": [
            "Static findings are review leads, not measured regressions.",
            "A missing measurement comparison means no before/after performance claim can be made.",
            "Validate suspected bottlenecks with Roblox profiling tools on representative hardware before changing code.",
        ]}

def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    warnings: list[str] = []
    files = iter_luau_files(root, MAX_FILES, warnings)
    print(f"Project: {root}")
    print(f"Luau/Lua source files discovered: {len(files)}")
    print("Optional local tools:")
    for executable in ("luau-analyze", "rojo", "git"):
        print(f"  {executable}: {shutil.which(executable) or 'not found on PATH'}")
    print("Roblox Studio profiling must be performed in Studio on representative devices.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0

def command_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    report = audit_source(root, max(1, min(args.max_files, MAX_FILES)))
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    print(f"Read-only audit written to: {output}")
    print(f"Files: {report['inventory']['files_read']}; findings: {sum(report['finding_counts'].values())}")
    print("Measurements: not collected by static analysis.")
    return 0

def command_budget(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    path, data = read_json_file(root, args.config)
    errors = validate_budgets(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    result = {"report_type": "v29_budget_validation", "schema_version": 1, "valid": True,
        "config": path.relative_to(root).as_posix(), "device_profiles": sorted(data["budgets"]),
        "metric_limits": data["budgets"]}
    output = safe_output_path(root, args.output)
    atomic_write_json(output, result)
    print(f"PASS: validated {len(result['device_profiles'])} device profiles. Report: {output}")
    return 0

def command_compare(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    _, baseline = read_json_file(root, args.baseline)
    _, candidate = read_json_file(root, args.candidate)
    budgets = read_json_file(root, args.budgets)[1] if args.budgets else None
    try:
        report = compare_measurements(baseline, candidate, budgets, args.regression_threshold_pct)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    output = safe_output_path(root, args.output)
    atomic_write_json(output, report)
    print(f"Comparison written to: {output}")
    print(f"Regressions: {report['regression_count']}; budget violations: {report['budget_violation_count']}")
    return 0

def command_report(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    audit = comparison = None
    if args.audit:
        _, audit = read_json_file(root, args.audit)
        if not isinstance(audit, dict) or audit.get("report_type") != "v29_static_performance_audit":
            print("FAIL: --audit must reference a V29 static performance audit JSON report.")
            return 1
    if args.comparison:
        _, comparison = read_json_file(root, args.comparison)
        if not isinstance(comparison, dict) or comparison.get("report_type") != "v29_performance_comparison":
            print("FAIL: --comparison must reference a V29 comparison JSON report.")
            return 1
    output = safe_output_path(root, args.output)
    atomic_write_json(output, build_summary(audit, comparison))
    print(f"Combined performance review written to: {output}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Inspect local source inventory and optional tooling.")
    doctor.add_argument("--root", required=True)
    doctor.set_defaults(func=command_doctor)
    audit = sub.add_parser("audit", help="Create a read-only heuristic Luau performance review.")
    audit.add_argument("--root", required=True)
    audit.add_argument("--output", default=DEFAULT_AUDIT)
    audit.add_argument("--max-files", type=int, default=MAX_FILES)
    audit.set_defaults(func=command_audit)
    budget = sub.add_parser("budget", help="Validate device-specific performance budgets.")
    budget.add_argument("--root", required=True)
    budget.add_argument("--config", required=True)
    budget.add_argument("--output", default=".codex/reports/v29-budget-validation.json")
    budget.set_defaults(func=command_budget)
    compare = sub.add_parser("compare", help="Compare two externally captured JSON measurement sets.")
    compare.add_argument("--root", required=True)
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--budgets")
    compare.add_argument("--regression-threshold-pct", type=float, default=5.0)
    compare.add_argument("--output", default=".codex/reports/v29-performance-comparison.json")
    compare.set_defaults(func=command_compare)
    report = sub.add_parser("report", help="Combine existing V29 audit and comparison reports.")
    report.add_argument("--root", required=True)
    report.add_argument("--audit")
    report.add_argument("--comparison")
    report.add_argument("--output", default=".codex/reports/v29-performance-report.json")
    report.set_defaults(func=command_report)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
