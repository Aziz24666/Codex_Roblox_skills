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
SPEC = importlib.util.spec_from_file_location("v44", ROOT / "tools" / "v44.py")
v44 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(v44)
STUDY_PATH = ROOT / "examples" / "feedback-study.example.json"
DATA_PATH = ROOT / "examples" / "feedback-data.example.json"
STUDY_SCHEMA = ROOT / "schemas" / "feedback-study.schema.json"
DATA_SCHEMA = ROOT / "schemas" / "feedback-data.schema.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class StudyValidationTests(unittest.TestCase):
    def setUp(self):
        self.study = read_json(STUDY_PATH)

    def test_example_valid(self):
        self.assertEqual([], v44.validate_study(self.study))

    def test_reject_boolean_schema_version(self):
        data = copy.deepcopy(self.study)
        data["schema_version"] = True
        self.assertTrue(v44.validate_study(data))

    def test_reject_unknown_identifier_field(self):
        data = copy.deepcopy(self.study)
        data["player_id"] = "12345"
        self.assertTrue(any("unsupported fields" in e for e in v44.validate_study(data)))

    def test_reject_unapproved_collection_notice(self):
        data = copy.deepcopy(self.study)
        data["notice"]["no_identifiers"] = False
        self.assertTrue(any("no_identifiers" in e for e in v44.validate_study(data)))

    def test_reject_unbounded_retention(self):
        data = copy.deepcopy(self.study)
        data["notice"]["retention_days"] = 365
        self.assertTrue(v44.validate_study(data))

    def test_reject_minimum_above_maximum(self):
        data = copy.deepcopy(self.study)
        data["target"]["minimum_responses"] = 101
        self.assertTrue(v44.validate_study(data))

    def test_reject_timezone_naive_window(self):
        data = copy.deepcopy(self.study)
        data["window"]["starts_at"] = "2026-10-01T00:00:00"
        self.assertTrue(any("timezone" in e for e in v44.validate_study(data)))

    def test_reject_reversed_window(self):
        data = copy.deepcopy(self.study)
        data["window"]["ends_at"] = "2026-09-30T23:59:59Z"
        self.assertTrue(any("later" in e for e in v44.validate_study(data)))

    def test_reject_window_over_90_days(self):
        data = copy.deepcopy(self.study)
        data["window"]["ends_at"] = "2027-02-01T00:00:00Z"
        self.assertTrue(any("90 days" in e for e in v44.validate_study(data)))

    def test_reject_duplicate_question_id(self):
        data = copy.deepcopy(self.study)
        data["questions"].append(copy.deepcopy(data["questions"][0]))
        self.assertTrue(any("Duplicate question_id" in e for e in v44.validate_study(data)))

    def test_reject_unknown_topic(self):
        data = copy.deepcopy(self.study)
        data["questions"][0]["topic"] = ["invalid"]
        self.assertTrue(v44.validate_study(data))

    def test_audit_flags_leading_prompt(self):
        data = copy.deepcopy(self.study)
        data["questions"][0]["prompt"] = "Was this obviously the best tutorial?"
        self.assertTrue(any("leading" in warning for warning in v44.audit_study(data)["warnings"]))

    def test_audit_requires_human_approval(self):
        self.assertTrue(v44.audit_study(self.study)["human_approval_required"])


class FeedbackDataTests(unittest.TestCase):
    def setUp(self):
        self.study = read_json(STUDY_PATH)
        self.data = read_json(DATA_PATH)

    def test_example_valid(self):
        self.assertEqual([], v44.validate_data(self.study, self.data))

    def test_reject_mismatched_study_id(self):
        data = copy.deepcopy(self.data)
        data["study_id"] = "another-study"
        self.assertTrue(any("study_id" in e for e in v44.validate_data(self.study, data)))

    def test_reject_mismatched_build(self):
        data = copy.deepcopy(self.data)
        data["build_id"] = "other-build"
        self.assertTrue(any("build_id" in e for e in v44.validate_data(self.study, data)))

    def test_reject_duplicate_response_ref(self):
        data = copy.deepcopy(self.data)
        data["records"][1]["response_ref"] = data["records"][0]["response_ref"]
        self.assertTrue(any("Duplicate response_ref" in e for e in v44.validate_data(self.study, data)))

    def test_reject_nonopaque_reference(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["response_ref"] = "player_123456"
        self.assertTrue(v44.validate_data(self.study, data))

    def test_reject_free_text_field(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["raw_text"] = "This contains identifying data"
        self.assertTrue(any("unsupported fields" in e for e in v44.validate_data(self.study, data)))

    def test_reject_account_id_field(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["user_id"] = 123
        self.assertTrue(v44.validate_data(self.study, data))

    def test_reject_unknown_cohort(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["cohort"] = "specific_player"
        self.assertTrue(v44.validate_data(self.study, data))

    def test_reject_record_outside_window(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["collected_at"] = "2026-09-01T00:00:00Z"
        self.assertTrue(any("outside" in e for e in v44.validate_data(self.study, data)))

    def test_reject_duplicate_tags(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["tags"] = ["confusing", "confusing"]
        self.assertTrue(any("tags" in e for e in v44.validate_data(self.study, data)))

    def test_reject_unhashable_tag(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["tags"] = [{"free": "text"}]
        self.assertTrue(any("tags" in e for e in v44.validate_data(self.study, data)))

    def test_reject_unknown_record_source(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["source"] = "private_chat_log"
        self.assertTrue(v44.validate_data(self.study, data))

    def test_reject_extra_nested_fields(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["participant"] = {"name": "Example"}
        self.assertTrue(v44.validate_data(self.study, data))

    def test_summary_suppresses_small_cells_and_uses_bands(self):
        report = v44.summarize(self.study, self.data)
        self.assertEqual("3-5", report["topic_counts"]["count_bands"]["onboarding"])
        self.assertNotIn("interface", report["topic_counts"]["count_bands"])
        self.assertTrue(report["topic_counts"]["has_suppressed_categories"])
        self.assertNotIn("record_count", report)

    def test_summary_is_descriptive_not_a_winner(self):
        report = v44.summarize(self.study, self.data)
        self.assertEqual("candidate_for_human_review", report["status"])
        self.assertTrue(report["human_decision_required"])
        self.assertIn("not presumed representative", report["interpretation"])
        self.assertIn("Exact total", report["interpretation"])

    def test_summary_target_is_not_a_success_signal(self):
        report = v44.summarize(self.study, self.data)
        self.assertNotIn("target_minimum_reached", report)


class InputAndSchemaTests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            v44._pairs_no_duplicates([("id", 1), ("id", 2)])

    def test_nonstandard_json_constant_rejected(self):
        with self.assertRaises(ValueError):
            v44._reject_constant("NaN")

    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v44.safe_path(Path(temp), "../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v44.safe_path(Path(temp), "/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v44.safe_path(Path(temp), r"nested\input.json")

    def test_empty_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                v44.safe_path(Path(temp), ".")

    def test_large_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "large.json").write_text(" " * (v44.MAX_INPUT_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                v44.load_json(root, "large.json")

    def test_atomic_report_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            v44.write_report(root, "reports/summary.json", {"status": "ok"})
            self.assertEqual({"status": "ok"}, read_json(root / "reports" / "summary.json"))

    def test_schemas_and_examples_conform(self):
        study_schema = read_json(STUDY_SCHEMA)
        data_schema = read_json(DATA_SCHEMA)
        Draft202012Validator.check_schema(study_schema)
        Draft202012Validator.check_schema(data_schema)
        Draft202012Validator(study_schema, format_checker=FormatChecker()).validate(read_json(STUDY_PATH))
        Draft202012Validator(data_schema, format_checker=FormatChecker()).validate(read_json(DATA_PATH))


if __name__ == "__main__":
    unittest.main()
