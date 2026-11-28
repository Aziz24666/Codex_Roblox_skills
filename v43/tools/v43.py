#!/usr/bin/env python3
"""Offline planner, validator, auditor, comparator, and decision reviewer for Roblox experiments."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "43.0.0"
MAX_INPUT_BYTES = 1024 * 1024
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
CONFIG_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,255}$")
EVENT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")

TOP_FIELDS = {
    "schema_version", "experiment_id", "name", "hypothesis", "product_type",
    "config", "duration_days", "exposure_percent", "variants", "metrics",
    "instrumentation", "quality_gates", "operations",
}
HYPOTHESIS_FIELDS = {"change", "expected_outcome", "rationale", "success_criteria"}
CONFIG_FIELDS = {"repository", "key", "value_type", "control_value"}
VARIANT_FIELDS = {"variant_id", "label", "is_baseline", "weight_percent", "value"}
METRIC_FIELDS = {"goal_metric", "goal_direction", "learning_metrics", "custom_metrics"}
CUSTOM_METRIC_FIELDS = {"metric_id", "source", "source_name", "calculation", "completion_step"}
INSTRUMENTATION_FIELDS = {"events", "max_custom_event_names", "custom_fields_reviewed"}
EVENT_FIELDS = {
    "event_name", "event_type", "server_only", "published_game_only",
    "privacy_reviewed", "cardinality_reviewed",
}
QUALITY_GATE_FIELDS = {
    "hypothesis_reviewed", "sample_feasibility_reviewed", "mde_reviewed",
    "targeting_and_assignment_reviewed", "instrumentation_preexisting",
    "interaction_reviewed", "no_mid_experiment_changes",
    "srm_monitoring_enabled", "critical_harm_stop_review_enabled",
    "no_early_success_stop", "human_decision_required",
}
OPERATION_FIELDS = {
    "read_scope_reviewed", "write_scope_reviewed", "credentials_outside_repository",
    "asynchronous_operation_polling", "write_requires_human_approval",
}
VALUE_TYPES = {"boolean", "number", "string", "json"}
PLATFORM_METRICS = {
    "D1_RETENTION", "D7_RETENTION", "PLAYTIME", "ARPU", "ARPPU",
    "PAYER_CONVERSION_RATE", "SESSION_TIME",
}
CUSTOM_SOURCES = {"custom", "economy", "funnel"}
CUSTOM_CALCULATIONS = {
    "AVERAGE_CUSTOM_VALUE", "AVERAGE_CUSTOM_VALUE_OVER_ALL_USERS", "PARTICIPATION_PERCENT",
    "AVERAGE_NET_CURRENCY_DELTA", "AVERAGE_CURRENCY_SOURCE_DELTA", "AVERAGE_CURRENCY_SINK_DELTA",
    "PER_USER_FUNNEL_CONVERSION", "PER_INSTANCE_FUNNEL_CONVERSION",
}
RESULT_FIELDS = {
    "schema_version", "experiment_id", "experiment_state", "observed_at",
    "elapsed_days", "srm_detected", "critical_harm_flag",
    "variant_enrolled_users", "treatment_results",
}
TREATMENT_RESULT_FIELDS = {
    "variant_id", "goal_metric_delta_percent", "confidence_interval_low_percent",
    "confidence_interval_high_percent", "guardrails",
}
GUARDRAIL_FIELDS = {
    "metric_id", "delta_percent", "confidence_interval_low_percent",
    "confidence_interval_high_percent", "harmful_direction",
}
RESULT_STATES = {"DRAFT", "SCHEDULED", "RUNNING", "DECISION_NEEDED", "COMPLETED"}


def allowed(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def is_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value))


def check_fields(value: dict, expected: set[str], label: str) -> list[str]:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    errors = []
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{label} contains unsupported fields: {', '.join(extra)}.")
    return errors


def value_matches_type(value: Any, value_type: str) -> bool:
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "number":
        return is_number(value)
    if value_type == "string":
        return isinstance(value, str)
    if value_type == "json":
        return isinstance(value, dict)
    return False


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be an ISO 8601 timestamp with an explicit UTC offset.")
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


def validate_manifest(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Experiment manifest must be a JSON object."]
    errors += check_fields(data, TOP_FIELDS, "manifest")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        errors.append("schema_version must be integer 1.")
    if not is_slug(data.get("experiment_id")):
        errors.append("experiment_id must be a lowercase slug (2-40 characters).")
    if not isinstance(data.get("name"), str) or not 1 <= len(data["name"]) <= 100:
        errors.append("name must contain 1-100 characters.")
    if data.get("product_type") != "in_game_config":
        errors.append("product_type must be in_game_config; this toolkit models Roblox in-experience config experiments only.")

    hypothesis = data.get("hypothesis")
    if not isinstance(hypothesis, dict):
        errors.append("hypothesis must be an object.")
        hypothesis = {}
    else:
        errors += check_fields(hypothesis, HYPOTHESIS_FIELDS, "hypothesis")
        for field in HYPOTHESIS_FIELDS:
            value = hypothesis.get(field)
            if not isinstance(value, str) or not 12 <= len(value.strip()) <= 500:
                errors.append(f"hypothesis.{field} must contain 12-500 non-whitespace characters.")

    config = data.get("config")
    if not isinstance(config, dict):
        errors.append("config must be an object.")
        config = {}
    else:
        errors += check_fields(config, CONFIG_FIELDS, "config")
        if config.get("repository") != "InExperienceConfig":
            errors.append("config.repository must be InExperienceConfig.")
        if not isinstance(config.get("key"), str) or not CONFIG_KEY.fullmatch(config["key"]):
            errors.append("config.key must be 1-256 characters, start with a letter, and use only letters, digits, underscore, dot, or hyphen.")
        value_type = config.get("value_type")
        if not allowed(value_type, VALUE_TYPES):
            errors.append("config.value_type must be boolean, number, string, or json.")
        elif "control_value" in config and not value_matches_type(config["control_value"], value_type):
            errors.append("config.control_value does not match config.value_type.")

    duration = data.get("duration_days")
    if not is_int(duration, 14, 60):
        errors.append("duration_days must be an integer from 14 to 60 (Roblox Experiments limit).")
    exposure = data.get("exposure_percent")
    if not is_int(exposure, 1, 100):
        errors.append("exposure_percent must be an integer from 1 to 100.")

    variants = data.get("variants")
    variant_map: dict[str, dict] = {}
    if not isinstance(variants, list) or not 2 <= len(variants) <= 3:
        errors.append("variants must contain one baseline and one or two treatment variants.")
        variants = []
    baseline_count = 0
    weight_total = 0
    labels: set[str] = set()
    for index, item in enumerate(variants):
        label = f"variants[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, VARIANT_FIELDS, label)
        variant_id = item.get("variant_id")
        if not is_slug(variant_id):
            errors.append(f"{label}.variant_id must be a lowercase slug.")
        elif variant_id in variant_map:
            errors.append(f"Duplicate variant_id: {variant_id}.")
        else:
            variant_map[variant_id] = item
        variant_label = item.get("label")
        if not isinstance(variant_label, str) or not 1 <= len(variant_label.strip()) <= 60:
            errors.append(f"{label}.label must contain 1-60 non-whitespace characters.")
        elif variant_label.casefold() in labels:
            errors.append(f"Duplicate variant label: {variant_label}.")
        else:
            labels.add(variant_label.casefold())
        if not isinstance(item.get("is_baseline"), bool):
            errors.append(f"{label}.is_baseline must be boolean.")
        elif item["is_baseline"]:
            baseline_count += 1
        weight = item.get("weight_percent")
        if not is_int(weight, 1, 100):
            errors.append(f"{label}.weight_percent must be an integer from 1 to 100.")
        else:
            weight_total += weight
        value_type = config.get("value_type")
        if allowed(value_type, VALUE_TYPES) and "value" in item and not value_matches_type(item["value"], value_type):
            errors.append(f"{label}.value does not match config.value_type.")
    if variants:
        if baseline_count != 1:
            errors.append("Exactly one variant must have is_baseline=true.")
        if weight_total != 100:
            errors.append(f"Variant weight_percent values must sum to 100; found {weight_total}.")
        baselines = [item for item in variants if isinstance(item, dict) and item.get("is_baseline") is True]
        if len(baselines) == 1 and "control_value" in config and baselines[0].get("value") != config.get("control_value"):
            errors.append("Baseline variant value must equal config.control_value.")

    metrics = data.get("metrics")
    metric_ids: set[str] = set()
    event_names: set[str] = set()
    if not isinstance(metrics, dict):
        errors.append("metrics must be an object.")
        metrics = {}
    else:
        errors += check_fields(metrics, METRIC_FIELDS, "metrics")
        if not allowed(metrics.get("goal_direction"), {"increase", "decrease"}):
            errors.append("metrics.goal_direction must be increase or decrease.")
        custom = metrics.get("custom_metrics")
        if not isinstance(custom, list) or len(custom) > 3:
            errors.append("metrics.custom_metrics must contain at most 3 custom metrics (Roblox Experiments limit).")
            custom = []
        for index, item in enumerate(custom):
            label = f"metrics.custom_metrics[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            errors += check_fields(item, CUSTOM_METRIC_FIELDS, label)
            metric_id = item.get("metric_id")
            if not is_slug(metric_id):
                errors.append(f"{label}.metric_id must be a lowercase slug.")
            elif metric_id in metric_ids:
                errors.append(f"Duplicate custom metric_id: {metric_id}.")
            else:
                metric_ids.add(metric_id)
            source = item.get("source")
            if not allowed(source, CUSTOM_SOURCES):
                errors.append(f"{label}.source must be custom, economy, or funnel.")
            source_name = item.get("source_name")
            if not isinstance(source_name, str) or not 1 <= len(source_name.strip()) <= 100:
                errors.append(f"{label}.source_name must contain 1-100 non-whitespace characters.")
            elif source == "custom":
                if not EVENT_NAME.fullmatch(source_name):
                    errors.append(f"{label}.source_name must be a valid AnalyticsService event name for custom source.")
                else:
                    event_names.add(source_name)
            step = item.get("completion_step")
            if source == "funnel":
                if not is_int(step, 1, 100):
                    errors.append(f"{label}.completion_step must be an integer from 1 to 100 for funnel metrics.")
            elif step is not None:
                errors.append(f"{label}.completion_step must be null for custom and economy metrics.")
            calculation = item.get("calculation")
            if not allowed(calculation, CUSTOM_CALCULATIONS):
                errors.append(f"{label}.calculation must be one of {', '.join(sorted(CUSTOM_CALCULATIONS))}.")
            elif source == "custom" and calculation not in {
                "AVERAGE_CUSTOM_VALUE", "AVERAGE_CUSTOM_VALUE_OVER_ALL_USERS", "PARTICIPATION_PERCENT"
            }:
                errors.append(f"{label}.calculation is not supported for custom-event metrics.")
            elif source == "economy" and calculation not in {
                "AVERAGE_NET_CURRENCY_DELTA", "AVERAGE_CURRENCY_SOURCE_DELTA", "AVERAGE_CURRENCY_SINK_DELTA"
            }:
                errors.append(f"{label}.calculation is not supported for economy metrics.")
            elif source == "funnel" and calculation not in {
                "PER_USER_FUNNEL_CONVERSION", "PER_INSTANCE_FUNNEL_CONVERSION"
            }:
                errors.append(f"{label}.calculation is not supported for funnel metrics.")
        def metric_ref_is_valid(value: Any) -> bool:
            if allowed(value, PLATFORM_METRICS):
                return True
            return isinstance(value, str) and value.startswith("custom:") and value[7:] in metric_ids
        if not metric_ref_is_valid(metrics.get("goal_metric")):
            errors.append(f"metrics.goal_metric must be a supported platform metric or custom:<metric_id> referencing a declared custom metric.")
        learning = metrics.get("learning_metrics")
        if not isinstance(learning, list) or len(learning) > 7 or not all(metric_ref_is_valid(x) for x in learning):
            errors.append("metrics.learning_metrics must contain at most 7 supported platform or declared custom metrics.")
        elif metrics.get("goal_metric") in learning or len(set(learning)) != len(learning):
            errors.append("metrics.learning_metrics must be unique and must not repeat the goal metric.")

    instrumentation = data.get("instrumentation")
    if not isinstance(instrumentation, dict):
        errors.append("instrumentation must be an object.")
        instrumentation = {}
    else:
        errors += check_fields(instrumentation, INSTRUMENTATION_FIELDS, "instrumentation")
        if instrumentation.get("max_custom_event_names") != 100:
            errors.append("instrumentation.max_custom_event_names must be 100 (documented Roblox custom-event limit).")
        if instrumentation.get("custom_fields_reviewed") is not True:
            errors.append("instrumentation.custom_fields_reviewed must be true.")
        events = instrumentation.get("events")
        if not isinstance(events, list) or len(events) < len(event_names) or len(events) > 100:
            errors.append("instrumentation.events must declare all custom-metric events and contain 0-100 event contracts.")
            events = []
        event_map: dict[str, dict] = {}
        for index, item in enumerate(events):
            label = f"instrumentation.events[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            errors += check_fields(item, EVENT_FIELDS, label)
            name = item.get("event_name")
            if not isinstance(name, str) or not EVENT_NAME.fullmatch(name):
                errors.append(f"{label}.event_name must be a valid 1-64 character event name.")
            elif name in event_map:
                errors.append(f"Duplicate instrumentation event_name: {name}.")
            else:
                event_map[name] = item
            if not allowed(item.get("event_type"), {"counter", "value"}):
                errors.append(f"{label}.event_type must be counter or value.")
            for flag in ("server_only", "published_game_only", "privacy_reviewed", "cardinality_reviewed"):
                if item.get(flag) is not True:
                    errors.append(f"{label}.{flag} must be true.")
        for name in sorted(event_names - set(event_map)):
            errors.append(f"Custom metric references undeclared instrumentation event {name!r}.")

    quality = data.get("quality_gates")
    if not isinstance(quality, dict):
        errors.append("quality_gates must be an object.")
    else:
        errors += check_fields(quality, QUALITY_GATE_FIELDS, "quality_gates")
        for field in QUALITY_GATE_FIELDS:
            if quality.get(field) is not True:
                errors.append(f"quality_gates.{field} must be true.")

    operations = data.get("operations")
    if not isinstance(operations, dict):
        errors.append("operations must be an object.")
    else:
        errors += check_fields(operations, OPERATION_FIELDS, "operations")
        for field in OPERATION_FIELDS:
            if operations.get(field) is not True:
                errors.append(f"operations.{field} must be true.")
    return sorted(set(errors))


def audit_manifest(data: dict) -> dict:
    warnings: list[str] = []
    if data["exposure_percent"] < 100:
        warnings.append("Partial exposure reduces the eligible sample; review Roblox's minimum detectable effect before scheduling.")
    if data["duration_days"] < 28:
        warnings.append("The planned duration is shorter than four weeks; verify that the goal metric has enough observation time and do not stop early for a favorable trend.")
    if not data["metrics"]["custom_metrics"]:
        warnings.append("No custom learning metrics are declared; verify that the goal metric alone answers the hypothesis.")
    if len(data["instrumentation"]["events"]) >= 80:
        warnings.append("The experience is approaching Roblox's 100 custom-event-name limit; reuse stable event names and reviewed custom fields.")
    if len(data["variants"]) == 3:
        warnings.append("Two treatment variants split the available audience; check per-variant MDE and sample feasibility.")
    return {
        "schema_version": 1,
        "experiment_id": data["experiment_id"],
        "status": "review_required" if warnings else "ready_for_human_review",
        "summary": {
            "config_key": data["config"]["key"],
            "duration_days": data["duration_days"],
            "exposure_percent": data["exposure_percent"],
            "variant_count": len(data["variants"]),
            "treatment_count": sum(1 for item in data["variants"] if not item["is_baseline"]),
            "goal_metric": data["metrics"]["goal_metric"],
            "custom_metric_count": len(data["metrics"]["custom_metrics"]),
            "instrumentation_event_count": len(data["instrumentation"]["events"]),
        },
        "warnings": sorted(warnings),
        "limitations": [
            "This audit validates a local plan only; it does not calculate Roblox MDE or guarantee a statistically useful sample.",
            "It does not create, schedule, start, monitor, or complete an experiment.",
            "A passing report is not approval to publish a variant. Review Creator Hub results and obtain human approval.",
        ],
    }


def compare_manifests(baseline: dict, candidate: dict) -> dict:
    changes: list[dict] = []
    def diff(label: str, left: Any, right: Any, breaking: bool = False) -> None:
        if left != right:
            changes.append({"field": label, "before": left, "after": right, "classification": "breaking" if breaking else "review"})
    for field in ("experiment_id", "name", "product_type"):
        diff(field, baseline[field], candidate[field])
    config_breaking = (
        baseline["config"].get("key") != candidate["config"].get("key")
        or baseline["config"].get("value_type") != candidate["config"].get("value_type")
    )
    diff("config", baseline["config"], candidate["config"], breaking=config_breaking)
    for field in ("hypothesis", "duration_days", "exposure_percent", "variants", "metrics", "instrumentation", "quality_gates", "operations"):
        diff(field, baseline[field], candidate[field])
    changes.sort(key=lambda item: item["field"])
    breaking = [item for item in changes if item["classification"] == "breaking"]
    warnings = [item for item in changes if item["classification"] != "breaking"]
    return {
        "schema_version": 1,
        "baseline_experiment_id": baseline["experiment_id"],
        "candidate_experiment_id": candidate["experiment_id"],
        "status": "breaking_changes" if breaking else ("review_required" if warnings else "unchanged"),
        "breaking_changes": breaking,
        "review_changes": warnings,
        "summary": {"breaking_change_count": len(breaking), "review_change_count": len(warnings)},
        "limitations": [
            "This compares declared plans only; it does not inspect live config conditions or Luau consumers.",
            "Changing an experiment after it is scheduled or running is not supported by the Roblox workflow; create a new draft/experiment instead.",
        ],
    }


def validate_results(manifest: dict, results: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(results, dict):
        return ["Results review input must be a JSON object."]
    errors += check_fields(results, RESULT_FIELDS, "results")
    if results.get("schema_version") != 1 or isinstance(results.get("schema_version"), bool):
        errors.append("results.schema_version must be integer 1.")
    if results.get("experiment_id") != manifest["experiment_id"]:
        errors.append("results.experiment_id must match the experiment manifest.")
    state = results.get("experiment_state")
    if not allowed(state, RESULT_STATES):
        errors.append("results.experiment_state must be DRAFT, SCHEDULED, RUNNING, DECISION_NEEDED, or COMPLETED.")
    parse_timestamp(results.get("observed_at"), "results.observed_at", errors)
    elapsed = results.get("elapsed_days")
    if not is_number(elapsed) or elapsed < 0 or elapsed > 60:
        errors.append("results.elapsed_days must be a finite number from 0 to 60.")
    for flag in ("srm_detected", "critical_harm_flag"):
        if not isinstance(results.get(flag), bool):
            errors.append(f"results.{flag} must be boolean.")
    counts = results.get("variant_enrolled_users")
    if not isinstance(counts, dict):
        errors.append("results.variant_enrolled_users must be an object keyed by variant_id.")
        counts = {}
    variant_ids = {item["variant_id"] for item in manifest["variants"]}
    if set(counts) != variant_ids:
        errors.append("results.variant_enrolled_users must contain exactly the manifest variant IDs.")
    for variant_id, count in counts.items():
        if not is_int(count, 0, 2**53 - 1):
            errors.append(f"results.variant_enrolled_users[{variant_id!r}] must be a non-negative integer.")
    treatments = results.get("treatment_results")
    treatment_ids = {item["variant_id"] for item in manifest["variants"] if not item["is_baseline"]}
    if not isinstance(treatments, list) or len(treatments) != len(treatment_ids):
        errors.append("results.treatment_results must contain exactly one entry per treatment variant.")
        treatments = []
    seen: set[str] = set()
    for index, item in enumerate(treatments):
        label = f"results.treatment_results[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue
        errors += check_fields(item, TREATMENT_RESULT_FIELDS, label)
        variant_id = item.get("variant_id")
        if not isinstance(variant_id, str) or variant_id not in treatment_ids:
            errors.append(f"{label}.variant_id must reference a treatment variant.")
        elif variant_id in seen:
            errors.append(f"Duplicate treatment result for {variant_id!r}.")
        else:
            seen.add(variant_id)
        for field in ("goal_metric_delta_percent", "confidence_interval_low_percent", "confidence_interval_high_percent"):
            if not is_number(item.get(field)):
                errors.append(f"{label}.{field} must be a finite number.")
        low = item.get("confidence_interval_low_percent")
        high = item.get("confidence_interval_high_percent")
        if is_number(low) and is_number(high) and low > high:
            errors.append(f"{label} confidence interval lower bound must not exceed upper bound.")
        guardrails = item.get("guardrails")
        if not isinstance(guardrails, list) or len(guardrails) > 20:
            errors.append(f"{label}.guardrails must contain at most 20 entries.")
            guardrails = []
        guardrail_ids: set[str] = set()
        for guard_index, guard in enumerate(guardrails):
            guard_label = f"{label}.guardrails[{guard_index}]"
            if not isinstance(guard, dict):
                errors.append(f"{guard_label} must be an object.")
                continue
            errors += check_fields(guard, GUARDRAIL_FIELDS, guard_label)
            metric_id = guard.get("metric_id")
            if not is_slug(metric_id):
                errors.append(f"{guard_label}.metric_id must be a lowercase slug.")
            elif metric_id in guardrail_ids:
                errors.append(f"{guard_label}.metric_id must be unique.")
            else:
                guardrail_ids.add(metric_id)
            for field in ("delta_percent", "confidence_interval_low_percent", "confidence_interval_high_percent"):
                if not is_number(guard.get(field)):
                    errors.append(f"{guard_label}.{field} must be a finite number.")
            gl = guard.get("confidence_interval_low_percent")
            gh = guard.get("confidence_interval_high_percent")
            if is_number(gl) and is_number(gh) and gl > gh:
                errors.append(f"{guard_label} confidence interval lower bound must not exceed upper bound.")
            if not allowed(guard.get("harmful_direction"), {"increase", "decrease"}):
                errors.append(f"{guard_label}.harmful_direction must be increase or decrease.")
    return sorted(set(errors))


def analyze_results(manifest: dict, results: dict) -> dict:
    errors = validate_results(manifest, results)
    if errors:
        return {"schema_version": 1, "experiment_id": manifest["experiment_id"], "status": "invalid_results", "errors": errors}
    issues: list[str] = []
    decisions: list[dict] = []
    if results["srm_detected"]:
        status = "invalid_sample_ratio_mismatch"
        issues.append("Roblox reports Sample Ratio Mismatch. Do not make a launch decision; investigate assignment/enrollment and restart only after review.")
    elif results["critical_harm_flag"]:
        status = "critical_harm_review"
        issues.append("A critical early-harm flag is present. Review safety and player impact with an operator; early-harm observations are not evidence of a successful launch.")
    elif results["experiment_state"] not in {"DECISION_NEEDED", "COMPLETED"} or results["elapsed_days"] < manifest["duration_days"] or any(count == 0 for count in results["variant_enrolled_users"].values()):
        status = "not_decision_ready"
        issues.append("The experiment has not completed its full planned duration or at least one variant has no enrolled players. Do not declare a winner from early trends or an empty sample.")
    else:
        desired = manifest["metrics"]["goal_direction"]
        goal_decisions: list[dict] = []
        for treatment in results["treatment_results"]:
            low = treatment["confidence_interval_low_percent"]
            high = treatment["confidence_interval_high_percent"]
            significant = low > 0 or high < 0
            favorable = (low > 0) if desired == "increase" else (high < 0)
            guardrail_harms = []
            for guard in treatment["guardrails"]:
                gl, gh = guard["confidence_interval_low_percent"], guard["confidence_interval_high_percent"]
                harm = (gl > 0) if guard["harmful_direction"] == "increase" else (gh < 0)
                if harm:
                    guardrail_harms.append(guard["metric_id"])
            goal_decisions.append({
                "variant_id": treatment["variant_id"],
                "goal_metric_significant": significant,
                "goal_metric_favorable": favorable and significant,
                "guardrail_harms": sorted(guardrail_harms),
            })
        decisions = goal_decisions
        if any(item["guardrail_harms"] for item in decisions):
            status = "tradeoff_review_required"
            issues.append("At least one treatment has a statistically significant adverse guardrail movement. Review the trade-off; a positive goal metric alone is not a clear win.")
        elif any(item["goal_metric_favorable"] for item in decisions):
            status = "candidate_for_human_review"
            issues.append("At least one treatment's goal-metric confidence interval excludes zero in the planned direction. This is a candidate for human review, not an automatic rollout instruction.")
        elif any(item["goal_metric_significant"] for item in decisions):
            status = "goal_metric_moved_against_hypothesis"
            issues.append("A treatment's goal metric is statistically significant in the direction opposite the hypothesis. Do not roll it out as a win.")
        else:
            status = "inconclusive"
            issues.append("No treatment's goal metric is statistically significant in the planned direction. Keep the control or plan a new, separately reviewed experiment.")
    return {
        "schema_version": 1,
        "experiment_id": manifest["experiment_id"],
        "status": status,
        "variant_reviews": decisions,
        "issues": sorted(issues),
        "limitations": [
            "Confidence intervals and SRM status must be transcribed from Roblox Creator Hub/Open Cloud results; this tool does not calculate statistical significance.",
            "A statistically significant result is not proof of universal benefit. Review player feedback, guardrails, experiment duration, and product context.",
            "This report never selects a winning variant, publishes config, completes an experiment, or performs a rollout.",
        ],
    }


def duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant is not allowed: {value}")


def resolve_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def safe_path(root: Path, raw: str, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 240 or "\x00" in raw or "\\" in raw or raw.startswith("/") or (len(raw) > 1 and raw[1:2] == ":"):
        raise ValueError("Path must be bounded, project-relative, and use forward slashes.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Empty, dot, and parent path segments are forbidden.")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise ValueError("Symlink traversal is not allowed.")
    resolved = probe.resolve(strict=must_exist)
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise ValueError("Path escapes the project root.") from exc
    if must_exist and not resolved.is_file():
        raise ValueError("Input must be an existing regular file.")
    return resolved


def load_json(root: Path, raw: str) -> Any:
    path = safe_path(root, raw, True)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("JSON input exceeds the 1 MiB limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=duplicate_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON: {exc}") from exc


def write_report(root: Path, raw: str, report: dict) -> None:
    path = safe_path(root, raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Output must be a regular file.")
    descriptor, temp = tempfile.mkstemp(prefix=".v43-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temp).replace(path)
    finally:
        try:
            Path(temp).unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("doctor")
    command.add_argument("--root", required=True)
    command = sub.add_parser("validate")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command = sub.add_parser("audit")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("compare")
    command.add_argument("--root", required=True)
    command.add_argument("--baseline", required=True)
    command.add_argument("--candidate", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("analyze")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command.add_argument("--results", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "doctor":
            print(f"V{VERSION} ready | project={root}")
            return 0
        if args.command == "compare":
            baseline, candidate = load_json(root, args.baseline), load_json(root, args.candidate)
            errors = [f"baseline: {e}" for e in validate_manifest(baseline)]
            errors += [f"candidate: {e}" for e in validate_manifest(candidate)]
            if errors:
                for error in errors:
                    print("FAIL: " + error)
                return 1
            report = compare_manifests(baseline, candidate)
            write_report(root, args.output, report)
            print(f"PASS: experiment comparison written; status={report['status']}; breaking={report['summary']['breaking_change_count']}; review={report['summary']['review_change_count']}.")
            return 1 if report["status"] == "breaking_changes" else 0
        manifest = load_json(root, args.manifest)
        errors = validate_manifest(manifest)
        if errors:
            for error in errors:
                print("FAIL: " + error)
            return 1
        if args.command == "validate":
            print("PASS: experiment hypothesis, config variants, metric plan, instrumentation, and quality gates are valid.")
            return 0
        if args.command == "audit":
            report = audit_manifest(manifest)
            write_report(root, args.output, report)
            print(f"PASS: experiment audit written; variants={report['summary']['variant_count']}; events={report['summary']['instrumentation_event_count']}; warnings={len(report['warnings'])}.")
            return 0
        results = load_json(root, args.results)
        report = analyze_results(manifest, results)
        write_report(root, args.output, report)
        print(f"PASS: results review written; status={report['status']}.")
        return 0 if report["status"] != "invalid_results" else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
