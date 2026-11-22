from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("v22_test_module", ROOT / "v22/tools/v22.py")
V22 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V22)


class PricingAuditTests(unittest.TestCase):
    def test_hardcoded_price(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Shop.client.lua").write_text("local priceInRobux = 250\n", encoding="utf-8")
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["hard_coded_price_literals"], 1)
            self.assertEqual(report["summary"]["files_scanned"], 1)

    def test_dynamic_lookup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Shop.lua").write_text(
                "MarketplaceService:GetProductInfoAsync(id)\n"
                "MarketplaceService:GetDeveloperProductsAsync()\n",
                encoding="utf-8",
            )
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["dynamic_price_lookup_sites"], 2)

    def test_legacy_product_info_is_not_counted_as_modern_dynamic_lookup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Shop.lua").write_text(
                "MarketplaceService:GetProductInfo(id, Enum.InfoType.Product)\n",
                encoding="utf-8",
            )
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["dynamic_price_lookup_sites"], 0)
            self.assertEqual(report["summary"]["legacy_product_info_sites"], 1)
            self.assertEqual(report["findings"][0]["code"], "LEGACY_PRODUCT_INFO_API")

    def test_price_level_api(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Gift.server.lua").write_text("GetUsersPriceLevelsAsync({id})\n", encoding="utf-8")
            self.assertEqual(V22.audit_pricing(root)["summary"]["price_level_api_sites"], 1)

    def test_subscription_api(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Sub.server.lua").write_text(
                "GetUserSubscriptionStatusAsync(userId,id)\n", encoding="utf-8"
            )
            self.assertEqual(V22.audit_pricing(root)["summary"]["subscription_api_sites"], 1)

    def test_ignores_markdown_and_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("priceInRobux = 100", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules/x.lua").write_text("priceInRobux = 100", encoding="utf-8")
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["files_considered"], 0)
            self.assertEqual(report["summary"]["files_scanned"], 0)
            self.assertEqual(report["findings"], [])

    def test_line_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Shop.lua").write_text(
                "-- shop\npriceInRobux = 99\nGetProductInfoAsync(id)\n", encoding="utf-8"
            )
            rows = V22.audit_pricing(root)["findings"]
            self.assertEqual([row["line"] for row in rows], [2, 3])

    def test_missing_project_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "does-not-exist"
            with self.assertRaises(ValueError):
                V22.audit_pricing(missing)

    def test_oversized_source_is_reported_as_skipped(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Large.lua").write_bytes(b"a" * (V22.MAX_FILE_BYTES + 1))
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["files_skipped_oversize"], 1)
            self.assertEqual(report["summary"]["files_scanned"], 0)
            self.assertTrue(any("exceeded" in item for item in report["next_steps"]))

    def test_unreadable_source_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "InvalidEncoding.lua").write_bytes(b"\xff\xfe")
            report = V22.audit_pricing(root)
            self.assertEqual(report["summary"]["files_unreadable"], 1)
            self.assertEqual(report["summary"]["files_scanned"], 0)
            self.assertTrue(any("could not be read" in item for item in report["next_steps"]))


class SubscriptionContractTests(unittest.TestCase):
    def test_example_passes(self):
        result = V22.validate_subscription_contract(
            ROOT, Path("v22/examples/subscription-contract.example.json")
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["benefit_count"], 2)

    def test_rejects_duplicate_benefits(self):
        contract = json.loads(
            (ROOT / "v22/examples/subscription-contract.example.json").read_text(encoding="utf-8")
        )
        contract["benefits"].append(contract["benefits"][0])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "v22/schemas").mkdir(parents=True)
            (root / "v22/schemas/subscription-contract.schema.json").write_text(
                (ROOT / "v22/schemas/subscription-contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(ValueError):
                V22.validate_subscription_contract(root, Path("contract.json"))

    def test_rejects_client_authority(self):
        contract = json.loads(
            (ROOT / "v22/examples/subscription-contract.example.json").read_text(encoding="utf-8")
        )
        contract["entitlement_authority"] = "client"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "v22/schemas").mkdir(parents=True)
            (root / "v22/schemas/subscription-contract.schema.json").write_text(
                (ROOT / "v22/schemas/subscription-contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(ValueError):
                V22.validate_subscription_contract(root, Path("contract.json"))

    def test_rejects_grant_key_without_product_and_billing_period(self):
        contract = json.loads(
            (ROOT / "v22/examples/subscription-contract.example.json").read_text(encoding="utf-8")
        )
        contract["period_grant_key"] = "user_id:monthly"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "v22/schemas").mkdir(parents=True)
            (root / "v22/schemas/subscription-contract.schema.json").write_text(
                (ROOT / "v22/schemas/subscription-contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(ValueError):
                V22.validate_subscription_contract(root, Path("contract.json"))


if __name__ == "__main__":
    unittest.main()
