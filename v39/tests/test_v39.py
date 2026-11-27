from __future__ import annotations
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import v39

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/"examples"/"economy-model.example.json"

class EconomyModelValidationTests(unittest.TestCase):
    def setUp(self):
        self.model=json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assertInvalid(self,model,fragment):
        errors=v39.validate_model(model)
        self.assertTrue(any(fragment in x for x in errors),errors)

    def test_example_is_valid(self):
        self.assertEqual([],v39.validate_model(self.model))

    def test_unknown_top_level_field_rejected(self):
        data=copy.deepcopy(self.model); data["player_ids"]=[]
        self.assertInvalid(data,"unsupported fields")

    def test_missing_top_level_field_rejected(self):
        data=copy.deepcopy(self.model); del data["horizon_days"]
        self.assertInvalid(data,"missing")

    def test_invalid_model_id_rejected(self):
        data=copy.deepcopy(self.model); data["model_id"]="../model"
        self.assertInvalid(data,"model_id")

    def test_horizon_over_limit_rejected(self):
        data=copy.deepcopy(self.model); data["horizon_days"]=366
        self.assertInvalid(data,"horizon_days")

    def test_boolean_horizon_rejected(self):
        data=copy.deepcopy(self.model); data["horizon_days"]=True
        self.assertInvalid(data,"horizon_days")

    def test_duplicate_currency_id_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"].append(copy.deepcopy(data["currencies"][0]))
        self.assertInvalid(data,"Duplicate currency_id")

    def test_bad_currency_kind_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["kind"]="premium"
        self.assertInvalid(data,"kind")

    def test_unhashable_currency_kind_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["kind"]={}
        self.assertInvalid(data,"kind")

    def test_negative_starting_balance_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["starting_balance"]=-1
        self.assertInvalid(data,"starting_balance")

    def test_boolean_amount_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["sources"][0]["amount_per_active_day"]=True
        self.assertInvalid(data,"amount_per_active_day")

    def test_duplicate_source_component_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["sources"].append(copy.deepcopy(data["currencies"][0]["sources"][0]))
        self.assertInvalid(data,"duplicates component_id")

    def test_unknown_currency_reward_rejected(self):
        data=copy.deepcopy(self.model); data["progression"]["levels"][0]["rewards"][0]["currency_id"]="unknown"
        self.assertInvalid(data,"unknown currency")

    def test_level_sequence_rejected(self):
        data=copy.deepcopy(self.model); data["progression"]["levels"][1]["level"]=4
        self.assertInvalid(data,"sequential")

    def test_non_increasing_xp_threshold_rejected(self):
        data=copy.deepcopy(self.model); data["progression"]["levels"][1]["xp_required"]=200
        self.assertInvalid(data,"thresholds must increase")

    def test_unhashable_cohort_fields_handled(self):
        data=copy.deepcopy(self.model); data["cohorts"][0]["cohort_id"]=[]
        self.assertInvalid(data,"cohort_id")

    def test_duplicate_cohort_id_rejected(self):
        data=copy.deepcopy(self.model); data["cohorts"][1]["cohort_id"]=data["cohorts"][0]["cohort_id"]
        self.assertInvalid(data,"Duplicate cohort_id")

    def test_activity_days_bounds(self):
        data=copy.deepcopy(self.model); data["cohorts"][0]["active_days_per_week"]=8
        self.assertInvalid(data,"active_days_per_week")

    def test_activity_multiplier_bounds(self):
        data=copy.deepcopy(self.model); data["cohorts"][0]["activity_multiplier_bps"]=25000
        self.assertInvalid(data,"activity_multiplier_bps")

    def test_boolean_level_threshold_rejected(self):
        data=copy.deepcopy(self.model); data["progression"]["levels"][0]["xp_required"]=True
        self.assertInvalid(data,"xp_required")

    def test_extra_currency_field_rejected(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["robux_price"]=10
        self.assertInvalid(data,"unsupported fields")

    def test_currency_count_limit(self):
        data=copy.deepcopy(self.model)
        data["currencies"]=[{"currency_id":f"currency_{i}","kind":"soft","starting_balance":0,"healthy_balance_ceiling":100,"sources":[],"sinks":[]} for i in range(9)]
        self.assertInvalid(data,"currencies must contain")

    def test_component_count_limit(self):
        data=copy.deepcopy(self.model); data["currencies"][0]["sources"]=[{"component_id":f"source_{i}","amount_per_active_day":1} for i in range(21)]
        self.assertInvalid(data,"at most 20")

class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.model=json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_simulation_is_deterministic(self):
        self.assertEqual(v39.simulate_model(self.model),v39.simulate_model(self.model))

    def test_three_synthetic_cohorts_are_reported(self):
        report=v39.simulate_model(self.model)
        self.assertEqual(3,report["summary"]["cohort_count"])
        self.assertEqual({"low_activity","regular_activity","high_activity"},{x["cohort_id"] for x in report["cohorts"]})

    def test_active_day_counts_are_bounded_by_horizon(self):
        report=v39.simulate_model(self.model)
        self.assertTrue(all(0<=x["active_days"]<=30 for x in report["cohorts"]))

    def test_sources_are_earned(self):
        report=v39.simulate_model(self.model)
        coins=report["cohorts"][1]["currencies"][0]
        self.assertGreater(coins["source_earned"],0)

    def test_sink_shortfall_reported(self):
        model=copy.deepcopy(self.model); model["currencies"][0]["sinks"][0]["amount_per_active_day"]=100000
        report=v39.simulate_model(model)
        self.assertGreater(report["cohorts"][0]["currencies"][0]["sink_shortfall"],0)
        self.assertTrue(any("shortfall" in x for x in report["warnings"]))

    def test_balance_ceiling_warning_reported(self):
        model=copy.deepcopy(self.model); model["currencies"][0]["healthy_balance_ceiling"]=1
        report=v39.simulate_model(model)
        self.assertTrue(any("exceeds review ceiling" in x for x in report["warnings"]))

    def test_progression_gap_warning_reported(self):
        model=copy.deepcopy(self.model); model["progression"]["level_gap_warning"]=1
        report=v39.simulate_model(model)
        self.assertTrue(any("progression gap" in x for x in report["warnings"]))

    def test_progression_rewards_are_granted(self):
        report=v39.simulate_model(self.model)
        high=next(x for x in report["cohorts"] if x["cohort_id"]=="high_activity")
        self.assertGreater(high["currencies"][0]["progression_rewards"],0)

    def test_unspent_balance_never_negative(self):
        model=copy.deepcopy(self.model); model["currencies"][0]["sinks"][0]["amount_per_active_day"]=1000000
        report=v39.simulate_model(model)
        self.assertTrue(all(c["closing_balance"]>=0 for cohort in report["cohorts"] for c in cohort["currencies"]))

    def test_sources_without_sinks_warn(self):
        model=copy.deepcopy(self.model); model["currencies"][0]["sinks"]=[]
        report=v39.simulate_model(model)
        self.assertTrue(any("no sinks" in x for x in report["warnings"]))

    def test_deterministic_integer_rounding(self):
        model=copy.deepcopy(self.model)
        model["horizon_days"]=7
        model["currencies"][0]["sources"]=[{"component_id":"tiny","amount_per_active_day":1}]
        model["currencies"][0]["sinks"]=[]
        model["cohorts"]=[{"cohort_id":"low","active_days_per_week":7,"activity_multiplier_bps":5000},{"cohort_id":"high","active_days_per_week":7,"activity_multiplier_bps":10000}]
        model["currencies"]=model["currencies"][:1]
        model["progression"]["levels"]=[]
        report=v39.simulate_model(model)
        self.assertEqual(0,report["cohorts"][0]["currencies"][0]["source_earned"])
        self.assertEqual(7,report["cohorts"][1]["currencies"][0]["source_earned"])

    def test_report_does_not_claim_live_observation(self):
        report=v39.simulate_model(self.model)
        self.assertTrue(any("not observed player behavior" in x for x in report["limitations"]))

class PathSafetyTests(unittest.TestCase):
    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v39.safe_path(Path(temp),"../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v39.safe_path(Path(temp),"/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v39.safe_path(Path(temp),r"nested\model.json")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): v39.duplicate_keys([("x",1),("x",2)])

    def test_non_standard_constant_rejected(self):
        with self.assertRaises(ValueError): v39.reject_constant("NaN")

    def test_large_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"large.json").write_text(" "*(v39.MAX_BYTES+1),encoding="utf-8")
            with self.assertRaises(ValueError): v39.load_model(root,"large.json")

    def test_symlink_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); outside=root.parent/"v39-symlink-test"; outside.mkdir(exist_ok=True)
            try:
                (root/"linked").symlink_to(outside,target_is_directory=True)
                with self.assertRaises(ValueError): v39.safe_path(root,"linked/file.json")
            finally: shutil.rmtree(outside,ignore_errors=True)

if __name__=="__main__": unittest.main()
