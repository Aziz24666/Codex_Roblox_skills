from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import v38

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "incident.example.json"

class IncidentValidationTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assertInvalid(self, data, fragment):
        messages=v38.validate_incident(data)
        self.assertTrue(any(fragment in item for item in messages), messages)

    def test_example_is_valid(self):
        self.assertEqual([],v38.validate_incident(self.data))

    def test_unknown_top_level_key_is_rejected(self):
        data=copy.deepcopy(self.data); data["secret"]="unexpected"
        self.assertInvalid(data,"unsupported fields")

    def test_missing_top_level_key_is_rejected(self):
        data=copy.deepcopy(self.data); del data["summary"]
        self.assertInvalid(data,"missing")

    def test_invalid_incident_id_is_rejected(self):
        data=copy.deepcopy(self.data); data["incident_id"]="INC-123"
        self.assertInvalid(data,"incident_id")

    def test_non_slug_project_key_is_rejected(self):
        data=copy.deepcopy(self.data); data["project_key"]="../game"
        self.assertInvalid(data,"project_key")

    def test_naive_timestamp_is_rejected(self):
        data=copy.deepcopy(self.data); data["opened_at"]="2026-11-27T10:00:00"
        self.assertInvalid(data,"opened_at")

    def test_detected_time_before_opened_is_rejected(self):
        data=copy.deepcopy(self.data); data["detected_at"]="2026-11-27T09:00:00Z"
        self.assertInvalid(data,"detected_at cannot precede")

    def test_bool_schema_version_is_rejected(self):
        data=copy.deepcopy(self.data); data["schema_version"]=True
        self.assertInvalid(data,"schema_version")

    def test_unreviewed_impact_privacy_is_rejected(self):
        data=copy.deepcopy(self.data); data["impact"]["privacy_reviewed"]=False
        self.assertInvalid(data,"privacy_reviewed")

    def test_non_private_detection_is_rejected(self):
        data=copy.deepcopy(self.data); data["detection"]["privacy_safe"]=False
        self.assertInvalid(data,"detection.privacy_safe")

    def test_invalid_signal_reference_is_rejected(self):
        data=copy.deepcopy(self.data); data["detection"]["signal_refs"]=["raw-player-identifier"]
        self.assertInvalid(data,"opaque reference")

    def test_high_incident_requires_technical_lead(self):
        data=copy.deepcopy(self.data); data["roles"]=[x for x in data["roles"] if x["role"]!="technical_lead"]
        self.assertInvalid(data,"technical_lead")

    def test_duplicate_role_is_rejected(self):
        data=copy.deepcopy(self.data); data["roles"].append(copy.deepcopy(data["roles"][0]))
        self.assertInvalid(data,"duplicate role")

    def test_timeline_must_start_with_detection(self):
        data=copy.deepcopy(self.data); data["timeline"][0]["event_type"]="triaged"
        self.assertInvalid(data,"first timeline event")

    def test_non_chronological_timeline_is_rejected(self):
        data=copy.deepcopy(self.data); data["timeline"][1]["occurred_at"]="2026-11-27T10:01:00Z"
        self.assertInvalid(data,"chronological")

    def test_duplicate_timeline_id_is_rejected(self):
        data=copy.deepcopy(self.data); data["timeline"][1]["event_id"]=data["timeline"][0]["event_id"]
        self.assertInvalid(data,"duplicate event_id")

    def test_high_risk_action_requires_approval(self):
        data=copy.deepcopy(self.data); data["actions"][0]["requires_approval"]=False
        self.assertInvalid(data,"requires human approval")

    def test_applied_action_requires_passed_verification(self):
        data=copy.deepcopy(self.data); action=data["actions"][0]
        action.update(status="applied",approval_ref="apr-approval1",approved_at="2026-11-27T10:10:00Z",verification_status="not_run")
        self.assertInvalid(data,"must pass verification")

    def test_applied_action_requires_approval_reference(self):
        data=copy.deepcopy(self.data); action=data["actions"][0]
        action.update(status="applied",approved_at="2026-11-27T10:10:00Z",verification_status="pass",verification_ref="ev-111122223333")
        self.assertInvalid(data,"approval_ref")

    def test_required_player_notice_must_be_reviewed_before_close(self):
        data=copy.deepcopy(self.data); data["status"]="resolved"
        data["resolution"].update(resolved_at="2026-11-27T10:12:00Z",verification_ref="ev-111122223333",customer_impact_closed=True)
        data["timeline"].append({"event_id":"evt-resolved01","occurred_at":"2026-11-27T10:12:00Z","event_type":"resolved","summary":"Service health verified after observation.","evidence_refs":["ev-111122223333"]})
        data["resolution"].update(postmortem_ref="pm-postmortem1",follow_up_ref="issue-followup1")
        self.assertInvalid(data,"must be reviewed")

    def test_critical_resolution_requires_postmortem_and_followup(self):
        data=copy.deepcopy(self.data); data["severity"]="critical"; data["status"]="resolved"
        data["communications"].update(player_notice_required=False,player_notice_reviewed=False)
        data["resolution"].update(resolved_at="2026-11-27T10:12:00Z",verification_ref="ev-111122223333",customer_impact_closed=True)
        data["timeline"].append({"event_id":"evt-resolved01","occurred_at":"2026-11-27T10:12:00Z","event_type":"resolved","summary":"Service health verified after observation.","evidence_refs":["ev-111122223333"]})
        self.assertInvalid(data,"postmortem_ref")

    def test_unresolved_incident_cannot_have_resolved_event(self):
        data=copy.deepcopy(self.data)
        data["timeline"].append({"event_id":"evt-resolved01","occurred_at":"2026-11-27T10:12:00Z","event_type":"resolved","summary":"Resolved event should not appear on open incident.","evidence_refs":[]})
        self.assertInvalid(data,"cannot include a resolved event")

    def test_unhashable_enum_values_are_reported_not_crashes(self):
        data=copy.deepcopy(self.data); data["severity"]={}; data["status"]=[]
        data["roles"][0]["role"]={}; data["timeline"][0]["event_type"]=[]
        self.assertTrue(v38.validate_incident(data))

class AuditTests(unittest.TestCase):
    def test_audit_flags_unacknowledged_and_pending_action(self):
        data=json.loads(EXAMPLE.read_text(encoding="utf-8")); result=v38.audit_incident(data)
        self.assertEqual("human_action_required",result["status"])
        self.assertEqual(1,result["pending_approval_count"] if "pending_approval_count" in result else result["summary"]["pending_approval_count"])
        self.assertTrue(result["warnings"])

    def test_audit_does_not_claim_to_execute(self):
        data=json.loads(EXAMPLE.read_text(encoding="utf-8")); result=v38.audit_incident(data)
        self.assertTrue(any("does not query Roblox" in item for item in result["limitations"]))

class PathSafetyTests(unittest.TestCase):
    def test_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v38.safe_path(Path(temp),"../outside.json")

    def test_absolute_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v38.safe_path(Path(temp),"/tmp/outside.json")

    def test_backslash_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): v38.safe_path(Path(temp),r"nested\incident.json")

    def test_symlink_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); outside=root.parent/"v38-outside"; outside.mkdir(exist_ok=True)
            try:
                (root/"linked").symlink_to(outside,target_is_directory=True)
                with self.assertRaises(ValueError): v38.safe_path(root,"linked/file.json")
            finally:
                import shutil
                shutil.rmtree(outside,ignore_errors=True)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): v38.duplicate_keys([("a",1),("a",2)])

    def test_non_standard_json_constants_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"bad.json").write_text('{"value": NaN}',encoding="utf-8")
            with self.assertRaises(ValueError): v38.load_json(root,"bad.json")

    def test_large_json_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"large.json").write_text(" "* (v38.MAX_BYTES+1),encoding="utf-8")
            with self.assertRaises(ValueError): v38.load_json(root,"large.json")

if __name__=="__main__": unittest.main()
