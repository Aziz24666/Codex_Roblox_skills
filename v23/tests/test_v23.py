from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("v23_test_module",ROOT/"tools/v23.py")
V23=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V23)

class OpportunityDiscoveryTests(unittest.TestCase):
    def test_catalogue_has_40_plus_unique_deterministic_options(self):
        catalog=V23.load_catalog()
        self.assertGreaterEqual(len(catalog),40)
        self.assertEqual(len({x["id"] for x in catalog}),len(catalog))
        self.assertTrue(all(x["deterministic"] is True for x in catalog))
    def test_character_customization_matches_cosmetics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"Character.client.lua").write_text("local avatarSkin='Explorer'\nlocal outfit='Default'\nlocal emote='Wave'\n",encoding="utf-8")
            report=V23.discover_opportunities(root); by_id={x["id"]:x for x in report["opportunities"]}
            for key in ("character-skins","outfit-bundles","emote-packs"): self.assertNotEqual(by_id[key]["status"],"not_detected")
            self.assertTrue(by_id["character-skins"]["evidence"])
    def test_full_catalogue_is_returned_even_without_matches(self):
        with tempfile.TemporaryDirectory() as temporary:
            report=V23.discover_opportunities(Path(temporary))
            self.assertEqual(report["summary"]["catalogue_options"],len(V23.load_catalog()))
            self.assertGreater(report["summary"]["not_detected"],0)
            self.assertGreater(report["summary"]["platform_review"],0)
    def test_paid_random_outcome_is_blocker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"Shop.server.lua").write_text("MarketplaceService:PromptProductPurchase(player, lootBoxProductId) -- random outcome\n",encoding="utf-8")
            report=V23.discover_opportunities(root)
            self.assertTrue(any(x["code"]=="PAID_RANDOM_OUTCOME" and x["severity"]=="blocker" for x in report["risk_findings"]))
    def test_pressure_copy_needs_purchase_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"Shop.client.lua").write_text("local message = 'Last chance - buy now, purchase'\n",encoding="utf-8")
            report=V23.discover_opportunities(root)
            self.assertTrue(any(x["code"]=="PRESSURE_COPY_OR_TIMER" for x in report["risk_findings"]))
    def test_paid_access_and_private_server_collision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"design.md").write_text("private server support and closed beta paid access for this experience\n",encoding="utf-8")
            report=V23.discover_opportunities(root)
            self.assertTrue(any(x["code"]=="ACCESS_MODEL_COLLISION" for x in report["risk_findings"]))
    def test_scan_limit_reports_truncation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for index in range(3): (root/f"File{index}.lua").write_text("print('game')\n",encoding="utf-8")
            report=V23.discover_opportunities(root,max_files=2)
            self.assertTrue(report["summary"]["scan_truncated"])
            self.assertEqual(report["summary"]["files_considered"],2)
    def test_oversized_file_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); (root/"Large.lua").write_bytes(b"x"*(V23.MAX_FILE_BYTES+1))
            self.assertEqual(V23.discover_opportunities(root)["summary"]["files_skipped_oversize"],1)
    def test_missing_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError): V23.discover_opportunities(Path(temporary)/"missing")
    def test_report_matches_schema(self):
        import jsonschema
        with tempfile.TemporaryDirectory() as temporary: report=V23.discover_opportunities(Path(temporary))
        schema=json.loads((ROOT/"schemas/opportunity-discovery-report.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(report)

if __name__=="__main__": unittest.main()
