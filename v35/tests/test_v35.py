from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import v35
import patch_cumulative_package
import audit_cumulative_package

def asset(key="wooden-crate",**changes):
    row={"asset_key":key,"kind":"mesh","source_kind":"studio_created","provider_asset_id":"rbx-12345","ownership_scope":"group","rights_status":"cleared","moderation_status":"not_applicable","lifecycle":"approved","version":"1.0.0","dependencies":[],"targets":["low_end_mobile","mobile"],"measurements":{"mesh_triangles":10000,"file_size_bytes":120000},"provenance_ref":"ev-111122223333","review_ref":"ev-222233334444"}
    row.update(changes); return row

def catalog(*assets):
    return {"schema_version":1,"catalog_id":"asset-catalog-a13b9c7d2e4f","project_key":"sample-game","generated_at":"2026-11-27T12:00:00Z","assets":list(assets) if assets else [asset()]}

def policy():
    return {"schema_version":1,"policy_id":"asset-policy-a13b9c7d2e4f","profiles":{"low_end_mobile":{"max_file_size_bytes":8000000,"max_texture_pixels":1048576,"max_mesh_triangles":30000,"max_audio_duration_seconds":30,"max_animation_keyframes":180},"mobile":{"max_file_size_bytes":16000000,"max_texture_pixels":4194304,"max_mesh_triangles":60000,"max_audio_duration_seconds":60,"max_animation_keyframes":300}},"release_requires_cleared_rights":True,"release_requires_approved_moderation":True,"release_requires_approved_dependencies":True}

class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name).resolve()
    def tearDown(self): self.temp.cleanup()
    def put(self,rel,data):
        path=self.root/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data),encoding="utf-8"); return path

class CatalogValidationTests(Fixture):
    def test_valid_catalog(self): self.assertEqual(v35.validate_catalog(catalog(),self.root),[])
    def test_catalog_rejects_unknown_field(self):
        data=catalog(); data["player_records"]=[]
        self.assertTrue(any("unsupported field" in x for x in v35.validate_catalog(data,self.root)))
    def test_asset_rejects_unknown_field(self): self.assertTrue(any("unsupported field" in x for x in v35.validate_catalog(catalog(asset(custom_note="no")),self.root)))
    def test_duplicate_asset_key(self): self.assertTrue(any("Duplicate asset_key" in x for x in v35.validate_catalog(catalog(asset(),asset()),self.root)))
    def test_bad_semver(self): self.assertTrue(any("MAJOR.MINOR.PATCH" in x for x in v35.validate_catalog(catalog(asset(version="v1")),self.root)))
    def test_bad_provenance_ref(self): self.assertTrue(any("opaque ev-" in x for x in v35.validate_catalog(catalog(asset(provenance_ref="https://invalid")),self.root)))
    def test_invalid_target(self): self.assertTrue(any("unsupported profiles" in x for x in v35.validate_catalog(catalog(asset(targets=["phone"])),self.root)))
    def test_bad_rights_enum(self): self.assertTrue(any("rights_status" in x for x in v35.validate_catalog(catalog(asset(rights_status="maybe")),self.root)))
    def test_unhashable_enum_rejected_cleanly(self): self.assertTrue(v35.validate_catalog(catalog(asset(kind=[])),self.root))
    def test_boolean_metric_is_not_integer(self): self.assertTrue(any("positive integer" in x for x in v35.validate_catalog(catalog(asset(measurements={"mesh_triangles":True})),self.root)))
    def test_missing_dependency(self): self.assertTrue(any("missing dependency" in x for x in v35.validate_catalog(catalog(asset(dependencies=["missing-asset"])),self.root)))
    def test_self_dependency(self): self.assertTrue(any("depend on itself" in x for x in v35.validate_catalog(catalog(asset(dependencies=["wooden-crate"])),self.root)))
    def test_dependency_cycle(self):
        a=asset("asset-alpha",dependencies=["asset-bravo"]); b=asset("asset-bravo",dependencies=["asset-alpha"])
        self.assertTrue(any("dependency cycle" in x for x in v35.validate_catalog(catalog(a,b),self.root)))
    def test_duplicate_dependency(self):
        self.assertTrue(any("duplicate asset keys" in x for x in v35.validate_catalog(catalog(asset(dependencies=["asset-other","asset-other"]),asset("asset-other")),self.root)))
    def test_local_source_requires_path(self): self.assertTrue(any("required for local_source" in x for x in v35.validate_catalog(catalog(asset(source_kind="local_source")),self.root)))
    def test_nonlocal_source_rejects_path(self): self.assertTrue(any("only allowed" in x for x in v35.validate_catalog(catalog(asset(source_path="Assets/x.fbx")),self.root)))
    def test_local_file_size_is_verified(self):
        (self.root/"Assets").mkdir(); (self.root/"Assets/model.fbx").write_bytes(b"abc")
        row=asset(source_kind="local_source",source_path="Assets/model.fbx",measurements={"file_size_bytes":5})
        self.assertTrue(any("does not match" in x for x in v35.validate_catalog(catalog(row),self.root)))
    def test_local_path_traversal(self): self.assertTrue(any("invalid" in x for x in v35.validate_catalog(catalog(asset(source_kind="local_source",source_path="../escape.fbx")),self.root)))
    def test_local_absolute_path(self): self.assertTrue(any("invalid" in x for x in v35.validate_catalog(catalog(asset(source_kind="local_source",source_path="C:/private.fbx")),self.root)))
    def test_local_symlink_rejected(self):
        outside=self.root.parent/"v35-external.txt"; outside.write_text("x"); link=self.root/"alias.txt"
        try: link.symlink_to(outside)
        except (OSError,NotImplementedError): self.skipTest("Symlinks unavailable.")
        self.assertTrue(any("symlink" in x for x in v35.validate_catalog(catalog(asset(source_kind="local_source",source_path="alias.txt")),self.root)))
        outside.unlink()

class PolicyAndAuditTests(Fixture):
    def test_valid_policy(self): self.assertEqual(v35.validate_policy(policy()),[])
    def test_unknown_policy_field(self):
        data=policy(); data["track_players"]=True
        self.assertTrue(any("unsupported field" in x for x in v35.validate_policy(data)))
    def test_invalid_budget(self):
        data=policy(); data["profiles"]["mobile"]["max_mesh_triangles"]=0
        self.assertTrue(any("positive integer" in x for x in v35.validate_policy(data)))
    def test_budget_overrun_blocker(self):
        result=v35.catalog_audit(catalog(asset(measurements={"mesh_triangles":90000})),policy(),release_ready=True)
        self.assertTrue(any(x["code"]=="budget_exceeded" and x["severity"]=="blocker" for x in result["issues"]))
    def test_rights_pending_warns_for_draft(self):
        result=v35.catalog_audit(catalog(asset(lifecycle="draft",rights_status="pending")),policy())
        self.assertTrue(any(x["code"]=="rights_not_cleared" and x["severity"]=="warning" for x in result["issues"]))
    def test_rights_pending_blocks_approved(self):
        result=v35.catalog_audit(catalog(asset(rights_status="pending")),policy())
        self.assertTrue(any(x["code"]=="rights_not_cleared" and x["severity"]=="blocker" for x in result["issues"]))
    def test_release_ready_moderation_pending(self):
        result=v35.catalog_audit(catalog(asset(moderation_status="pending")),policy(),release_ready=True)
        self.assertTrue(any(x["code"]=="moderation_pending" for x in result["issues"]))
    def test_rejected_moderation_always_blocks(self):
        result=v35.catalog_audit(catalog(asset(moderation_status="rejected",lifecycle="draft")),policy())
        self.assertTrue(any(x["code"]=="moderation_rejected" for x in result["issues"]))
    def test_unknown_ownership_blocks_release(self):
        result=v35.catalog_audit(catalog(asset(ownership_scope="unknown")),policy(),release_ready=True)
        self.assertTrue(any(x["code"]=="ownership_unknown" for x in result["issues"]))
    def test_missing_measurement_warns(self):
        result=v35.catalog_audit(catalog(asset(kind="texture",measurements={})),policy())
        self.assertTrue(any(x["code"]=="measurement_missing" for x in result["issues"]))
    def test_dependency_not_ready_blocks(self):
        result=v35.catalog_audit(catalog(asset("asset-base",lifecycle="draft"),asset("asset-child",dependencies=["asset-base"],lifecycle="released")),policy(),release_ready=True)
        self.assertTrue(any(x["code"]=="dependency_not_ready" for x in result["issues"]))
    def test_summary_counts(self):
        result=v35.catalog_audit(catalog(asset(rights_status="pending")),policy(),release_ready=True)
        self.assertGreaterEqual(result["blocker_count"],1); self.assertEqual(result["issue_count"],len(result["issues"]))

class CatalogComparisonTests(Fixture):
    def test_added(self): self.assertEqual(v35.compare_catalogs(catalog(),catalog(asset(),asset("asset-new")))["added"],["asset-new"])
    def test_removed(self): self.assertEqual(v35.compare_catalogs(catalog(asset(),asset("asset-old")),catalog(asset()))["removed"],["asset-old"])
    def test_changed_fields(self): self.assertIn("version",v35.compare_catalogs(catalog(asset()),catalog(asset(version="2.0.0")))["changed"][0]["changed_fields"])
    def test_rights_regression(self): self.assertIn("rights_status_regressed",[x["code"] for x in v35.compare_catalogs(catalog(),catalog(asset(rights_status="unknown")))["regressions"]])
    def test_moderation_regression(self): self.assertIn("moderation_status_regressed",[x["code"] for x in v35.compare_catalogs(catalog(),catalog(asset(moderation_status="pending")))["regressions"]])
    def test_removed_dependency_still_referenced(self):
        old=catalog(asset(),asset("asset-old")); new=catalog(asset(dependencies=["asset-old"]))
        self.assertIn("removed_asset_still_referenced",[x["code"] for x in v35.compare_catalogs(old,new)["regressions"]])

class PathAndCommandTests(Fixture):
    def test_load_json_rejects_nan(self):
        (self.root/"bad.json").write_text('{"value": NaN}')
        with self.assertRaises(ValueError): v35.load_json(self.root,"bad.json")
    def test_load_json_rejects_oversize(self):
        (self.root/"big.json").write_bytes(b" "*(v35.MAX_JSON_BYTES+1))
        with self.assertRaises(ValueError): v35.load_json(self.root,"big.json")
    def test_safe_output_rejects_symlink(self):
        target=self.root/"real.txt"; target.write_text("ok"); link=self.root/"alias.txt"
        try: link.symlink_to(target)
        except (OSError,NotImplementedError): self.skipTest("Symlinks unavailable.")
        with self.assertRaises(ValueError): v35.safe_output_path(self.root,"alias.txt")
    def test_atomic_json_output(self):
        target=v35.safe_output_path(self.root,".codex/reports/out.json"); v35.write_json(target,{"ok":True})
        self.assertEqual(json.loads(target.read_text()),{"ok":True})
    def test_cli_validate_catalog(self):
        self.put("catalog.json",catalog())
        self.assertEqual(v35.main_with_args(["validate-catalog","--root",str(self.root),"--catalog","catalog.json"]),0)

class PatcherTests(Fixture):
    def make_sources(self):
        src=self.root/"source"; (src/"tools").mkdir(parents=True); (src/"skills").mkdir()
        (src/"VERSION").write_text("35.0.0"); (src/"tools/v35.py").write_text("# test")
        for i in range(4):
            skill=src/"skills"/f"skill-{i}"/"SKILL.md"; skill.parent.mkdir()
            skill.write_text(f"---\nname: test-skill-{i}\ndescription: test metadata\n---\n# test\n")
        return src
    def make_package(self):
        root=self.root/"package"; (root/".agents/skills").mkdir(parents=True); (root/"AGENTS.md").write_text("# Agents\n")
        for i in range(240):
            file=root/".agents/skills"/f"old-skill-{i}"/"SKILL.md"; file.parent.mkdir(); file.write_text(f"---\nname: old-skill-{i}\ndescription: old\n---\n")
        return root
    def test_patch_and_idempotence(self):
        source,package=self.make_sources(),self.make_package()
        self.assertEqual(patch_cumulative_package.patch(package,source),244)
        self.assertEqual(patch_cumulative_package.patch(package,source),244)
        self.assertTrue((package/"v35/VERSION").is_file())
    def test_wrong_skill_count_rejected(self):
        source,package=self.make_sources(),self.make_package()
        file=package/".agents/skills/old-skill-239/SKILL.md"; file.unlink(); file.parent.rmdir()
        with self.assertRaises(ValueError): patch_cumulative_package.patch(package,source)
    def test_incomplete_source_skills_rejected(self):
        source,package=self.make_sources(),self.make_package(); (source/"skills/skill-3/SKILL.md").unlink()
        with self.assertRaises(ValueError): patch_cumulative_package.patch(package,source)
    def test_name_collision_rejected(self):
        source,package=self.make_sources(),self.make_package()
        target=package/".agents/skills/skill-0"; target.mkdir(); (target/"SKILL.md").write_text("conflict")
        with self.assertRaises(ValueError): patch_cumulative_package.patch(package,source)

class PackageAuditTests(Fixture):
    def test_complete_package_passes(self):
        for relative in audit_cumulative_package.REQUIRED_FILES:
            path=self.root/relative; path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text("35.0.0" if relative=="v35/VERSION" else "placeholder")
        (self.root/"AGENTS.md").write_text("<!-- V35_ASSET_PIPELINE_GOVERNANCE -->")
        (self.root/"README.md").write_text("V35 244 native Codex skills")
        for i in range(244):
            path=self.root/".agents/skills"/f"skill-{i}"/"SKILL.md"; path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(f"---\nname: skill-{i}\ndescription: test\n---\n")
        self.assertEqual(audit_cumulative_package.audit(self.root),[])

if __name__=="__main__": unittest.main()
