from __future__ import annotations
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
SPEC=importlib.util.spec_from_file_location("v45",ROOT/"tools"/"v45.py")
v45=importlib.util.module_from_spec(SPEC); assert SPEC and SPEC.loader; SPEC.loader.exec_module(v45)
EXAMPLE=json.loads((ROOT/"examples"/"narrative-project.example.json").read_text(encoding="utf-8"))
SCHEMA=json.loads((ROOT/"schemas"/"narrative-project.schema.json").read_text(encoding="utf-8"))
class ValidationTests(unittest.TestCase):
 def setUp(self): self.p=copy.deepcopy(EXAMPLE)
 def test_example_valid(self): self.assertEqual([],v45.validate_project(self.p))
 def test_bool_schema_rejected(self): self.p["schema_version"]=True; self.assertTrue(v45.validate_project(self.p))
 def test_unknown_field_rejected(self): self.p["extra"]="no"; self.assertTrue(any("unsupported fields" in e for e in v45.validate_project(self.p)))
 def test_default_locale_must_be_supported(self): self.p["default_locale"]="de-DE"; self.assertTrue(any("default_locale" in e for e in v45.validate_project(self.p)))
 def test_duplicate_locale_rejected(self): self.p["supported_locales"].append("en-US"); self.assertTrue(any("Duplicate supported locale" in e for e in v45.validate_project(self.p)))
 def test_missing_quest_start(self): self.p["quests"][0]["start_node_id"]="missing"; self.assertTrue(v45.validate_project(self.p))
 def test_duplicate_quest_node(self):
  q=self.p["quests"][0]; q["nodes"].append(copy.deepcopy(q["nodes"][0])); self.assertTrue(any("duplicate node_id" in e for e in v45.validate_project(self.p)))
 def test_missing_quest_edge(self): self.p["quests"][0]["nodes"][0]["next_node_ids"]=["missing"]; self.assertTrue(any("references missing node" in e for e in v45.validate_project(self.p)))
 def test_unreachable_quest_node(self):
  q=self.p["quests"][0]; q["nodes"].append({"node_id":"orphan","kind":"complete","title":"Orphan end","objective_type":None,"next_node_ids":[]})
  self.assertTrue(any("unreachable nodes" in e for e in v45.validate_project(self.p)))
 def test_quest_cycle(self): self.p["quests"][0]["nodes"][1]["next_node_ids"]=["approach-guide"]; self.assertTrue(any("contains a cycle" in e for e in v45.validate_project(self.p)))
 def test_quest_without_finish_path(self): self.p["quests"][0]["nodes"][1]["next_node_ids"]=[]; self.assertTrue(any("cannot reach a completion" in e for e in v45.validate_project(self.p)))
 def test_unhashable_quest_kind_is_reported(self):
  self.p["quests"][0]["nodes"][0]["kind"]=["objective"]; self.assertTrue(v45.validate_project(self.p))
 def test_unhashable_repeat_policy_is_reported(self):
  self.p["quests"][0]["repeat_policy"]=[]; self.assertTrue(v45.validate_project(self.p))
 def test_unhashable_objective_type_is_reported(self):
  self.p["quests"][0]["nodes"][0]["objective_type"]={}; self.assertTrue(v45.validate_project(self.p))
 def test_unhashable_dialogue_kind_is_reported(self):
  self.p["dialogues"][0]["nodes"][0]["kind"]={}; self.assertTrue(v45.validate_project(self.p))
 def test_branch_needs_multiple_edges(self): self.p["quests"][0]["nodes"][0]["kind"]="branch"; self.assertTrue(any("branch nodes must have" in e for e in v45.validate_project(self.p)))
 def test_missing_prerequisite(self): self.p["quests"][0]["prerequisites"]=["not-authored"]; self.assertTrue(any("missing prerequisite" in e for e in v45.validate_project(self.p)))
 def test_prerequisite_cycle(self):
  self.p["quests"][0]["prerequisites"]=["follow-up"]
  self.p["quests"].append({"quest_id":"follow-up","title":"Follow-up task","summary":"A sample dependent quest for the cycle test.","repeat_policy":"once","prerequisites":["meet-the-guide"],"start_node_id":"done","nodes":[{"node_id":"done","kind":"complete","title":"Done","objective_type":None,"next_node_ids":[]}]})
  self.assertTrue(any("prerequisite graph contains a cycle" in e for e in v45.validate_project(self.p)))
 def test_duplicate_dialogue_node(self):
  d=self.p["dialogues"][0]; d["nodes"].append(copy.deepcopy(d["nodes"][0])); self.assertTrue(any("duplicate node_id" in e for e in v45.validate_project(self.p)))
 def test_bad_dialogue_destination(self): self.p["dialogues"][0]["nodes"][0]["choices"][0]["next_node_id"]="missing"; self.assertTrue(any("references missing node" in e for e in v45.validate_project(self.p)))
 def test_unreachable_dialogue_node(self):
  d=self.p["dialogues"][0]; d["nodes"].append({"node_id":"orphan","kind":"end","speaker":"guide","text_key":"guide.orphan","text":"Unused ending.","choices":[]})
  self.assertTrue(any("unreachable nodes" in e for e in v45.validate_project(self.p)))
 def test_dialogue_node_without_end_path(self):
  d=self.p["dialogues"][0]; d["nodes"][0]["choices"][0]["next_node_id"]="directions"; d["nodes"][1]["choices"][0]["next_node_id"]="directions"
  self.assertTrue(any("cannot reach an ending" in e for e in v45.validate_project(self.p)))
 def test_dialogue_loop_with_exit_allowed(self):
  d=self.p["dialogues"][0]; d["nodes"][1]["choices"].append({"choice_id":"repeat-route","label_key":"guide.choice.repeat","label":"Repeat directions","next_node_id":"greeting"})
  self.assertEqual([],v45.validate_project(self.p))
 def test_duplicate_text_key(self): self.p["dialogues"][0]["nodes"][1]["text_key"]="guide.greeting"; self.assertTrue(any("Duplicate localization key" in e for e in v45.validate_project(self.p)))
 def test_line_requires_choice(self): self.p["dialogues"][0]["nodes"][0]["choices"]=[]; self.assertTrue(v45.validate_project(self.p))
 def test_end_has_no_choices(self):
  self.p["dialogues"][0]["nodes"][-1]["choices"]=[{"choice_id":"x","label_key":"x.label","label":"Continue","next_node_id":"greeting"}]
  self.assertTrue(v45.validate_project(self.p))
 def test_audit_reports_human_review(self): self.assertTrue(v45.audit_project(self.p)["human_review_required"])
 def test_invalid_audit_blocked(self): self.p["quests"][0]["start_node_id"]="missing"; self.assertEqual("blocked",v45.audit_project(self.p)["status"])
class SecurityAndSchemaTests(unittest.TestCase):
 def test_schema_example(self):
  Draft202012Validator.check_schema(SCHEMA); self.assertEqual([],list(Draft202012Validator(SCHEMA,format_checker=FormatChecker()).iter_errors(EXAMPLE)))
 def test_duplicate_json_key(self):
  with self.assertRaises(ValueError): v45._pairs_no_duplicates([("id",1),("id",2)])
 def test_nonstandard_constant(self):
  with self.assertRaises(ValueError): v45._reject_constant("NaN")
 def test_unsafe_paths(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(ValueError): v45.safe_path(Path(temp),"../outside.json")
   with self.assertRaises(ValueError): v45.safe_path(Path(temp),"/etc/passwd")
 def test_windows_path(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(ValueError): v45.safe_path(Path(temp),r"nested\input.json")
 def test_input_limit(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp); (root/"big.json").write_text(" "*(v45.MAX_INPUT_BYTES+1),encoding="utf-8")
   with self.assertRaises(ValueError): v45.load_json(root,"big.json")
 def test_atomic_report(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp); v45.write_report(root,"reports/audit.json",{"status":"ok"})
   self.assertEqual({"status":"ok"},json.loads((root/"reports"/"audit.json").read_text(encoding="utf-8")))
if __name__=="__main__": unittest.main()
