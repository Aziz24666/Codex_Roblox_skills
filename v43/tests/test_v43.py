from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("v43", ROOT / "tools" / "v43.py")
v43 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(v43)
PLAN = ROOT / "examples" / "experiment-plan.example.json"
RESULTS = ROOT / "examples" / "experiment-results.example.json"
PLAN_SCHEMA = ROOT / "schemas" / "experiment-plan.schema.json"
RESULTS_SCHEMA = ROOT / "schemas" / "experiment-results-review.schema.json"


class ManifestValidationTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(PLAN.read_text(encoding="utf-8"))

    def assertInvalid(self, model, fragment):
        errors = v43.validate_manifest(model)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_example_manifest_is_valid(self):
        self.assertEqual([], v43.validate_manifest(self.model))

    def test_example_manifest_conforms_to_json_schema(self):
        schema = json.loads(PLAN_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.model)

    def test_whitespace_only_name_rejected(self):
        data = copy.deepcopy(self.model)
        data["name"] = " " * 12
        self.assertInvalid(data, "non-whitespace")

    def test_oversized_config_string_rejected(self):
        data = copy.deepcopy(self.model)
        data["config"]["control_value"] = "x" * 100_001
        data["variants"][0]["value"] = data["config"]["control_value"]
        self.assertInvalid(data, "does not match config.value_type")

    def test_guardrails_are_required(self):
        data = copy.deepcopy(self.model)
        del data["metrics"]["guardrails"]
        self.assertInvalid(data, "guardrails must declare")

    def test_guardrails_must_be_nonempty(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["guardrails"] = []
        self.assertInvalid(data, "guardrails must declare")

    def test_guardrail_metric_ids_must_be_unique(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["guardrails"][1]["metric_id"] = data["metrics"]["guardrails"][0]["metric_id"]
        self.assertInvalid(data, "Duplicate guardrail metric_id")

    def test_guardrail_metric_must_be_declared(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["guardrails"][0]["metric"] = "custom:missing_metric"
        self.assertInvalid(data, "declared custom")

    def test_guardrail_cannot_duplicate_goal_metric(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["guardrails"][0]["metric"] = data["metrics"]["goal_metric"]
        self.assertInvalid(data, "must not repeat the primary goal metric")

    def test_non_object_rejected(self):
        self.assertIn("JSON object", v43.validate_manifest([])[0])

    def test_unknown_top_level_field_rejected(self):
        data = copy.deepcopy(self.model)
        data["unexpected"] = True
        self.assertInvalid(data, "unsupported fields")

    def test_boolean_schema_version_rejected(self):
        data = copy.deepcopy(self.model)
        data["schema_version"] = True
        self.assertInvalid(data, "integer 1")

    def test_product_type_restricted_to_native_in_game_config(self):
        data = copy.deepcopy(self.model)
        data["product_type"] = "custom_client_randomizer"
        self.assertInvalid(data, "in_game_config")

    def test_experiment_id_must_be_slug(self):
        data = copy.deepcopy(self.model)
        data["experiment_id"] = "Bad ID"
        self.assertInvalid(data, "lowercase slug")

    def test_experiment_name_length(self):
        data = copy.deepcopy(self.model)
        data["name"] = ""
        self.assertInvalid(data, "name must contain")

    def test_hypothesis_fields_must_be_meaningful(self):
        data = copy.deepcopy(self.model)
        data["hypothesis"]["rationale"] = "tiny"
        self.assertInvalid(data, "hypothesis.rationale")

    def test_hypothesis_extra_field_rejected(self):
        data = copy.deepcopy(self.model)
        data["hypothesis"]["invented"] = "extra"
        self.assertInvalid(data, "unsupported fields")

    def test_repository_must_be_in_experience_config(self):
        data = copy.deepcopy(self.model)
        data["config"]["repository"] = "DataStore"
        self.assertInvalid(data, "InExperienceConfig")

    def test_config_key_max_length(self):
        data = copy.deepcopy(self.model)
        data["config"]["key"] = "A" + "x" * 256
        self.assertInvalid(data, "config.key")

    def test_config_key_invalid_start(self):
        data = copy.deepcopy(self.model)
        data["config"]["key"] = "_flag"
        self.assertInvalid(data, "config.key")

    def test_config_value_type_mismatch(self):
        data = copy.deepcopy(self.model)
        data["config"]["value_type"] = "boolean"
        self.assertInvalid(data, "control_value does not match")

    def test_boolean_is_not_a_number(self):
        data = copy.deepcopy(self.model)
        data["config"]["value_type"] = "number"
        data["config"]["control_value"] = True
        self.assertInvalid(data, "control_value does not match")

    def test_duration_minimum(self):
        data = copy.deepcopy(self.model)
        data["duration_days"] = 13
        self.assertInvalid(data, "14 to 60")

    def test_duration_maximum(self):
        data = copy.deepcopy(self.model)
        data["duration_days"] = 61
        self.assertInvalid(data, "14 to 60")

    def test_boolean_duration_rejected(self):
        data = copy.deepcopy(self.model)
        data["duration_days"] = True
        self.assertInvalid(data, "14 to 60")

    def test_exposure_out_of_range(self):
        data = copy.deepcopy(self.model)
        data["exposure_percent"] = 0
        self.assertInvalid(data, "1 to 100")

    def test_exposure_boolean_rejected(self):
        data = copy.deepcopy(self.model)
        data["exposure_percent"] = True
        self.assertInvalid(data, "1 to 100")

    def test_variant_count_minimum(self):
        data = copy.deepcopy(self.model)
        data["variants"] = data["variants"][:1]
        self.assertInvalid(data, "one baseline and one or two treatment")

    def test_variant_count_maximum(self):
        data = copy.deepcopy(self.model)
        data["variants"] = data["variants"] * 2
        self.assertInvalid(data, "one baseline and one or two treatment")

    def test_exactly_one_baseline_required(self):
        data = copy.deepcopy(self.model)
        data["variants"][0]["is_baseline"] = False
        self.assertInvalid(data, "Exactly one variant")

    def test_two_baselines_rejected(self):
        data = copy.deepcopy(self.model)
        data["variants"].append({
            "variant_id": "guided_again", "label": "Guided 2", "is_baseline": True,
            "weight_percent": 20, "value": "guided"
        })
        data["variants"][1]["weight_percent"] = 30
        self.assertInvalid(data, "Exactly one variant")

    def test_variant_weights_must_sum_to_100(self):
        data = copy.deepcopy(self.model)
        data["variants"][0]["weight_percent"] = 60
        self.assertInvalid(data, "sum to 100")

    def test_variant_weight_boolean_rejected(self):
        data = copy.deepcopy(self.model)
        data["variants"][0]["weight_percent"] = True
        self.assertInvalid(data, "weight_percent")

    def test_duplicate_variant_id_rejected(self):
        data = copy.deepcopy(self.model)
        data["variants"][1]["variant_id"] = data["variants"][0]["variant_id"]
        self.assertInvalid(data, "Duplicate variant_id")

    def test_duplicate_variant_label_rejected_case_insensitive(self):
        data = copy.deepcopy(self.model)
        data["variants"][1]["label"] = "CLASSIC ONBOARDING"
        self.assertInvalid(data, "Duplicate variant label")

    def test_baseline_value_must_match_control(self):
        data = copy.deepcopy(self.model)
        data["variants"][0]["value"] = "wrong"
        self.assertInvalid(data, "must equal config.control_value")

    def test_variant_value_type_mismatch(self):
        data = copy.deepcopy(self.model)
        data["variants"][1]["value"] = False
        self.assertInvalid(data, "does not match config.value_type")

    def test_goal_metric_restricted(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["goal_metric"] = "REVENUE"
        self.assertInvalid(data, "goal_metric")

    def test_goal_direction_required(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["goal_direction"] = "whatever"
        self.assertInvalid(data, "goal_direction")

    def test_learning_metrics_cannot_repeat_goal(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["learning_metrics"].append("D1_RETENTION")
        self.assertInvalid(data, "must not repeat the goal metric")

    def test_learning_metric_duplicates_rejected(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["learning_metrics"].append("PLAYTIME")
        self.assertInvalid(data, "must be unique")

    def test_custom_metric_limit_three(self):
        data = copy.deepcopy(self.model)
        base = copy.deepcopy(data["metrics"]["custom_metrics"][0])
        data["metrics"]["custom_metrics"] = [base, copy.deepcopy(base), copy.deepcopy(base), copy.deepcopy(base)]
        self.assertInvalid(data, "at most 3 custom metrics")

    def test_custom_metric_id_unique(self):
        data = copy.deepcopy(self.model)
        second = copy.deepcopy(data["metrics"]["custom_metrics"][0])
        second["source_name"] = "OnboardingStarted"
        data["metrics"]["custom_metrics"].append(second)
        self.assertInvalid(data, "Duplicate custom metric_id")

    def test_custom_metric_event_name_must_be_declared(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["custom_metrics"][0]["source_name"] = "MissingEvent"
        self.assertInvalid(data, "references undeclared instrumentation event")

    def test_custom_metric_supports_funnel_source(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["custom_metrics"][0] = {
            "metric_id": "onboarding_finish",
            "source": "funnel",
            "source_name": "OnboardingFlow",
            "calculation": "PER_USER_FUNNEL_CONVERSION",
            "completion_step": 4
        }
        data["metrics"]["goal_metric"] = "custom:onboarding_finish"
        data["metrics"]["guardrails"][1]["metric"] = "custom:onboarding_finish"
        self.assertEqual([], v43.validate_manifest(data))

    def test_custom_metric_supports_economy_source(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["custom_metrics"][0] = {
            "metric_id": "coin_sink",
            "source": "economy",
            "source_name": "Coins",
            "calculation": "AVERAGE_CURRENCY_SINK_DELTA",
            "completion_step": None
        }
        data["metrics"]["guardrails"][1]["metric"] = "custom:coin_sink"
        self.assertEqual([], v43.validate_manifest(data))

    def test_custom_metric_goal_reference_must_exist(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["goal_metric"] = "custom:missing_metric"
        self.assertInvalid(data, "custom:<metric_id>")

    def test_funnel_metric_requires_completion_step(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["custom_metrics"][0]["source"] = "funnel"
        data["metrics"]["custom_metrics"][0]["calculation"] = "PER_USER_FUNNEL_CONVERSION"
        data["metrics"]["custom_metrics"][0]["completion_step"] = None
        self.assertInvalid(data, "completion_step")

    def test_custom_metric_calculation_restricted(self):
        data = copy.deepcopy(self.model)
        data["metrics"]["custom_metrics"][0]["calculation"] = "PER_PLAYER_PRIVATE_PROFILE"
        self.assertInvalid(data, "calculation")

    def test_instrumentation_event_count_maximum(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"] = data["instrumentation"]["events"] * 51
        self.assertInvalid(data, "0-100 event contracts")

    def test_instrumentation_event_names_unique(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][1]["event_name"] = data["instrumentation"]["events"][0]["event_name"]
        self.assertInvalid(data, "Duplicate instrumentation event_name")

    def test_instrumentation_event_name_format(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][0]["event_name"] = "bad event name"
        self.assertInvalid(data, "valid 1-64 character event name")

    def test_custom_event_name_limit_fixed_at_100(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["max_custom_event_names"] = 200
        self.assertInvalid(data, "must be 100")

    def test_client_events_rejected(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][0]["server_only"] = False
        self.assertInvalid(data, "server_only must be true")

    def test_studio_events_rejected(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][0]["published_game_only"] = False
        self.assertInvalid(data, "published_game_only must be true")

    def test_privacy_review_required(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][0]["privacy_reviewed"] = False
        self.assertInvalid(data, "privacy_reviewed must be true")

    def test_cardinality_review_required(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["events"][0]["cardinality_reviewed"] = False
        self.assertInvalid(data, "cardinality_reviewed must be true")

    def test_custom_fields_review_required(self):
        data = copy.deepcopy(self.model)
        data["instrumentation"]["custom_fields_reviewed"] = False
        self.assertInvalid(data, "custom_fields_reviewed must be true")

    def test_quality_gate_false_rejected(self):
        data = copy.deepcopy(self.model)
        data["quality_gates"]["mde_reviewed"] = False
        self.assertInvalid(data, "mde_reviewed must be true")

    def test_unknown_quality_gate_rejected(self):
        data = copy.deepcopy(self.model)
        data["quality_gates"]["skip_statistics"] = True
        self.assertInvalid(data, "unsupported fields")

    def test_api_credentials_must_stay_outside_repository(self):
        data = copy.deepcopy(self.model)
        data["operations"]["credentials_outside_repository"] = False
        self.assertInvalid(data, "credentials_outside_repository must be true")

    def test_open_cloud_writes_need_human_approval(self):
        data = copy.deepcopy(self.model)
        data["operations"]["write_requires_human_approval"] = False
        self.assertInvalid(data, "write_requires_human_approval must be true")


class ManifestAuditAndCompareTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_audit_counts(self):
        result = v43.audit_manifest(self.model)
        self.assertEqual(2, result["summary"]["variant_count"])
        self.assertEqual(2, result["summary"]["instrumentation_event_count"])
        self.assertEqual(1, result["summary"]["custom_metric_count"])

    def test_audit_partial_exposure_warning(self):
        data = copy.deepcopy(self.model)
        data["exposure_percent"] = 20
        report = v43.audit_manifest(data)
        self.assertTrue(any("reduces the eligible sample" in item for item in report["warnings"]))

    def test_audit_short_duration_warning(self):
        data = copy.deepcopy(self.model)
        data["duration_days"] = 14
        report = v43.audit_manifest(data)
        self.assertTrue(any("shorter than four weeks" in item for item in report["warnings"]))

    def test_audit_three_variants_warning(self):
        data = copy.deepcopy(self.model)
        data["variants"].append({
            "variant_id": "guided_b", "label": "Guided alternative",
            "is_baseline": False, "weight_percent": 20, "value": "guided-b"
        })
        data["variants"][0]["weight_percent"] = 40
        data["variants"][1]["weight_percent"] = 40
        report = v43.audit_manifest(data)
        self.assertTrue(any("split the available audience" in item for item in report["warnings"]))

    def test_identical_manifests_unchanged(self):
        self.assertEqual("unchanged", v43.compare_manifests(self.model, copy.deepcopy(self.model))["status"])

    def test_config_key_change_is_breaking(self):
        candidate = copy.deepcopy(self.model)
        candidate["config"]["key"] = "onboarding.different_key"
        result = v43.compare_manifests(self.model, candidate)
        self.assertEqual("breaking_changes", result["status"])

    def test_config_type_change_is_breaking(self):
        candidate = copy.deepcopy(self.model)
        candidate["config"]["value_type"] = "boolean"
        candidate["config"]["control_value"] = False
        candidate["variants"][0]["value"] = False
        candidate["variants"][1]["value"] = True
        result = v43.compare_manifests(self.model, candidate)
        self.assertEqual("breaking_changes", result["status"])

    def test_variant_change_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["variants"][1]["value"] = "guided-v2"
        result = v43.compare_manifests(self.model, candidate)
        self.assertEqual("review_required", result["status"])

    def test_experiment_id_change_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["experiment_id"] = "onboarding-flow-v2"
        self.assertEqual("review_required", v43.compare_manifests(self.model, candidate)["status"])

    def test_experiment_name_change_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["name"] = "A revised test"
        self.assertEqual("review_required", v43.compare_manifests(self.model, candidate)["status"])

    def test_metrics_change_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["metrics"]["goal_metric"] = "DAY_7_RETENTION"
        result = v43.compare_manifests(self.model, candidate)
        self.assertEqual("review_required", result["status"])


class ResultsReviewTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(PLAN.read_text(encoding="utf-8"))
        self.results = json.loads(RESULTS.read_text(encoding="utf-8"))

    def analyze(self, results=None):
        return v43.analyze_results(self.model, results or self.results)

    def test_example_results_valid(self):
        self.assertEqual([], v43.validate_results(self.model, self.results))

    def test_example_results_conform_to_json_schema(self):
        schema = json.loads(RESULTS_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(self.results)

    def test_schema_rejects_result_supplied_harmful_direction(self):
        schema = json.loads(RESULTS_SCHEMA.read_text(encoding="utf-8"))
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["harmful_direction"] = "decrease"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(data)))

    def test_success_candidate_requires_completed_full_duration(self):
        report = self.analyze()
        self.assertEqual("candidate_for_human_review", report["status"])

    def test_running_experiment_not_decision_ready(self):
        data = copy.deepcopy(self.results)
        data["experiment_state"] = "RUNNING"
        self.assertEqual("not_decision_ready", self.analyze(data)["status"])

    def test_draft_experiment_not_decision_ready(self):
        data = copy.deepcopy(self.results)
        data["experiment_state"] = "DRAFT"
        self.assertEqual("not_decision_ready", self.analyze(data)["status"])

    def test_decision_needed_after_full_duration_is_reviewable(self):
        data = copy.deepcopy(self.results)
        data["experiment_state"] = "DECISION_NEEDED"
        self.assertEqual("candidate_for_human_review", self.analyze(data)["status"])

    def test_scheduled_experiment_not_decision_ready(self):
        data = copy.deepcopy(self.results)
        data["experiment_state"] = "SCHEDULED"
        self.assertEqual("not_decision_ready", self.analyze(data)["status"])

    def test_completed_before_planned_duration_not_decision_ready(self):
        data = copy.deepcopy(self.results)
        data["elapsed_days"] = 14
        self.assertEqual("not_decision_ready", self.analyze(data)["status"])

    def test_unknown_experiment_state_rejected(self):
        data = copy.deepcopy(self.results)
        data["experiment_state"] = "STOPPED"
        self.assertTrue(any("experiment_state must be" in error for error in v43.validate_results(self.model, data)))

    def test_srm_invalidates_decision(self):
        data = copy.deepcopy(self.results)
        data["srm_detected"] = True
        self.assertEqual("invalid_sample_ratio_mismatch", self.analyze(data)["status"])

    def test_critical_harm_requires_review(self):
        data = copy.deepcopy(self.results)
        data["critical_harm_flag"] = True
        self.assertEqual("critical_harm_review", self.analyze(data)["status"])

    def test_goal_interval_crossing_zero_is_inconclusive(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["goal_metric_delta_percent"] = 0.5
        data["treatment_results"][0]["confidence_interval_low_percent"] = -1
        data["treatment_results"][0]["confidence_interval_high_percent"] = 2
        self.assertEqual("inconclusive", self.analyze(data)["status"])

    def test_significant_negative_goal_conflicts_with_hypothesis(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["goal_metric_delta_percent"] = -3
        data["treatment_results"][0]["confidence_interval_low_percent"] = -5
        data["treatment_results"][0]["confidence_interval_high_percent"] = -1
        self.assertEqual("goal_metric_moved_against_hypothesis", self.analyze(data)["status"])

    def test_significant_guardrail_harm_requires_tradeoff_review(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["delta_percent"] = -4
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_low_percent"] = -5
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_high_percent"] = -3
        self.assertEqual("tradeoff_review_required", self.analyze(data)["status"])

    def test_harmful_direction_is_taken_from_manifest(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["delta_percent"] = -4
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_low_percent"] = -5
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_high_percent"] = -3
        review = self.analyze(data)
        self.assertEqual("decrease", review["variant_reviews"][0]["guardrail_reviews"][0]["harmful_direction"])
        self.assertTrue(review["variant_reviews"][0]["guardrail_reviews"][0]["significant_harm"])

    def test_guardrail_interval_crossing_zero_not_significant_harm(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_low_percent"] = -1
        data["treatment_results"][0]["guardrails"][0]["confidence_interval_high_percent"] = 1
        self.assertEqual("candidate_for_human_review", self.analyze(data)["status"])

    def test_positive_goal_requires_lower_bound_above_zero_for_increase(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["confidence_interval_low_percent"] = 0
        data["treatment_results"][0]["confidence_interval_high_percent"] = 5
        self.assertEqual("inconclusive", self.analyze(data)["status"])

    def test_direction_decrease_can_be_favorable(self):
        model = copy.deepcopy(self.model)
        model["metrics"]["goal_direction"] = "decrease"
        results = copy.deepcopy(self.results)
        results["treatment_results"][0]["goal_metric_delta_percent"] = -3
        results["treatment_results"][0]["confidence_interval_low_percent"] = -5
        results["treatment_results"][0]["confidence_interval_high_percent"] = -1
        self.assertEqual("candidate_for_human_review", v43.analyze_results(model, results)["status"])

    def test_empty_variant_sample_not_decision_ready(self):
        data = copy.deepcopy(self.results)
        data["variant_enrolled_users"]["guided"] = 0
        self.assertEqual("not_decision_ready", self.analyze(data)["status"])

    def test_wrong_experiment_id_rejected(self):
        data = copy.deepcopy(self.results)
        data["experiment_id"] = "other-test"
        self.assertTrue(v43.validate_results(self.model, data))

    def test_missing_variant_sample_rejected(self):
        data = copy.deepcopy(self.results)
        del data["variant_enrolled_users"]["guided"]
        self.assertTrue(any("exactly the manifest variant IDs" in e for e in v43.validate_results(self.model, data)))

    def test_duplicate_treatment_result_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"].append(copy.deepcopy(data["treatment_results"][0]))
        self.assertTrue(any("exactly one entry" in e or "Duplicate treatment" in e for e in v43.validate_results(self.model, data)))

    def test_confidence_interval_order_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["confidence_interval_low_percent"] = 9
        data["treatment_results"][0]["confidence_interval_high_percent"] = 1
        self.assertTrue(any("lower bound must not exceed upper bound" in e for e in v43.validate_results(self.model, data)))

    def test_goal_point_estimate_must_lie_within_confidence_interval(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["goal_metric_delta_percent"] = 50
        self.assertTrue(any("must lie within its confidence interval" in e for e in v43.validate_results(self.model, data)))

    def test_guardrail_point_estimate_must_lie_within_confidence_interval(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["delta_percent"] = 50
        self.assertTrue(any("must lie within its confidence interval" in e for e in v43.validate_results(self.model, data)))

    def test_empty_guardrails_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"] = []
        self.assertTrue(any("exactly the 2 guardrails" in e for e in v43.validate_results(self.model, data)))

    def test_missing_guardrail_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"].pop()
        self.assertTrue(any("missing declared guardrail" in e for e in v43.validate_results(self.model, data)))

    def test_undeclared_guardrail_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][0]["metric_id"] = "unplanned_guardrail"
        self.assertTrue(any("not declared in the experiment manifest" in e for e in v43.validate_results(self.model, data)))

    def test_duplicate_guardrail_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["guardrails"][1]["metric_id"] = data["treatment_results"][0]["guardrails"][0]["metric_id"]
        errors = v43.validate_results(self.model, data)
        self.assertTrue(any("must be unique" in e for e in errors))
        self.assertTrue(any("missing declared guardrail" in e for e in errors))

    def test_nan_result_rejected(self):
        data = copy.deepcopy(self.results)
        data["treatment_results"][0]["goal_metric_delta_percent"] = float("nan")
        self.assertTrue(v43.validate_results(self.model, data))


class InputSafetyTests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            v43.duplicate_keys([("id", 1), ("id", 2)])

    def test_non_standard_constant_rejected(self):
        with self.assertRaises(ValueError):
            v43.reject_constant("NaN")

    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v43.safe_path(Path(temp), "../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v43.safe_path(Path(temp), "/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v43.safe_path(Path(temp), r"nested\manifest.json")

    def test_large_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "large.json").write_text(" " * (v43.MAX_INPUT_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                v43.load_json(root, "large.json")

    def test_atomic_report_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            v43.write_report(root, "reports/review.json", {"status": "ok"})
            self.assertEqual({"status": "ok"}, json.loads((root / "reports" / "review.json").read_text(encoding="utf-8")))

    def test_plan_and_results_examples_are_valid_json(self):
        json.loads(PLAN.read_text(encoding="utf-8"))
        json.loads(RESULTS.read_text(encoding="utf-8"))

    def test_v43_schemas_are_valid_and_examples_conform(self):
        plan_schema = json.loads((ROOT / "schemas" / "experiment-plan.schema.json").read_text(encoding="utf-8"))
        results_schema = json.loads((ROOT / "schemas" / "experiment-results-review.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(plan_schema)
        Draft202012Validator.check_schema(results_schema)
        Draft202012Validator(plan_schema).validate(json.loads(PLAN.read_text(encoding="utf-8")))
        Draft202012Validator(results_schema, format_checker=FormatChecker()).validate(json.loads(RESULTS.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
