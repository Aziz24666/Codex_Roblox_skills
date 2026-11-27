from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("v42", ROOT / "tools" / "v42.py")
v42 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(v42)
EXAMPLE = ROOT / "examples" / "liveops-model.example.json"


class ModelValidationTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assertInvalid(self, model, fragment):
        errors = v42.validate_model(model)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_example_is_valid(self):
        self.assertEqual([], v42.validate_model(self.model))

    def test_unknown_top_level_field_rejected(self):
        data = copy.deepcopy(self.model)
        data["unknown"] = True
        self.assertInvalid(data, "unsupported fields")

    def test_boolean_schema_version_rejected(self):
        data = copy.deepcopy(self.model)
        data["schema_version"] = True
        self.assertInvalid(data, "schema_version must be integer 1")

    def test_wrong_repository_rejected(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["repository"] = "MemoryStore"
        self.assertInvalid(data, "repository must be InExperienceConfig")

    def test_repository_key_limit_capped_at_100(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["key_limit"] = 101
        self.assertInvalid(data, "key_limit must be an integer from 1 to 100")

    def test_declared_config_count_cannot_exceed_contract_limit(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["key_limit"] = 4
        self.assertInvalid(data, "exceeding config_contract.key_limit")

    def test_active_config_limit_capped_at_1000(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["active_config_limit"] = 1001
        self.assertInvalid(data, "active_config_limit must be an integer from 1 to 1000")

    def test_runtime_config_write_must_be_disabled(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["runtime_write_access"] = True
        self.assertInvalid(data, "runtime_write_access must be false")

    def test_staging_required(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["staged_before_publish"] = False
        self.assertInvalid(data, "staged_before_publish must be true")

    def test_draft_hash_guard_required(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["draft_hash_guard"] = False
        self.assertInvalid(data, "draft_hash_guard must be true")

    def test_server_only_config_contract(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["server_only"] = False
        self.assertInvalid(data, "config_contract.server_only must be true")

    def test_unknown_snapshot_policy_rejected(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["snapshot_refresh_policy"] = "always_mid_match"
        self.assertInvalid(data, "snapshot_refresh_policy")

    def test_wrong_refresh_signal_contract_rejected(self):
        data = copy.deepcopy(self.model)
        data["config_contract"]["refresh_signal_handling"] = "none"
        self.assertInvalid(data, "refresh_signal_handling")

    def test_duplicate_config_key_rejected(self):
        data = copy.deepcopy(self.model)
        data["configs"].append(copy.deepcopy(data["configs"][0]))
        self.assertInvalid(data, "Duplicate config key")

    def test_config_key_length_capped_at_256(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["key"] = "A" + "x" * 256
        self.assertInvalid(data, "key must be 1-256 characters")

    def test_invalid_config_key_start_rejected(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["key"] = "_private"
        self.assertInvalid(data, "key must be 1-256 characters")

    def test_too_many_config_entries_rejected(self):
        data = copy.deepcopy(self.model)
        data["configs"] = data["configs"] * 17
        self.assertInvalid(data, "configs must contain 1-100")

    def test_default_type_mismatch_rejected(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["default_value"] = "true"
        self.assertInvalid(data, "does not match value_type boolean")

    def test_boolean_is_not_a_number(self):
        data = copy.deepcopy(self.model)
        data["configs"][3]["default_value"] = True
        self.assertInvalid(data, "does not match value_type number")

    def test_secret_values_forbidden(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["contains_secret"] = True
        self.assertInvalid(data, "contains_secret must be false")

    def test_config_consumer_is_server_only(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["server_only"] = False
        self.assertInvalid(data, "server_only must be true")

    def test_string_config_limit(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["value_type"] = "string"
        data["configs"][0]["default_value"] = "x" * (v42.MAX_CONFIG_VALUE_CHARS + 1)
        self.assertInvalid(data, "exceeds Roblox")

    def test_json_config_limit(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["value_type"] = "json"
        data["configs"][0]["default_value"] = {"payload": "x" * v42.MAX_CONFIG_VALUE_CHARS}
        self.assertInvalid(data, "exceeds Roblox")

    def test_inexact_large_integer_rejected(self):
        data = copy.deepcopy(self.model)
        data["configs"][3]["default_value"] = 2**53 + 1
        self.assertInvalid(data, "exact numeric representation")

    def test_condition_count_per_config_limit(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["targeting_mode"] = "conditional"
        data["configs"][0]["condition_count"] = 21
        self.assertInvalid(data, "condition_count must be an integer from 0 to 20")

    def test_global_config_cannot_have_conditions(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["condition_count"] = 1
        self.assertInvalid(data, "global targeting must have condition_count 0")

    def test_conditional_config_requires_condition(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["targeting_mode"] = "conditional"
        self.assertInvalid(data, "conditional targeting must declare at least one condition")

    def test_condition_order_review_required(self):
        data = copy.deepcopy(self.model)
        data["configs"][5]["condition_order_reviewed"] = False
        self.assertInvalid(data, "condition_order_reviewed must be true")

    def test_experience_condition_total_capped_at_100(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["targeting_mode"] = "conditional"
        data["configs"][0]["condition_count"] = 20
        data["configs"][1]["targeting_mode"] = "conditional"
        data["configs"][1]["condition_count"] = 20
        data["configs"][2]["targeting_mode"] = "conditional"
        data["configs"][2]["condition_count"] = 20
        data["configs"][3]["targeting_mode"] = "conditional"
        data["configs"][3]["condition_count"] = 20
        data["configs"][4]["targeting_mode"] = "conditional"
        data["configs"][4]["condition_count"] = 20
        data["configs"][5]["targeting_mode"] = "conditional"
        data["configs"][5]["condition_count"] = 20
        self.assertInvalid(data, "Total condition_count exceeds")

    def test_naive_event_timestamp_rejected(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["starts_at"] = "2027-12-01T00:00:00"
        self.assertInvalid(data, "timezone or UTC offset")

    def test_invalid_event_timestamp_rejected(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["starts_at"] = "not-a-date"
        self.assertInvalid(data, "valid ISO 8601")

    def test_event_end_must_follow_start(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["ends_at"] = "2027-11-30T00:00:00Z"
        self.assertInvalid(data, "ends_at must be later")

    def test_overlapping_active_events_in_same_group_rejected(self):
        data = copy.deepcopy(self.model)
        second = data["events"][1]
        second["status"] = "scheduled"
        second["schedule_group"] = data["events"][0]["schedule_group"]
        second["starts_at"] = "2027-12-10T00:00:00Z"
        second["ends_at"] = "2027-12-20T00:00:00Z"
        second["test_case_ids"] = ["event_start"]
        self.assertInvalid(data, "overlap in schedule_group")

    def test_overlapping_events_in_different_groups_allowed(self):
        data = copy.deepcopy(self.model)
        second = data["events"][1]
        second["status"] = "scheduled"
        second["starts_at"] = "2027-12-10T00:00:00Z"
        second["ends_at"] = "2027-12-20T00:00:00Z"
        second["test_case_ids"] = ["event_start"]
        self.assertEqual([], v42.validate_model(data))

    def test_unknown_event_config_key_rejected(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["config_keys"].append("event.missing.enabled")
        self.assertInvalid(data, "references undeclared config key")

    def test_enabled_event_key_must_be_in_config_key_list(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["config_keys"].remove("event.winter_festival.enabled")
        self.assertInvalid(data, "must also appear in config_keys")

    def test_enabled_event_key_must_be_boolean(self):
        data = copy.deepcopy(self.model)
        data["configs"][1]["value_type"] = "number"
        data["configs"][1]["default_value"] = 0
        self.assertInvalid(data, "must reference a boolean")

    def test_staged_event_requires_test_cases(self):
        data = copy.deepcopy(self.model)
        data["events"][1]["status"] = "scheduled"
        self.assertInvalid(data, "must not be empty")

    def test_cancelled_event_can_have_no_test_cases(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["status"] = "cancelled"
        data["events"][0]["test_case_ids"] = []
        self.assertEqual([], v42.validate_model(data))

    def test_event_preflight_required(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["preflight_required"] = False
        self.assertInvalid(data, "preflight_required must be true")

    def test_deployment_requires_human_approval(self):
        data = copy.deepcopy(self.model)
        data["deployment"]["human_approval_required"] = False
        self.assertInvalid(data, "human_approval_required must be true")

    def test_deployment_message_length(self):
        data = copy.deepcopy(self.model)
        data["deployment"]["publish_message"] = "short"
        self.assertInvalid(data, "publish_message must contain")

    def test_draft_hash_guard_at_deployment(self):
        data = copy.deepcopy(self.model)
        data["deployment"]["draft_hash_guard_required"] = False
        self.assertInvalid(data, "draft_hash_guard_required must be true")

    def test_api_key_must_stay_outside_project(self):
        data = copy.deepcopy(self.model)
        data["deployment"]["api_key_outside_project"] = False
        self.assertInvalid(data, "api_key_outside_project must be true")

    def test_rollback_requires_republish_after_restore(self):
        data = copy.deepcopy(self.model)
        data["rollback"]["republish_after_restore"] = False
        self.assertInvalid(data, "republish_after_restore must be true")

    def test_rollback_requires_human_approval(self):
        data = copy.deepcopy(self.model)
        data["rollback"]["human_approval_required"] = False
        self.assertInvalid(data, "rollback.human_approval_required must be true")

    def test_consumer_must_reference_existing_config(self):
        data = copy.deepcopy(self.model)
        data["consumers"][0]["config_key"] = "not.registered"
        self.assertInvalid(data, "must reference a declared config")

    def test_consumer_type_must_match_config(self):
        data = copy.deepcopy(self.model)
        data["consumers"][0]["expected_type"] = "number"
        self.assertInvalid(data, "does not match config")

    def test_consumer_fallback_must_match_type(self):
        data = copy.deepcopy(self.model)
        data["consumers"][0]["fallback_value"] = 0
        self.assertInvalid(data, "fallback_value does not match")

    def test_required_consumer_needs_fallback(self):
        data = copy.deepcopy(self.model)
        del data["consumers"][0]["fallback_value"]
        self.assertInvalid(data, "missing required fields")

    def test_consumer_must_be_server_side(self):
        data = copy.deepcopy(self.model)
        data["consumers"][0]["server_only"] = False
        self.assertInvalid(data, "server_only must be true")

    def test_duplicate_consumer_id_rejected(self):
        data = copy.deepcopy(self.model)
        data["consumers"][1]["consumer_id"] = data["consumers"][0]["consumer_id"]
        self.assertInvalid(data, "Duplicate consumer_id")

    def test_unhashable_config_type_is_reported_not_raised(self):
        data = copy.deepcopy(self.model)
        data["configs"][0]["value_type"] = []
        self.assertTrue(v42.validate_model(data))

    def test_unhashable_event_status_is_reported_not_raised(self):
        data = copy.deepcopy(self.model)
        data["events"][0]["status"] = []
        self.assertTrue(v42.validate_model(data))

    def test_unhashable_consumer_type_is_reported_not_raised(self):
        data = copy.deepcopy(self.model)
        data["consumers"][0]["expected_type"] = []
        self.assertTrue(v42.validate_model(data))


class AuditAndCompareTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_audit_is_deterministic(self):
        self.assertEqual(v42.audit_model(self.model), v42.audit_model(self.model))

    def test_audit_reports_counts(self):
        result = v42.audit_model(self.model)
        self.assertEqual(6, result["summary"]["config_count"])
        self.assertEqual(2, result["summary"]["event_count"])
        self.assertEqual(6, result["summary"]["runtime_consumer_count"])

    def test_audit_warns_about_immediate_rollout(self):
        model = copy.deepcopy(self.model)
        model["deployment"]["strategy"] = "Immediate"
        result = v42.audit_model(model)
        self.assertTrue(any("Immediate publishing" in item for item in result["warnings"]))

    def test_audit_warns_for_unused_config(self):
        model = copy.deepcopy(self.model)
        model["configs"][0]["key"] = "feature.unused"
        result = v42.audit_model(model)
        self.assertIn("feature.unused", result["summary"]["unused_config_keys"])

    def test_unchanged_models_are_compatible(self):
        result = v42.compare_models(self.model, copy.deepcopy(self.model))
        self.assertEqual("compatible", result["status"])

    def test_removed_config_is_breaking(self):
        candidate = copy.deepcopy(self.model)
        candidate["configs"] = [item for item in candidate["configs"] if item["key"] != "feature.new_lobby"]
        result = v42.compare_models(self.model, candidate)
        self.assertEqual("breaking_changes", result["status"])
        self.assertEqual(["feature.new_lobby"], result["changes"]["removed_config_keys"])

    def test_type_change_is_breaking(self):
        candidate = copy.deepcopy(self.model)
        candidate["configs"][0]["value_type"] = "string"
        candidate["configs"][0]["default_value"] = "disabled"
        result = v42.compare_models(self.model, candidate)
        self.assertEqual("breaking_changes", result["status"])
        self.assertEqual(1, result["summary"]["type_change_count"])

    def test_default_change_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["configs"][3]["default_value"] = 1.25
        result = v42.compare_models(self.model, candidate)
        self.assertEqual("review_required", result["status"])
        self.assertEqual(1, result["summary"]["default_change_count"])

    def test_event_removal_requires_review(self):
        candidate = copy.deepcopy(self.model)
        candidate["events"] = [candidate["events"][1]]
        result = v42.compare_models(self.model, candidate)
        self.assertEqual("review_required", result["status"])
        self.assertEqual(["winter_festival"], result["changes"]["removed_events"])

    def test_event_addition_is_reported(self):
        candidate = copy.deepcopy(self.model)
        new_event = copy.deepcopy(candidate["events"][0])
        new_event["event_id"] = "new_event"
        candidate["events"].append(new_event)
        result = v42.compare_models(self.model, candidate)
        self.assertEqual(["new_event"], result["changes"]["added_events"])


class InputSafetyTests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            v42.duplicate_keys([("key", 1), ("key", 2)])

    def test_non_standard_constant_rejected(self):
        with self.assertRaises(ValueError):
            v42.reject_constant("NaN")

    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v42.safe_path(Path(temp), "../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v42.safe_path(Path(temp), "/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v42.safe_path(Path(temp), r"nested\model.json")

    def test_large_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "large.json").write_text(" " * (v42.MAX_INPUT_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                v42.load_model(root, "large.json")

    def test_atomic_report_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            v42.write_report(root, "reports/audit.json", {"ok": True})
            self.assertEqual({"ok": True}, json.loads((root / "reports" / "audit.json").read_text(encoding="utf-8")))

    def test_schema_and_example_are_valid_json(self):
        schema = json.loads((ROOT / "schemas" / "liveops-model.schema.json").read_text(encoding="utf-8"))
        model = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual([], v42.validate_model(model))


if __name__ == "__main__":
    unittest.main()
