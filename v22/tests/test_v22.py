from __future__ import annotations
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("v22_test_module",ROOT/"v22/tools/v22.py")
V22=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V22)
class PricingAuditTests(unittest.TestCase):
    def test_hardcoded_price(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"Shop.client.lua").write_text("local priceInRobux = 250\n")
            self.assertEqual(V22.audit_pricing(root)["summary"]["hard_coded_price_literals"],1)
    def test_dynamic_lookup(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"Shop.lua").write_text("MarketplaceService:GetProductInfoAsync(id)\n")
            self.assertEqual(V22.audit_pricing(root)["summary"]["dynamic_price_lookup_sites"],1)
    def test_price_level_api(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"Gift.server.lua").write_text("GetUsersPriceLevelsAsync({id})\n")
            self.assertEqual(V22.audit_pricing(root)["summary"]["price_level_api_sites"],1)
    def test_subscription_api(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"Sub.server.lua").write_text("GetUserSubscriptionStatusAsync(userId,id)\n")
            self.assertEqual(V22.audit_pricing(root)["summary"]["subscription_api_sites"],1)
    def test_ignores_markdown_and_dependencies(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"README.md").write_text("priceInRobux = 100")
            (root/"node_modules").mkdir(); (root/"node_modules/x.lua").write_text("priceInRobux = 100")
            self.assertEqual(V22.audit_pricing(root)["summary"]["files_scanned"],0)
    def test_line_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"Shop.lua").write_text("-- shop\npriceInRobux = 99\nGetProductInfoAsync(id)\n")
            rows=V22.audit_pricing(root)["findings"]; self.assertEqual([x["line"] for x in rows],[2,3])
class SubscriptionContractTests(unittest.TestCase):
    def test_example_passes(self):
        result=V22.validate_subscription_contract(ROOT,Path("v22/examples/subscription-contract.example.json"))
        self.assertEqual(result["status"],"PASS"); self.assertEqual(result["benefit_count"],2)
    def test_rejects_duplicate_benefits(self):
        contract=json.loads((ROOT/"v22/examples/subscription-contract.example.json").read_text()); contract["benefits"].append(contract["benefits"][0])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"v22/schemas").mkdir(parents=True)
            (root/"v22/schemas/subscription-contract.schema.json").write_text((ROOT/"v22/schemas/subscription-contract.schema.json").read_text())
            (root/"contract.json").write_text(json.dumps(contract))
            with self.assertRaises(ValueError): V22.validate_subscription_contract(root,Path("contract.json"))
    def test_rejects_client_authority(self):
        contract=json.loads((ROOT/"v22/examples/subscription-contract.example.json").read_text()); contract["entitlement_authority"]="client"
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"v22/schemas").mkdir(parents=True)
            (root/"v22/schemas/subscription-contract.schema.json").write_text((ROOT/"v22/schemas/subscription-contract.schema.json").read_text())
            (root/"contract.json").write_text(json.dumps(contract))
            with self.assertRaises(ValueError): V22.validate_subscription_contract(root,Path("contract.json"))
if __name__=="__main__": unittest.main()
