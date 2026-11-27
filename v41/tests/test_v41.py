from __future__ import annotations
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("v41", ROOT / "tools" / "v41.py")
v41 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(v41)
EXAMPLE = ROOT / "examples" / "matchmaking-model.example.json"

class ModelValidationTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assertInvalid(self, model, fragment):
        errors = v41.validate_model(model)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_example_is_valid(self):
        self.assertEqual([], v41.validate_model(self.model))

    def test_unknown_top_level_field_rejected(self):
        data = copy.deepcopy(self.model); data["unknown"] = True
        self.assertInvalid(data, "unsupported fields")

    def test_boolean_is_not_integer_for_player_count(self):
        data = copy.deepcopy(self.model); data["matching"]["maximum_players"] = True
        self.assertInvalid(data, "maximum_players must be an integer")

    def test_player_counts_are_ordered(self):
        data = copy.deepcopy(self.model); data["matching"]["preferred_players"] = 11
        self.assertInvalid(data, "minimum_players <= preferred_players")

    def test_party_cannot_exceed_match_capacity(self):
        data = copy.deepcopy(self.model); data["party"]["maximum_size"] = 11
        self.assertInvalid(data, "party.maximum_size cannot exceed")

    def test_party_ticket_is_atomic(self):
        data = copy.deepcopy(self.model); data["party"]["party_ticket_atomic"] = False
        self.assertInvalid(data, "party_ticket_atomic must be true")

    def test_matching_never_splits_parties(self):
        data = copy.deepcopy(self.model); data["matching"]["party_atomicity"] = "split_if_needed"
        self.assertInvalid(data, "party_atomicity must be all_or_none")

    def test_memory_store_must_not_be_durable_profile_storage(self):
        data = copy.deepcopy(self.model); data["queue"]["stores_durable_player_data"] = True
        self.assertInvalid(data, "stores_durable_player_data must be false")

    def test_queue_calls_must_be_protected(self):
        data = copy.deepcopy(self.model); data["queue"]["network_calls_protected"] = False
        self.assertInvalid(data, "network_calls_protected must be true")

    def test_queue_entry_removal_after_assignment(self):
        data = copy.deepcopy(self.model); data["queue"]["remove_after_assignment"] = False
        self.assertInvalid(data, "remove_after_assignment must be true")

    def test_coordination_fencing_required(self):
        data = copy.deepcopy(self.model); data["coordination"]["fencing_token_required"] = False
        self.assertInvalid(data, "fencing_token_required must be true")

    def test_lease_refresh_must_not_exceed_half_lease(self):
        data = copy.deepcopy(self.model); data["coordination"]["lease_refresh_seconds"] = 60
        self.assertInvalid(data, "must not exceed half of lease_seconds")

    def test_messaging_is_not_authoritative(self):
        data = copy.deepcopy(self.model); data["coordination"]["messaging_as_authority"] = True
        self.assertInvalid(data, "messaging_as_authority must be false")

    def test_messaging_assumes_best_effort_delivery(self):
        data = copy.deepcopy(self.model); data["coordination"]["messaging_delivery_assumed"] = "guaranteed"
        self.assertInvalid(data, "messaging_delivery_assumed must be best_effort")

    def test_teleport_is_server_side(self):
        data = copy.deepcopy(self.model); data["teleport"]["server_context_only"] = False
        self.assertInvalid(data, "server_context_only must be true")

    def test_reserved_server_id_route_required(self):
        data = copy.deepcopy(self.model); data["teleport"]["route_mode"] = "access_code"
        self.assertInvalid(data, "route_mode must be ReservedServerId")

    def test_teleport_data_cannot_contain_secrets(self):
        data = copy.deepcopy(self.model); data["teleport"]["secure_data_in_teleport_payload"] = True
        self.assertInvalid(data, "teleport data is visible")

    def test_group_teleport_limit_is_enforced(self):
        data = copy.deepcopy(self.model); data["teleport"]["maximum_players_per_call"] = 5
        self.assertInvalid(data, "cannot exceed teleport.maximum_players_per_call")

    def test_teleport_init_failed_handler_required(self):
        data = copy.deepcopy(self.model); data["teleport"]["teleport_init_failed_handler"] = False
        self.assertInvalid(data, "teleport_init_failed_handler must be true")

    def test_ticket_retries_same_destination(self):
        data = copy.deepcopy(self.model); data["teleport"]["retry_same_destination"] = False
        self.assertInvalid(data, "retry_same_destination must be true")

    def test_client_cannot_be_authoritative_for_recovery(self):
        data = copy.deepcopy(self.model); data["recovery"]["client_state_is_authoritative"] = True
        self.assertInvalid(data, "client_state_is_authoritative must be false")

    def test_ticket_ids_must_be_unique(self):
        data = copy.deepcopy(self.model); data["simulation_tickets"].append(copy.deepcopy(data["simulation_tickets"][0]))
        self.assertInvalid(data, "Duplicate simulation ticket_id")

    def test_order_indexes_must_be_unique(self):
        data = copy.deepcopy(self.model); data["simulation_tickets"][1]["order_index"] = 0
        self.assertInvalid(data, "Duplicate simulation order_index")

    def test_simulation_ticket_party_size_is_bounded(self):
        data = copy.deepcopy(self.model); data["simulation_tickets"][0]["party_size"] = 6
        self.assertInvalid(data, "exceeds party.maximum_size")

    def test_non_object_model_is_rejected(self):
        self.assertIn("Model must be a JSON object.", v41.validate_model([]))

class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_simulation_is_deterministic(self):
        self.assertEqual(v41.simulate_match(self.model), v41.simulate_match(self.model))

    def test_example_selects_whole_parties(self):
        result = v41.simulate_match(self.model)
        self.assertEqual("matched", result["status"])
        self.assertEqual(["party_alpha", "party_beta"], result["selected_ticket_ids"])
        self.assertEqual(4, result["player_count"])
        self.assertTrue(result["synthetic_data"])

    def test_party_is_never_split_to_fill_match(self):
        model = copy.deepcopy(self.model)
        model["matching"].update(minimum_players=4, preferred_players=4, maximum_players=4)
        model["simulation_tickets"] = [
            {"ticket_id":"party_large", "party_size":3, "skill_rating":1000, "wait_seconds":30, "order_index":0},
            {"ticket_id":"party_two", "party_size":2, "skill_rating":1000, "wait_seconds":20, "order_index":1},
        ]
        result = v41.simulate_match(model)
        self.assertEqual(["party_large"], result["selected_ticket_ids"])
        self.assertEqual(3, result["player_count"])
        self.assertEqual("insufficient_players", result["status"])
        self.assertEqual("would_exceed_capacity_without_splitting_party", result["skipped"][0]["reason"])

    def test_empty_queue_returns_insufficient(self):
        model = copy.deepcopy(self.model); model["simulation_tickets"] = []
        result = v41.simulate_match(model)
        self.assertEqual("insufficient_players", result["status"])
        self.assertEqual([], result["selected_ticket_ids"])

    def test_skill_window_expands_with_anchor_wait(self):
        model = copy.deepcopy(self.model)
        model["simulation_tickets"] = [
            {"ticket_id":"anchor_one", "party_size":2, "skill_rating":1000, "wait_seconds":90, "order_index":0},
            {"ticket_id":"nearby", "party_size":2, "skill_rating":1150, "wait_seconds":10, "order_index":1},
        ]
        result = v41.simulate_match(model)
        self.assertEqual(125, result["skill_window_used"])
        self.assertNotIn("nearby", result["selected_ticket_ids"])

class AuditTests(unittest.TestCase):
    def test_audit_exposes_ephemeral_system_boundaries(self):
        model = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        report = v41.audit_model(model)
        self.assertTrue(any("does not call MemoryStoreService" in item for item in report["limitations"]))

    def test_short_queue_ttl_warns(self):
        model = json.loads(EXAMPLE.read_text(encoding="utf-8")); model["queue"]["item_ttl_seconds"] = 60
        report = v41.audit_model(model)
        self.assertTrue(any("TTL does not exceed" in warning for warning in report["warnings"]))

    def test_short_invisibility_timeout_warns(self):
        model = json.loads(EXAMPLE.read_text(encoding="utf-8")); model["queue"]["invisibility_timeout_seconds"] = 10
        report = v41.audit_model(model)
        self.assertTrue(any("shorter than Roblox's documented 30-second default" in warning for warning in report["warnings"]))

class InputSafetyTests(unittest.TestCase):
    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v41.safe_path(Path(temp), "../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v41.safe_path(Path(temp), "/tmp/outside.json")

    def test_windows_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v41.safe_path(Path(temp), r"nested\\model.json")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): v41.duplicate_keys([("queue", 1), ("queue", 2)])

    def test_non_standard_json_constant_rejected(self):
        with self.assertRaises(ValueError): v41.reject_constant("NaN")

    def test_symlink_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); outside = root.parent / "v41-symlink-test"
            outside.mkdir(exist_ok=True)
            try:
                (root / "linked").symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError): v41.safe_path(root, "linked/model.json")
            finally:
                shutil.rmtree(outside, ignore_errors=True)

    def test_input_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); large = root / "large.json"
            large.write_text(" " * (v41.MAX_INPUT_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError): v41.load_model(root, "large.json")

    def test_atomic_report_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = {"ok": True}
            v41.write_report(root, "reports/result.json", report)
            self.assertEqual(report, json.loads((root / "reports/result.json").read_text(encoding="utf-8")))

if __name__ == "__main__":
    unittest.main()
