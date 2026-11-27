from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import v36\nimport audit_cumulative_package

def surface(**changes):
    row={"surface_id":"main-menu","kind":"menu","platforms":["desktop","mobile"],"input_methods":["keyboard_mouse","touch"],"uses_motion":True,"critical_audio":True,
    "localization":{"strings_externalized":True,"text_expansion_tested":True,"rtl_reviewed":True},
    "accessibility":{"focus_navigation":True,"text_scaling":True,"non_color_cues":True,"contrast_reviewed":True,"critical_audio_captions":True,"reduced_motion_option":True},
    "evidence_refs":["ev-111122223333"]}
    row.update(changes); return row

def manifest(*surfaces):
    return {"schema_version":1,"project_key":"sample-game","generated_at":"2026-11-27T12:00:00Z","target_locales":["en-us","ar"],"surfaces":list(surfaces) if surfaces else [surface()]}

class V36Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name).resolve()
    def tearDown(self): self.tmp.cleanup()
    def test_readme_preserves_all_cumulative_skill_count_labels(self):\n        readme=(Path(__file__).resolve().parents[2]/"README.md").read_text(encoding="utf-8")\n        self.assertEqual([x for x in audit_cumulative_package.HISTORICAL_SKILL_LABELS if x not in readme],[])\n    def test_valid_manifest(self): self.assertEqual(v36.validate_manifest(manifest()),[])
    def test_reject_unknown_root_field(self):
        data=manifest(); data["player_data"]=[]
        self.assertTrue(any("unsupported fields" in x for x in v36.validate_manifest(data)))
    def test_reject_unknown_surface_field(self):
        row=surface(); row["private_notes"]="x"
        self.assertTrue(any("unsupported fields" in x for x in v36.validate_manifest(manifest(row))))
    def test_reject_duplicate_surface(self): self.assertTrue(any("Duplicate surface_id" in x for x in v36.validate_manifest(manifest(surface(),surface()))))
    def test_reject_bad_locale(self):
        data=manifest(); data["target_locales"]=["english!"]
        self.assertTrue(any("target_locales" in x for x in v36.validate_manifest(data)))
    def test_reject_bad_evidence_ref(self):
        row=surface(evidence_refs=["https://example.com"])
        self.assertTrue(any("opaque ev-" in x for x in v36.validate_manifest(manifest(row))))
    def test_reject_pathological_json_types(self):
        row=surface(platforms=[[]])
        self.assertTrue(v36.validate_manifest(manifest(row)))
    def test_reject_bad_bool(self):
        row=surface(uses_motion="yes")
        self.assertTrue(any("must be boolean" in x for x in v36.validate_manifest(manifest(row))))
    def test_rtl_gap_detected(self):
        row=surface(localization={"strings_externalized":True,"text_expansion_tested":True,"rtl_reviewed":False})
        report=v36.audit_manifest(manifest(row))
        self.assertIn("rtl_review_missing",{x["code"] for x in report["findings"]})
    def test_focus_navigation_blocker(self):
        acc=surface()["accessibility"]; acc["focus_navigation"]=False
        report=v36.audit_manifest(manifest(surface(accessibility=acc)))
        self.assertIn("focus_navigation_missing",{x["code"] for x in report["findings"]})
    def test_audio_alternative_blocker(self):
        acc=surface()["accessibility"]; acc["critical_audio_captions"]=False
        report=v36.audit_manifest(manifest(surface(accessibility=acc)))
        self.assertIn("critical_audio_alternative_missing",{x["code"] for x in report["findings"]})
    def test_motion_warning(self):
        acc=surface()["accessibility"]; acc["reduced_motion_option"]=False
        report=v36.audit_manifest(manifest(surface(accessibility=acc)))
        self.assertIn("reduced_motion_unverified",{x["code"] for x in report["findings"]})
    def test_strings_not_externalized_blocker(self):
        loc=surface()["localization"]; loc["strings_externalized"]=False
        report=v36.audit_manifest(manifest(surface(localization=loc)))
        self.assertIn("strings_not_externalized",{x["code"] for x in report["findings"]})
    def test_non_color_cue_blocker(self):
        acc=surface()["accessibility"]; acc["non_color_cues"]=False
        report=v36.audit_manifest(manifest(surface(accessibility=acc)))
        self.assertIn("non_color_cues_missing",{x["code"] for x in report["findings"]})
    def test_missing_text_expansion_warning(self):
        loc=surface()["localization"]; loc["text_expansion_tested"]=False
        report=v36.audit_manifest(manifest(surface(localization=loc)))
        self.assertIn("text_expansion_unverified",{x["code"] for x in report["findings"]})
    def test_no_rtl_target_no_rtl_warning(self):
        data=manifest(); data["target_locales"]=["en-us"]
        self.assertNotIn("rtl_review_missing",{x["code"] for x in v36.audit_manifest(data)["findings"]})
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError): v36.safe_path(self.root,"../outside.json")
    def test_absolute_path_rejected(self):
        with self.assertRaises(ValueError): v36.safe_path(self.root,"C:/outside.json")
    def test_symlink_rejected(self):
        outside=self.root.parent/"v36-outside.txt"; outside.write_text("x")
        link=self.root/"alias.txt"
        try: link.symlink_to(outside)
        except (OSError,NotImplementedError): outside.unlink(); self.skipTest("Symlinks unavailable.")
        with self.assertRaises(ValueError): v36.safe_path(self.root,"alias.txt")
        outside.unlink()
    def test_valid_report_no_findings(self):
        report=v36.audit_manifest(manifest())
        self.assertEqual(report["summary"]["findings"],0)
        self.assertEqual(report["status"],"reviewed_no_findings")
    def test_blocker_count(self):
        report=v36.audit_manifest(manifest(surface(critical_audio=True,accessibility={**surface()["accessibility"],"critical_audio_captions":False})))
        self.assertGreater(report["summary"]["blockers"],0)
    def test_output_is_written_inside_project(self):
        v36.write_json(self.root,"reports/audit.json",{"ok":True})
        self.assertTrue((self.root/"reports"/"audit.json").is_file())
    def test_output_traversal_rejected(self):
        with self.assertRaises(ValueError): v36.write_json(self.root,"../escape.json",{"ok":True})

if __name__=="__main__": unittest.main()
