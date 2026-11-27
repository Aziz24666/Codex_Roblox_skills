#!/usr/bin/env python3
"""Offline V34 validators and trend/comparison tools for Roblox performance evidence."""
from __future__ import annotations

import argparse
import json
import math
import shutil
import statistics
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "34.0.0"
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_SAMPLES = 250
MAX_CAPTURES_PER_BUILD = 8
SCENARIOS = {
    "idle_server_soak", "steady_gameplay", "high_activity", "join_leave_churn",
    "asset_streaming", "spawn_respawn", "round_transition",
}
TARGETS = {"server", "client"}
DEVICE_PROFILES = {"server", "low_end_mobile", "high_end_mobile", "desktop"}
SOURCES = {"microprofiler", "script_profiler", "developer_console", "performance_dashboard", "custom_harness"}
NETWORK_PROFILES = {"baseline", "high_latency", "jitter", "packet_loss"}
METRICS = {
    "server_memory_mb", "lua_heap_mb", "instance_count", "script_cpu_ms_per_frame",
    "server_cpu_ms_per_frame", "server_heartbeat_fps", "client_frame_time_ms_p95",
    "client_memory_mb", "join_time_s", "replication_kbps",
}
TREND_METRICS = {"server_memory_mb", "lua_heap_mb", "instance_count"}
HIGHER_WORSE = {
    "server_memory_mb", "lua_heap_mb", "instance_count", "script_cpu_ms_per_frame",
    "server_cpu_ms_per_frame", "client_frame_time_ms_p95", "client_memory_mb", "join_time_s",
}
LOWER_WORSE = {"server_heartbeat_fps"}
CAPTURE_FIELDS = {
    "schema_version", "run_id", "build_id", "scenario", "target", "device_profile",
    "measurement_source", "network_profile", "player_count", "started_at",
    "warmup_minutes", "duration_minutes", "sample_interval_seconds", "evidence_ref", "samples",
}
SUITE_FIELDS = {
    "schema_version", "suite_id", "scenario", "target", "device_profile",
    "measurement_source", "network_profile", "player_count", "duration_minutes",
    "sample_interval_seconds", "baseline_build", "candidate_build", "threshold_pct",
    "baseline_captures", "candidate_captures",
}
SAMPLE_FIELDS = {"elapsed_seconds", "server_age_minutes", "connected_clients", "metrics"}
RUN_ID_PREFIX = "perf-run-"
SUITE_ID_PREFIX = "perf-suite-"
EVIDENCE_PREFIX = "ev-"


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_project_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw.strip() or "\x00" in raw:
        raise ValueError("Project-relative path must be a non-empty string.")
    if "\\" in raw or raw.startswith("/") or len(raw) > 240:
        raise ValueError("Path must be project-relative, bounded, and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Path must remain inside the selected project root.")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Path cannot traverse a symlink.")
    candidate = root.joinpath(*parts)
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Path resolves outside the selected project root or does not exist.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Path must identify an existing regular file.")
    return resolved


def safe_output_path(root: Path, raw: str) -> Path:
    target = safe_project_path(root, raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve(strict=True)
    if not parent.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Output directory resolves outside the selected project root.")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise ValueError("Output path must be a regular file and cannot replace a symlink.")
    return parent / target.name


def write_json(path: Path, value: dict[str, Any]) -> None:
    text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", closefd=True) as stream:
            stream.write(text)
            stream.flush()
        Path(temporary).replace(path)
    finally:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass


def reject_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON numeric constant: {value}")


def load_json(root: Path, raw: str) -> tuple[Path, Any]:
    path = safe_project_path(root, raw, must_exist=True)
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError(f"{path.relative_to(root)} exceeds the {MAX_JSON_BYTES}-byte JSON limit.")
        data = json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path.relative_to(root)}: {exc}") from exc
    return path, data


def finite_number(value: Any, *, positive: bool = False) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and (float(value) > 0 if positive else float(value) >= 0)
    )


def valid_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def valid_token(value: Any, prefix: str, minimum: int = 8, maximum: int = 24) -> bool:
    if not isinstance(value, str) or not value.startswith(prefix):
        return False
    tail = value[len(prefix):]
    return minimum <= len(tail) <= maximum and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789" for ch in tail)


def valid_build_id(value: Any) -> bool:
    if not isinstance(value, str) or not 1 <= len(value) <= 120:
        return False
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:+/-"
    return all(ch in allowed for ch in value)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def validate_capture(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Capture must be a JSON object."]
    if set(data) != CAPTURE_FIELDS:
        if CAPTURE_FIELDS - set(data):
            errors.append("Capture is missing required fields.")
        if set(data) - CAPTURE_FIELDS:
            errors.append("Capture contains unsupported fields; do not add player identity, raw logs, or free text.")
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        errors.append("schema_version must equal integer 1.")
    if not valid_token(data.get("run_id"), RUN_ID_PREFIX):
        errors.append("run_id must be an opaque perf-run- reference with 8-24 lowercase letters or digits.")
    if not valid_build_id(data.get("build_id")):
        errors.append("build_id must be a bounded build/revision token using letters, digits, dot, underscore, colon, plus, slash, or hyphen.")
    for field, allowed in (
        ("scenario", SCENARIOS), ("target", TARGETS), ("device_profile", DEVICE_PROFILES),
        ("measurement_source", SOURCES), ("network_profile", NETWORK_PROFILES),
    ):
        value = data.get(field)
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"{field} is not a supported fixed code.")
    target = data.get("target")
    profile = data.get("device_profile")
    if target == "server" and profile != "server":
        errors.append("A server-target capture must use device_profile server.")
    if target == "client" and profile not in {"low_end_mobile", "high_end_mobile", "desktop"}:
        errors.append("A client-target capture must use a supported client device profile.")
    if not valid_int(data.get("player_count"), 1, 100):
        errors.append("player_count must be an integer from 1 to 100.")
    if parse_timestamp(data.get("started_at")) is None:
        errors.append("started_at must be an ISO-8601 timestamp with a timezone.")
    if not valid_int(data.get("warmup_minutes"), 0, 60):
        errors.append("warmup_minutes must be an integer from 0 to 60.")
    if not valid_int(data.get("duration_minutes"), 30, 1440):
        errors.append("duration_minutes must be an integer from 30 to 1440.")
    if not valid_int(data.get("sample_interval_seconds"), 30, 3600):
        errors.append("sample_interval_seconds must be an integer from 30 to 3600.")
    if not valid_token(data.get("evidence_ref"), EVIDENCE_PREFIX, 12, 12):
        errors.append("evidence_ref must be an opaque ev- reference with exactly 12 lowercase letters or digits.")

    samples = data.get("samples")
    if not isinstance(samples, list) or not 5 <= len(samples) <= MAX_SAMPLES:
        errors.append(f"samples must contain 5-{MAX_SAMPLES} entries.")
        return errors

    metric_keys: set[str] | None = None
    previous_elapsed: float | None = None
    previous_age: float | None = None
    elapsed_values: list[float] = []
    client_counts: list[int] = []
    interval = data.get("sample_interval_seconds")
    duration = data.get("duration_minutes")
    player_count = data.get("player_count")
    for index, sample in enumerate(samples):
        prefix = f"samples[{index}]"
        if not isinstance(sample, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        if set(sample) != SAMPLE_FIELDS:
            errors.append(f"{prefix} must contain exactly the documented fields.")
        elapsed = sample.get("elapsed_seconds")
        age = sample.get("server_age_minutes")
        clients = sample.get("connected_clients")
        if not finite_number(elapsed):
            errors.append(f"{prefix}.elapsed_seconds must be a finite non-negative number.")
        else:
            elapsed_float = float(elapsed)
            elapsed_values.append(elapsed_float)
            if previous_elapsed is not None:
                delta = elapsed_float - previous_elapsed
                if delta <= 0:
                    errors.append(f"{prefix}.elapsed_seconds must increase strictly.")
                elif valid_int(interval, 30, 3600) and abs(delta - interval) > max(15.0, interval * 0.4):
                    errors.append(f"{prefix}.elapsed_seconds is too far from the declared sample interval.")
            previous_elapsed = elapsed_float
            if valid_int(duration, 30, 1440) and elapsed_float > duration * 60 * 1.1:
                errors.append(f"{prefix}.elapsed_seconds exceeds the declared duration tolerance.")
        if not finite_number(age):
            errors.append(f"{prefix}.server_age_minutes must be a finite non-negative number.")
        else:
            age_float = float(age)
            if previous_age is not None and age_float <= previous_age:
                errors.append(f"{prefix}.server_age_minutes must increase strictly.")
            previous_age = age_float
        if not valid_int(clients, 0, 100):
            errors.append(f"{prefix}.connected_clients must be an integer from 0 to 100.")
        else:
            client_counts.append(clients)
            if valid_int(player_count, 1, 100) and clients > player_count:
                errors.append(f"{prefix}.connected_clients cannot exceed the planned player_count.")
        metrics = sample.get("metrics")
        if not isinstance(metrics, dict) or not metrics:
            errors.append(f"{prefix}.metrics must be a non-empty object.")
            continue
        unknown = set(metrics) - METRICS
        if unknown:
            errors.append(f"{prefix}.metrics contains unsupported metric names.")
        current_keys = set(metrics)
        if metric_keys is None:
            metric_keys = current_keys
        elif current_keys != metric_keys:
            errors.append("Every sample must contain the same metric set.")
        for name, value in metrics.items():
            if name not in METRICS:
                continue
            if name == "instance_count":
                if not valid_int(value, 0, 2_000_000_000):
                    errors.append(f"{prefix}.metrics.instance_count must be a non-negative integer.")
            elif not finite_number(value, positive=name in {"server_heartbeat_fps", "client_frame_time_ms_p95", "join_time_s"}):
                errors.append(f"{prefix}.metrics.{name} must be a finite non-negative number.")

    if metric_keys:
        if target == "server" and not metric_keys.intersection({"server_memory_mb", "lua_heap_mb", "instance_count", "server_cpu_ms_per_frame", "server_heartbeat_fps"}):
            errors.append("Server captures must include at least one server-side metric.")
        if target == "client" and not metric_keys.intersection({"client_frame_time_ms_p95", "client_memory_mb", "join_time_s", "replication_kbps"}):
            errors.append("Client captures must include at least one client-side metric.")
    if elapsed_values and valid_int(duration, 30, 1440):
        if elapsed_values[0] > (interval if valid_int(interval, 30, 3600) else 0):
            errors.append("The first sample must begin within one declared sample interval.")
        if elapsed_values[-1] < duration * 60 * 0.75:
            errors.append("Samples must cover at least 75% of the declared measured duration.")
    return errors


def validate_suite(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Repeat suite manifest must be a JSON object."]
    if set(data) != SUITE_FIELDS:
        if SUITE_FIELDS - set(data):
            errors.append("Repeat suite manifest is missing required fields.")
        if set(data) - SUITE_FIELDS:
            errors.append("Repeat suite manifest contains unsupported fields.")
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        errors.append("schema_version must equal integer 1.")
    if not valid_token(data.get("suite_id"), SUITE_ID_PREFIX):
        errors.append("suite_id must be an opaque perf-suite- reference.")
    for field, allowed in (
        ("scenario", SCENARIOS), ("target", TARGETS), ("device_profile", DEVICE_PROFILES),
        ("measurement_source", SOURCES), ("network_profile", NETWORK_PROFILES),
    ):
        value = data.get(field)
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"{field} is not a supported fixed code.")
    if data.get("target") == "server" and data.get("device_profile") != "server":
        errors.append("A server-target suite must use device_profile server.")
    if data.get("target") == "client" and data.get("device_profile") not in {"low_end_mobile", "high_end_mobile", "desktop"}:
        errors.append("A client-target suite must use a supported client device profile.")
    if not valid_int(data.get("player_count"), 1, 100):
        errors.append("player_count must be an integer from 1 to 100.")
    if not valid_int(data.get("duration_minutes"), 30, 1440):
        errors.append("duration_minutes must be an integer from 30 to 1440.")
    if not valid_int(data.get("sample_interval_seconds"), 30, 3600):
        errors.append("sample_interval_seconds must be an integer from 30 to 3600.")
    baseline_build = data.get("baseline_build")
    candidate_build = data.get("candidate_build")
    if not valid_build_id(baseline_build) or not valid_build_id(candidate_build):
        errors.append("baseline_build and candidate_build must be valid build identifiers.")
    elif baseline_build == candidate_build:
        errors.append("baseline_build and candidate_build must differ.")
    threshold = data.get("threshold_pct")
    if not finite_number(threshold, positive=True) or float(threshold) > 100:
        errors.append("threshold_pct must be greater than 0 and no more than 100.")
    all_paths: list[str] = []
    for field in ("baseline_captures", "candidate_captures"):
        paths = data.get(field)
        if not isinstance(paths, list) or not 3 <= len(paths) <= MAX_CAPTURES_PER_BUILD:
            errors.append(f"{field} must contain 3-{MAX_CAPTURES_PER_BUILD} project-relative capture paths.")
            continue
        if any(not isinstance(path, str) or not path.strip() for path in paths):
            errors.append(f"{field} must contain non-empty path strings.")
            continue
        if len(paths) != len(set(paths)):
            errors.append(f"{field} must not contain duplicate capture paths.")
        all_paths.extend(paths)
    if len(all_paths) != len(set(all_paths)):
        errors.append("Baseline and candidate capture paths must be distinct.")
    return errors


def linear_trend(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("A trend needs at least two paired samples.")
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator <= 0:
        raise ValueError("Trend samples must span a positive time range.")
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    intercept = mean_y - slope * mean_x
    residual = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    total = sum((y - mean_y) ** 2 for y in ys)
    if total <= 1e-12:
        r_squared = 1.0 if residual <= 1e-12 else 0.0
    else:
        r_squared = max(0.0, min(1.0, 1.0 - residual / total))
    return slope, intercept, r_squared


def analyze_soak(capture: dict[str, Any], growth_threshold_pct: float = 8.0,
                 min_r_squared: float = 0.7, max_client_variance: int = 1) -> dict[str, Any]:
    if not finite_number(growth_threshold_pct, positive=True) or growth_threshold_pct > 100:
        raise ValueError("growth_threshold_pct must be greater than 0 and no more than 100.")
    if not finite_number(min_r_squared) or not 0 <= min_r_squared <= 1:
        raise ValueError("min_r_squared must be between 0 and 1.")
    if not valid_int(max_client_variance, 0, 100):
        raise ValueError("max_client_variance must be an integer from 0 to 100.")
    samples = capture["samples"]
    client_counts = [item["connected_clients"] for item in samples]
    load_stable = max(client_counts) - min(client_counts) <= max_client_variance
    metrics = set.intersection(*(set(item["metrics"]) for item in samples))
    trend_names = sorted(metrics & TREND_METRICS)
    if not trend_names:
        raise ValueError("Capture contains no supported memory/instance metric for soak analysis.")
    xs = [float(item["server_age_minutes"]) / 60.0 for item in samples]
    results: list[dict[str, Any]] = []
    for name in trend_names:
        ys = [float(item["metrics"][name]) for item in samples]
        slope, intercept, r_squared = linear_trend(xs, ys)
        first = ys[0]
        last = ys[-1]
        delta = last - first
        delta_pct = (delta / first * 100.0) if first > 0 else None
        signal = (
            load_stable and slope > 0 and delta_pct is not None
            and delta_pct >= growth_threshold_pct and r_squared >= min_r_squared
        )
        results.append({
            "metric": name,
            "first_value": first,
            "last_value": last,
            "delta": delta,
            "delta_pct": round(delta_pct, 4) if delta_pct is not None else None,
            "slope_per_server_hour": round(slope, 6),
            "r_squared": round(r_squared, 4),
            "growth_signal": bool(signal),
            "interpretation": "growth_signal_review_required" if signal else (
                "load_unstable_no_growth_verdict" if not load_stable else "no_thresholded_growth_signal"
            ),
        })
    return {
        "report_type": "v34_performance_soak_analysis",
        "schema_version": 1,
        "version": VERSION,
        "run_id": capture["run_id"],
        "build_id": capture["build_id"],
        "scenario": capture["scenario"],
        "target": capture["target"],
        "device_profile": capture["device_profile"],
        "measurement_source": capture["measurement_source"],
        "sample_count": len(samples),
        "server_age_span_minutes": round(samples[-1]["server_age_minutes"] - samples[0]["server_age_minutes"], 4),
        "connected_clients": {
            "minimum": min(client_counts),
            "maximum": max(client_counts),
            "range": max(client_counts) - min(client_counts),
            "stable_within_tolerance": load_stable,
        },
        "thresholds": {
            "growth_threshold_pct": float(growth_threshold_pct),
            "min_r_squared": float(min_r_squared),
            "max_client_variance": max_client_variance,
        },
        "metrics": results,
        "growth_signal_count": sum(1 for item in results if item["growth_signal"]),
        "execution_status": "offline_analysis_of_supplied_capture",
        "limitations": [
            "This is a simple linear trend on supplied samples, not a memory-leak proof or root-cause diagnosis.",
            "Changing player count, workload, server configuration, or measurement method can confound a trend.",
            "R-squared and percentage thresholds are review heuristics, not a statistical significance test.",
            "Confirm a growth signal with repeated runs and Roblox Developer Console memory categories.",
            "V34 does not access live telemetry, Roblox Studio, Creator Dashboard, or proprietary profiler dump files.",
        ],
    }


def capture_profile(capture: dict[str, Any]) -> tuple[Any, ...]:
    return (
        capture["scenario"], capture["target"], capture["device_profile"],
        capture["measurement_source"], capture["network_profile"], capture["player_count"],
        capture["duration_minutes"], capture["sample_interval_seconds"], capture["warmup_minutes"],
    )


def load_suite(root: Path, manifest_path: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    _, manifest = load_json(root, manifest_path)
    errors = validate_suite(manifest)
    if errors:
        return {}, [], [], errors
    baseline: list[dict[str, Any]] = []
    candidate: list[dict[str, Any]] = []
    for side, paths, expected_build, target_list in (
        ("baseline", manifest["baseline_captures"], manifest["baseline_build"], baseline),
        ("candidate", manifest["candidate_captures"], manifest["candidate_build"], candidate),
    ):
        for raw_path in paths:
            try:
                path, capture = load_json(root, raw_path)
            except (OSError, ValueError) as exc:
                errors.append(f"{side} capture {raw_path!r}: {exc}")
                continue
            problems = validate_capture(capture)
            if problems:
                errors.extend(f"{side} capture {raw_path!r}: {item}" for item in problems)
                continue
            if capture["build_id"] != expected_build:
                errors.append(f"{side} capture {raw_path!r} does not match the declared {side}_build.")
                continue
            expected_profile = (
                manifest["scenario"], manifest["target"], manifest["device_profile"],
                manifest["measurement_source"], manifest["network_profile"], manifest["player_count"],
                manifest["duration_minutes"], manifest["sample_interval_seconds"],
            )
            actual_profile = (
                capture["scenario"], capture["target"], capture["device_profile"],
                capture["measurement_source"], capture["network_profile"], capture["player_count"],
                capture["duration_minutes"], capture["sample_interval_seconds"],
            )
            if actual_profile != expected_profile:
                errors.append(f"{side} capture {raw_path!r} does not match the repeat suite environment.")
                continue
            target_list.append(capture)
    for side, captures in (("baseline", baseline), ("candidate", candidate)):
        run_ids = [item["run_id"] for item in captures]
        if len(run_ids) != len(set(run_ids)):
            errors.append(f"{side} captures contain duplicate run IDs.")
    if not errors and baseline and candidate:
        if len({item["warmup_minutes"] for item in baseline + candidate}) > 1:
            errors.append("All baseline and candidate captures must use the same warmup_minutes.")
    return manifest, baseline, candidate, errors


def compare_repeated(manifest: dict[str, Any], baseline: list[dict[str, Any]],
                     candidate: list[dict[str, Any]]) -> dict[str, Any]:
    all_capture_metric_sets = [
        set.intersection(*(set(sample["metrics"]) for sample in capture["samples"]))
        for capture in baseline + candidate
    ]
    common = set.intersection(*all_capture_metric_sets) if all_capture_metric_sets else set()
    if not common:
        raise ValueError("Baseline and candidate captures have no common consistently measured metrics.")
    metrics_out: list[dict[str, Any]] = []
    regression_count = 0
    for name in sorted(common):
        baseline_run_values = [
            statistics.median(float(sample["metrics"][name]) for sample in capture["samples"])
            for capture in baseline
        ]
        candidate_run_values = [
            statistics.median(float(sample["metrics"][name]) for sample in capture["samples"])
            for capture in candidate
        ]
        before = float(statistics.median(baseline_run_values))
        after = float(statistics.median(candidate_run_values))
        delta_pct = (after - before) / before * 100.0 if before != 0 else None
        direction = "higher_is_worse" if name in HIGHER_WORSE else (
            "lower_is_worse" if name in LOWER_WORSE else "context_only"
        )
        regression = None
        if delta_pct is not None and direction == "higher_is_worse":
            regression = delta_pct >= float(manifest["threshold_pct"])
        elif delta_pct is not None and direction == "lower_is_worse":
            regression = delta_pct <= -float(manifest["threshold_pct"])
        if regression:
            regression_count += 1
        metrics_out.append({
            "metric": name,
            "direction": direction,
            "baseline_median_of_runs": round(before, 6),
            "candidate_median_of_runs": round(after, 6),
            "delta_pct": round(delta_pct, 4) if delta_pct is not None else None,
            "threshold_pct": float(manifest["threshold_pct"]),
            "regression": regression,
            "baseline_run_medians": [round(value, 6) for value in baseline_run_values],
            "candidate_run_medians": [round(value, 6) for value in candidate_run_values],
        })
    return {
        "report_type": "v34_repeated_performance_comparison",
        "schema_version": 1,
        "version": VERSION,
        "suite_id": manifest["suite_id"],
        "scenario": manifest["scenario"],
        "target": manifest["target"],
        "device_profile": manifest["device_profile"],
        "measurement_source": manifest["measurement_source"],
        "network_profile": manifest["network_profile"],
        "baseline_build": manifest["baseline_build"],
        "candidate_build": manifest["candidate_build"],
        "baseline_runs": len(baseline),
        "candidate_runs": len(candidate),
        "threshold_pct": float(manifest["threshold_pct"]),
        "metrics": metrics_out,
        "regression_count": regression_count,
        "gate_status": "review_required" if regression_count else "no_thresholded_regression_detected",
        "execution_status": "offline_comparison_of_supplied_captures",
        "limitations": [
            "Each capture is aggregated by its sample median, then cohorts are compared using the median across runs.",
            "This is not a formal statistical significance test; review run-level values and measurement noise.",
            "A neutral/context metric is displayed but not assigned a universal regression direction.",
            "The report cannot authenticate that a supplied capture came from Roblox Studio or a live experience.",
            "A passing comparison does not prove performance is good; apply project-specific budgets and player-impact review.",
        ],
    }


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    print(f"Project: {root}")
    print("Optional local tools:")
    for executable in ("git", "rojo", "luau-analyze", "selene"):
        print(f"  {executable}: {shutil.which(executable) or 'not found on PATH'}")
    print("V34 only validates project-local JSON evidence; no Studio or Roblox service is contacted.")
    return 0


def command_validate_capture(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    path, capture = load_json(root, args.capture)
    errors = validate_capture(capture)
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: capture {capture['run_id']} ({path.relative_to(root)}) with {len(capture['samples'])} samples.")
    print("Structural validation only; evidence provenance and actual Studio execution are not authenticated.")
    return 0


def command_analyze_soak(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    _, capture = load_json(root, args.capture)
    errors = validate_capture(capture)
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        return 1
    report = analyze_soak(capture, args.growth_threshold_pct, args.min_r_squared, args.max_client_variance)
    output = safe_output_path(root, args.output)
    write_json(output, report)
    print(f"PASS: soak analysis written to {output}.")
    print(f"Growth signals requiring review: {report['growth_signal_count']}.")
    print("A growth signal is not proof of a memory leak.")
    return 0


def command_validate_suite(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    manifest, baseline, candidate, errors = load_suite(root, args.manifest)
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: suite {manifest['suite_id']} matched {len(baseline)} baseline and "
        f"{len(candidate)} candidate captures."
    )
    print("All runs use the manifest environment; capture provenance remains externally supplied.")
    return 0


def command_compare_repeated(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    manifest, baseline, candidate, errors = load_suite(root, args.manifest)
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        return 1
    try:
        report = compare_repeated(manifest, baseline, candidate)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    output = safe_output_path(root, args.output)
    write_json(output, report)
    print(f"PASS: repeated comparison written to {output}.")
    print(f"Thresholded regressions: {report['regression_count']}.")
    if args.fail_on_regression and report["regression_count"]:
        return 3
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Inspect local tools and project root.")
    doctor.add_argument("--root", required=True)
    doctor.set_defaults(func=command_doctor)
    capture = sub.add_parser("validate-capture", help="Validate one time-series performance capture.")
    capture.add_argument("--root", required=True)
    capture.add_argument("--capture", required=True)
    capture.set_defaults(func=command_validate_capture)
    soak = sub.add_parser("analyze-soak", help="Analyze resource trends during a long-session capture.")
    soak.add_argument("--root", required=True)
    soak.add_argument("--capture", required=True)
    soak.add_argument("--output", default=".codex/reports/v34-soak-analysis.json")
    soak.add_argument("--growth-threshold-pct", type=float, default=8.0)
    soak.add_argument("--min-r-squared", type=float, default=0.7)
    soak.add_argument("--max-client-variance", type=int, default=1)
    soak.set_defaults(func=command_analyze_soak)
    suite = sub.add_parser("validate-suite", help="Validate a repeat manifest and its capture files.")
    suite.add_argument("--root", required=True)
    suite.add_argument("--manifest", required=True)
    suite.set_defaults(func=command_validate_suite)
    compare = sub.add_parser("compare-repeated", help="Compare at least three repeated runs per build.")
    compare.add_argument("--root", required=True)
    compare.add_argument("--manifest", required=True)
    compare.add_argument("--output", default=".codex/reports/v34-repeated-comparison.json")
    compare.add_argument("--fail-on-regression", action="store_true")
    compare.set_defaults(func=command_compare_repeated)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
