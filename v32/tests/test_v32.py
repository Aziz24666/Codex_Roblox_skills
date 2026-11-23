from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import v32  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402

class Fixtures(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name).resolve()
    def tearDown(self): self.temp.cleanup()
    def put(self,relative,content):
        p=self.root/relative; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8"); return p
    def policy(self):
        return {"schema_version":1,"review_sla_hours":{"low":168,"standard":72,"high":24,"critical":2},"evidence_retention_days":30,"appeal_window_days":30,"require_second_review_for":["high","critical"],"automated_enforcement":False}
    def case(self,**kw):
        d={"schema_version":1,"case_ref":"case-2f4b8c1d9e0a","created_at":"2026-11-20T11:00:00Z","source":"platform_report","category":"harassment","channel":"text","severity":"standard","status":"open","summary_code":"user_report_submitted","evidence_refs":["ev-2f4b8c1d9e0a"]}
        d.update(kw); return d

class PolicyTests(Fixtures):
    def test_valid_policy(self): self.assertEqual(v32.validate_policy(self.policy()),[])
    def test_automated_enforcement_forbidden(self):
        p=self.policy(); p["automated_enforcement"]=True
        self.assertTrue(any("must be false" in x for x in v32.validate_policy(p)))
    def test_exact_sla_severity_set_required(self):
        p=self.policy(); del p["review_sla_hours"]["critical"]
        self.assertTrue(any("exactly low, standard, high, and critical" in x for x in v32.validate_policy(p)))
    def test_retention_is_bounded(self):
        p=self.policy(); p["evidence_retention_days"]=1000
        self.assertTrue(any("no greater than 365" in x for x in v32.validate_policy(p)))
    def test_second_review_only_high_or_critical(self):
        p=self.policy(); p["require_second_review_for"]=["low"]
        self.assertTrue(any("only be required for high or critical" in x for x in v32.validate_policy(p)))
    def test_unknown_policy_fields_rejected(self):
        p=self.policy(); p["free_text_notes"]="private"
        self.assertTrue(any("unsupported fields" in x for x in v32.validate_policy(p)))
    def test_malformed_review_list_does_not_crash(self):
        p=self.policy(); p["require_second_review_for"]=[{"severity":"high"}]
        self.assertTrue(v32.validate_policy(p))

class CaseTests(Fixtures):
    def test_valid_open_case(self): self.assertEqual(v32.validate_case(self.case(),self.policy()),[])
    def test_valid_resolved_case(self):
        c=self.case(status="resolved",reviewed_at="2026-11-20T12:00:00Z",reviewer_role="moderator",decision_code="policy_reminder")
        self.assertEqual(v32.validate_case(c,self.policy()),[])
    def test_identifiers_and_raw_content_fields_rejected(self):
        for key in ("target_user_id","reporter_user_id","username","raw_chat","message_text","free_text_notes"):
            c=self.case(); c[key]="not accepted"
            self.assertTrue(any("unsupported fields" in x for x in v32.validate_case(c,self.policy())),key)
    def test_case_reference_must_be_opaque(self):
        c=self.case(case_ref="https://example.test/report/1")
        self.assertTrue(any("opaque case-" in x for x in v32.validate_case(c,self.policy())))
    def test_evidence_references_are_opaque_and_unique(self):
        c=self.case(evidence_refs=["https://example.test/evidence"])
        self.assertTrue(any("opaque ev-" in x for x in v32.validate_case(c,self.policy())))
        c=self.case(evidence_refs=["ev-2f4b8c1d9e0a"]*2)
        self.assertTrue(any("unique opaque" in x for x in v32.validate_case(c,self.policy())))
    def test_evidence_reference_count_bounded(self):
        c=self.case(evidence_refs=[f"ev-{i:012d}" for i in range(9)])
        self.assertTrue(any("at most eight" in x for x in v32.validate_case(c,self.policy())))
    def test_final_state_requires_reviewer_decision(self):
        e=v32.validate_case(self.case(status="closed"),self.policy())
        self.assertTrue(any("requires reviewed_at" in x for x in e))
        self.assertTrue(any("requires a reviewer_role" in x for x in e))
        self.assertTrue(any("requires a decision_code" in x for x in e))
    def test_review_time_cannot_precede_creation(self):
        c=self.case(status="resolved",reviewed_at="2026-11-19T11:00:00Z",reviewer_role="moderator",decision_code="no_action")
        self.assertTrue(any("cannot be earlier" in x for x in v32.validate_case(c,self.policy())))
    def test_appeal_pending_needs_opaque_reference(self):
        c=self.case(status="appeal_pending",reviewed_at="2026-11-20T12:00:00Z",reviewer_role="moderator",decision_code="policy_reminder",appeal_ref="bad",appeal_outcome="pending")
        self.assertTrue(any("opaque appeal-" in x for x in v32.validate_case(c,self.policy())))
    def test_appeal_resolved_requires_final_outcome(self):
        c=self.case(status="appeal_resolved",reviewed_at="2026-11-20T12:00:00Z",reviewer_role="moderator",decision_code="policy_reminder",appeal_ref="appeal-2f4b8c1d9e0a",appeal_outcome="pending")
        self.assertTrue(any("upheld, modified, or overturned" in x for x in v32.validate_case(c,self.policy())))
    def test_high_severity_requires_second_reviewer(self):
        c=self.case(severity="high",status="resolved",reviewed_at="2026-11-20T12:00:00Z",reviewer_role="moderator",decision_code="temporary_feature_restriction")
        self.assertTrue(any("requires a recorded second reviewer" in x for x in v32.validate_case(c,self.policy())))
        c["second_reviewer_role"]="safety_lead"; self.assertEqual(v32.validate_case(c,self.policy()),[])
    def test_second_reviewer_role_must_differ(self):
        c=self.case(severity="critical",status="resolved",reviewed_at="2026-11-20T12:00:00Z",reviewer_role="safety_lead",second_reviewer_role="safety_lead",decision_code="refer_to_platform")
        self.assertTrue(any("different role" in x for x in v32.validate_case(c,self.policy())))
    def test_free_text_summary_rejected(self):
        c=self.case(summary_code="a player said something at 12:03")
        self.assertTrue(any("predefined code" in x for x in v32.validate_case(c,self.policy())))
    def test_timestamps_require_timezone(self):
        c=self.case(created_at="2026-11-20T11:00:00")
        self.assertTrue(any("timezone" in x for x in v32.validate_case(c,self.policy())))
    def test_malformed_enum_types_do_not_crash(self):
        c=self.case(source=["bad"],status=["bad"],severity={"x":1})
        self.assertTrue(v32.validate_case(c,self.policy()))

class RegisterTests(Fixtures):
    def test_duplicate_case_reference_rejected(self):
        reg={"schema_version":1,"cases":[self.case(),self.case()]}
        self.assertTrue(any("Duplicate case_ref" in x for x in v32.validate_register(reg,self.policy())))
    def test_register_schema_fields_are_strict(self):
        reg={"schema_version":1,"cases":[],"player_records":[]}
        self.assertTrue(any("only schema_version and cases" in x for x in v32.validate_register(reg,self.policy())))

class AuditTests(Fixtures):
    def test_filtering_and_raw_display_inventory(self):
        self.put("ServerScriptService/Text.server.lua",'local TextService=game:GetService("TextService")\nlocal TextChatService=game:GetService("TextChatService")\nTextService:FilterStringAsync(rawText,player.UserId)\nTextLabel.Text=inputText\n')
        r=v32.audit_project(self.root)
        self.assertEqual(r["inventory"]["text_service_filter_calls"],1)
        self.assertEqual(r["inventory"]["text_chat_service_get_service_calls"],1)
        self.assertEqual(r["inventory"]["possible_raw_text_sinks"],1)
        self.assertTrue(any(x["code"]=="possible_unfiltered_text_display" for x in r["findings"]))
    def test_legacy_chat_filter_flagged(self):
        self.put("Server/Legacy.server.lua","Chat:FilterStringAsync(rawText,player,receiver)\n")
        self.assertTrue(any(x["code"]=="legacy_chat_filter_api" for x in v32.audit_project(self.root)["findings"]))
    def test_client_text_filter_flagged(self):
        self.put("StarterPlayer/StarterPlayerScripts/Text.client.lua","TextService:FilterStringAsync(rawText,player.UserId)\n")
        self.assertTrue(any(x["code"]=="text_filter_call_in_client_context" for x in v32.audit_project(self.root)["findings"]))
    def test_audit_does_not_copy_source_or_player_text(self):
        self.put("Server/Leak.server.lua",'local rawText="private player content"\nTextLabel.Text=rawText\n')
        report=json.dumps(v32.audit_project(self.root))
        self.assertNotIn("private player content",report); self.assertNotIn("rawText=",report)
    def test_scan_limit_and_symlink(self):
        self.put("a.lua","return true\n"); self.put("b.lua","return true\n")
        r=v32.audit_project(self.root,max_files=1)
        self.assertEqual(r["inventory"]["luau_files_discovered"],1)
        self.assertTrue(any("file scan limit" in x for x in r["warnings"]))
        real=self.put("real.lua","return true\n"); link=self.root/"linked.lua"
        try: link.symlink_to(real)
        except (OSError,NotImplementedError): self.skipTest("Symlinks unavailable.")
        warnings=[]; found=v32.iter_luau_files(self.root,100,warnings)
        self.assertNotIn(link,found); self.assertTrue(any("symlink" in x for x in warnings))

class PackageTests(Fixtures):
    def test_patch_is_idempotent_and_audit_passes(self):
        source=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp); skills=package/".agents"/"skills"
            for i in range(228):
                p=skills/f"legacy-{i:03}"/"SKILL.md"; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(f"---\nname: legacy-{i:03}\ndescription: Legacy skill {i}.\n---\n",encoding="utf-8")
            (package/"AGENTS.md").write_text("# Agent rules\nNo gambling.\n",encoding="utf-8")
            for name in audit_cumulative_package.REQUIRED_FILES:
                if name.startswith(".agents/skills/") or name.startswith("v32/"): continue
                p=package/name; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text("{}\n" if name.endswith(".json") else "# Fixture\n",encoding="utf-8")
            patch_cumulative_package.patch(package,source); patch_cumulative_package.patch(package,source)
            agents=(package/"AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER),1)
            self.assertEqual(audit_cumulative_package.audit(package),[])

if __name__=="__main__": unittest.main()
