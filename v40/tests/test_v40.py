from __future__ import annotations
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import v40

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/"examples"/"persistence-model.example.json"

class PersistenceContractTests(unittest.TestCase):
    def setUp(self):
        self.model=json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assertInvalid(self,model,fragment):
        errors=v40.validate_model(model)
        self.assertTrue(any(fragment in error for error in errors),errors)

    def test_example_is_valid(self):
        self.assertEqual([],v40.validate_model(self.model))

    def test_unknown_top_level_field_rejected(self):
        data=copy.deepcopy(self.model); data["raw_player_data"]=[]
        self.assertInvalid(data,"unsupported fields")

    def test_missing_top_level_field_rejected(self):
        data=copy.deepcopy(self.model); del data["saving"]
        self.assertInvalid(data,"missing required fields")

    def test_boolean_schema_version_rejected(self):
        data=copy.deepcopy(self.model); data["schema_version"]=True
        self.assertInvalid(data,"schema_version")

    def test_bad_model_id_rejected(self):
        data=copy.deepcopy(self.model); data["model_id"]="../bad"
        self.assertInvalid(data,"model_id")

    def test_invalid_store_name_rejected(self):
        data=copy.deepcopy(self.model); data["profile_store"]["store_name"]="player profiles!"
        self.assertInvalid(data,"store_name")

    def test_store_name_over_50_characters_rejected(self):
        data=copy.deepcopy(self.model); data["profile_store"]["store_name"]="x"*51
        self.assertInvalid(data,"store_name")

    def test_minimum_supported_version_cannot_exceed_current(self):
        data=copy.deepcopy(self.model); data["profile_store"]["minimum_supported_version"]=4
        self.assertInvalid(data,"cannot exceed schema_version")

    def test_profile_payload_limit_rejected(self):
        data=copy.deepcopy(self.model); data["profile_store"]["profile_size_budget_bytes"]=5_000_000
        self.assertInvalid(data,"profile_size_budget_bytes")

    def test_non_user_key_strategy_rejected(self):
        data=copy.deepcopy(self.model); data["profile_store"]["key_strategy"]="display_name"
        self.assertInvalid(data,"key_strategy")

    def test_session_lock_required(self):
        data=copy.deepcopy(self.model); data["session"]["locking_enabled"]=False
        self.assertInvalid(data,"locking_enabled")

    def test_session_lock_method_must_be_update_async_lease(self):
        data=copy.deepcopy(self.model); data["session"]["lock_method"]="SetAsync"
        self.assertInvalid(data,"lock_method")

    def test_refresh_interval_must_fit_inside_lease(self):
        data=copy.deepcopy(self.model); data["session"]["refresh_interval_seconds"]=100
        self.assertInvalid(data,"half of lease_seconds")

    def test_missing_owner_token_rejected(self):
        data=copy.deepcopy(self.model); data["session"]["owner_token_required"]=False
        self.assertInvalid(data,"owner_token_required")

    def test_wrong_save_method_rejected(self):
        data=copy.deepcopy(self.model); data["saving"]["write_method"]="SetAsync"
        self.assertInvalid(data,"write_method")

    def test_boolean_retry_count_rejected(self):
        data=copy.deepcopy(self.model); data["saving"]["retry_attempts"]=True
        self.assertInvalid(data,"retry_attempts")

    def test_shutdown_budget_capped_at_25_seconds(self):
        data=copy.deepcopy(self.model); data["saving"]["shutdown_budget_seconds"]=30
        self.assertInvalid(data,"shutdown_budget_seconds")

    def test_max_backoff_cannot_be_smaller_than_initial(self):
        data=copy.deepcopy(self.model); data["saving"]["max_backoff_ms"]=100
        self.assertInvalid(data,"cannot be smaller")

    def test_jitter_required(self):
        data=copy.deepcopy(self.model); data["saving"]["jitter"]=False
        self.assertInvalid(data,"jitter must be true")

    def test_unknown_write_outcome_requires_reconciliation(self):
        data=copy.deepcopy(self.model); data["saving"]["unknown_write_outcome"]="blind_retry"
        self.assertInvalid(data,"unknown_write_outcome")

    def test_empty_fields_rejected(self):
        data=copy.deepcopy(self.model); data["fields"]=[]
        self.assertInvalid(data,"fields must contain")

    def test_duplicate_field_id_rejected(self):
        data=copy.deepcopy(self.model); data["fields"].append(copy.deepcopy(data["fields"][0]))
        self.assertInvalid(data,"Duplicate field_id")

    def test_sensitive_field_name_rejected(self):
        data=copy.deepcopy(self.model); data["fields"][0]["field_id"]="email"
        self.assertInvalid(data,"personal or sensitive")

    def test_unknown_data_type_rejected(self):
        data=copy.deepcopy(self.model); data["fields"][0]["data_type"]="binary"
        self.assertInvalid(data,"data_type")

    def test_default_value_type_mismatch_rejected(self):
        data=copy.deepcopy(self.model); data["fields"][0]["default_value"]="100"
        self.assertInvalid(data,"does not match data_type")

    def test_boolean_is_not_an_integer_default(self):
        data=copy.deepcopy(self.model); data["fields"][0]["default_value"]=True
        self.assertInvalid(data,"does not match data_type integer")

    def test_field_budgets_cannot_exceed_profile_budget(self):
        data=copy.deepcopy(self.model); data["fields"][0]["max_encoded_bytes"]=1_600_000
        self.assertInvalid(data,"Sum of declared field budgets")

    def test_authoritative_fields_cannot_be_client_mutable(self):
        data=copy.deepcopy(self.model); data["fields"][0]["client_mutable"]=True
        self.assertInvalid(data,"cannot be client_mutable")

    def test_client_mutable_setting_requires_server_validation(self):
        data=copy.deepcopy(self.model); data["fields"][-1]["server_validation_required"]=False
        self.assertInvalid(data,"require server_validation_required=true")

    def test_migration_chain_must_be_complete(self):
        data=copy.deepcopy(self.model); data["migrations"].pop(0)
        self.assertInvalid(data,"Missing migration step from schema version 1")

    def test_migration_must_advance_exactly_one_version(self):
        data=copy.deepcopy(self.model); data["migrations"][0]["to_version"]=3
        self.assertInvalid(data,"exactly one version step")

    def test_migration_must_be_idempotent(self):
        data=copy.deepcopy(self.model); data["migrations"][0]["idempotent"]=False
        self.assertInvalid(data,"idempotent must be true")

    def test_migration_requires_backup(self):
        data=copy.deepcopy(self.model); data["migrations"][0]["backup_required"]=False
        self.assertInvalid(data,"backup_required must be true")

    def test_migration_requires_test_cases(self):
        data=copy.deepcopy(self.model); data["migrations"][0]["test_case_ids"]=[]
        self.assertInvalid(data,"test_case_ids must contain")

    def test_duplicate_migration_id_rejected(self):
        data=copy.deepcopy(self.model); data["migrations"][1]["migration_id"]=data["migrations"][0]["migration_id"]
        self.assertInvalid(data,"Duplicate migration_id")

    def test_invalid_rollback_strategy_rejected(self):
        data=copy.deepcopy(self.model); data["migrations"][0]["rollback_strategy"]=[]
        self.assertInvalid(data,"rollback_strategy")

    def test_duplicate_transaction_operation_rejected(self):
        data=copy.deepcopy(self.model); data["transactions"].append(copy.deepcopy(data["transactions"][0]))
        self.assertInvalid(data,"Duplicate operation_id")

    def test_transaction_must_reference_known_field(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["dedupe_field_id"]="missing_ledger"
        self.assertInvalid(data,"must reference a declared")

    def test_transaction_dedupe_field_must_be_ledger_array(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["dedupe_field_id"]="inventory"
        self.assertInvalid(data,"category transaction_ledger")

    def test_receipt_uses_purchase_id(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["idempotency_key_source"]="server_operation_id"
        self.assertInvalid(data,"must be PurchaseId")

    def test_gameplay_reward_uses_server_operation_id(self):
        data=copy.deepcopy(self.model); data["transactions"][1]["idempotency_key_source"]="PurchaseId"
        self.assertInvalid(data,"must be server_operation_id")

    def test_effect_and_dedupe_marker_must_share_update(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["same_update_contains_effect_and_marker"]=False
        self.assertInvalid(data,"same_update_contains_effect_and_marker")

    def test_receipt_acknowledgement_requires_commit(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["acknowledge_after_commit"]=False
        self.assertInvalid(data,"acknowledge_after_commit")

    def test_concurrent_delivery_policy_is_serialized(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["concurrent_delivery_policy"]="best_effort"
        self.assertInvalid(data,"concurrent_delivery_policy")

    def test_unhashable_transaction_kind_is_safe(self):
        data=copy.deepcopy(self.model); data["transactions"][0]["transaction_kind"]=[]
        self.assertInvalid(data,"transaction_kind")

    def test_missing_migrations_allowed_for_first_schema(self):
        data=copy.deepcopy(self.model); data["profile_store"]["schema_version"]=1; data["profile_store"]["minimum_supported_version"]=1; data["migrations"]=[]
        self.assertEqual([],v40.validate_model(data))

class PersistenceAuditTests(unittest.TestCase):
    def setUp(self):
        self.model=json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_audit_report_is_repeatable(self):
        self.assertEqual(v40.audit_model(self.model),v40.audit_model(self.model))

    def test_audit_reports_field_migration_and_transaction_counts(self):
        report=v40.audit_model(self.model)
        self.assertEqual(5,report["summary"]["field_count"])
        self.assertEqual(2,report["summary"]["migration_step_count"])
        self.assertEqual(2,report["summary"]["transaction_definition_count"])

    def test_no_transaction_definitions_warn(self):
        model=copy.deepcopy(self.model); model["transactions"]=[]
        report=v40.audit_model(model)
        self.assertTrue(any("No transaction definitions" in warning for warning in report["warnings"]))

    def test_large_payload_budget_warns(self):
        model=copy.deepcopy(self.model); model["profile_store"]["profile_size_budget_bytes"]=4_000_000
        report=v40.audit_model(model)
        self.assertTrue(any("above 90%" in warning for warning in report["warnings"]))

    def test_high_declared_field_budget_warns(self):
        model=copy.deepcopy(self.model); model["fields"][0]["max_encoded_bytes"]=1_200_000
        report=v40.audit_model(model)
        self.assertTrue(any("more than 75%" in warning for warning in report["warnings"]))

    def test_close_autosave_and_lease_warn(self):
        model=copy.deepcopy(self.model); model["saving"]["autosave_interval_seconds"]=100
        report=v40.audit_model(model)
        self.assertTrue(any("close to the session lease" in warning for warning in report["warnings"]))

class PathSafetyTests(unittest.TestCase):
    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v40.safe_path(Path(temp),"../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v40.safe_path(Path(temp),"/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v40.safe_path(Path(temp),r"nested\model.json")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): v40.duplicate_keys([("x",1),("x",2)])

    def test_non_standard_constant_rejected(self):
        with self.assertRaises(ValueError): v40.reject_constant("NaN")

    def test_large_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"large.json").write_text(" "*(v40.MAX_INPUT_BYTES+1),encoding="utf-8")
            with self.assertRaises(ValueError): v40.load_model(root,"large.json")

    def test_symlink_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); outside=root.parent/"v40-symlink-test"; outside.mkdir(exist_ok=True)
            try:
                (root/"linked").symlink_to(outside,target_is_directory=True)
                with self.assertRaises(ValueError): v40.safe_path(root,"linked/file.json")
            finally: shutil.rmtree(outside,ignore_errors=True)

if __name__=="__main__": unittest.main()
