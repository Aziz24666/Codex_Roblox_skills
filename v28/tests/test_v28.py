from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v28  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def put(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class RemoteReviewTests(Fixture):
    def test_remote_handler_signals_and_static_client_pairing(self):
        self.put(
            "src/Client.client.lua",
            'local PurchaseRequest = ReplicatedStorage.Remotes:WaitForChild("PurchaseRequest")\n'
            'PurchaseRequest:FireServer("skin")\n',
        )
        self.put(
            "src/Server.server.lua",
            'local PurchaseRequest = ReplicatedStorage.Remotes:WaitForChild("PurchaseRequest")\n'
            'PurchaseRequest.OnServerEvent:Connect(function(player, itemId)\n'
            '    if typeof(itemId) ~= "string" then return end\n'
            '    if not table.find(allowedItems, itemId) then return end\n'
            '    if os.clock() < nextAllowed then return end\n'
            '    if processedRequests[itemId] then return end\n'
            '    grantItem(player, itemId)\n'
            'end)\n',
        )
        report = v28.build_report(self.root)
        remote = report["remote_security"]
        self.assertEqual(remote["client_to_server_calls"], {"PurchaseRequest": 1})
        self.assertEqual(remote["server_handlers"], {"PurchaseRequest": 1})
        self.assertEqual(len(remote["unpaired_client_calls"]), 0)
        handler = remote["handlers"][0]
        self.assertTrue(handler["nearby_signals"]["type_or_range_validation"])
        self.assertTrue(handler["nearby_signals"]["rate_limit_or_cooldown"])
        self.assertTrue(handler["nearby_signals"]["duplicate_or_idempotency_signal"])

    def test_critical_handler_without_nearby_signals_gets_review_flags(self):
        self.put(
            "src/Server.server.lua",
            'local Reward = ReplicatedStorage.Remotes:WaitForChild("RewardRequest")\n'
            'Reward.OnServerEvent:Connect(function(player, amount)\n'
            '    leaderstats.Coins.Value += amount\n'
            'end)\n',
        )
        handlers = v28.build_report(self.root)["remote_security"]["handlers"]
        self.assertEqual(len(handlers), 1)
        self.assertGreaterEqual(len(handlers[0]["review_flags"]), 2)

    def test_unpaired_static_client_call_is_reported(self):
        self.put("src/Client.client.lua", 'local Unknown = folder:WaitForChild("Unknown")\nUnknown:InvokeServer()\n')
        report = v28.build_report(self.root)["remote_security"]
        self.assertEqual(report["unpaired_client_calls"][0]["remote_reference"], "Unknown")


class DataStoreReviewTests(Fixture):
    def test_datastore_calls_and_safety_signals_are_inventoried(self):
        self.put(
            "src/Profile.server.lua",
            'local Store = DataStoreService:GetDataStore("Profiles")\n'
            'local schemaVersion = 2 -- current profile schema version\n'
            'local ok, result = pcall(function()\n'
            '  return Store:UpdateAsync(key, transform)\n'
            'end)\n'
            'local backup = snapshotProfile(result)\n'
            'local function migrateProfile(data) -- migration\n'
            '  return data\n'
            'end\n'
            'local attempts = 3 -- retry with backoff\n'
            'local budget = DataStoreService:GetRequestBudgetForRequestType(Enum.DataStoreRequestType.UpdateAsync)\n',
        )
        report = v28.build_report(self.root)["datastore"]
        self.assertEqual(report["datastore_factory_calls"], 1)
        self.assertEqual(report["api_call_counts"], {"UpdateAsync": 1})
        self.assertGreater(report["signals"]["schema_version_markers"], 0)
        self.assertGreater(report["signals"]["migration_markers"], 0)
        self.assertGreater(report["signals"]["backup_or_rollback_markers"], 0)
        self.assertGreater(report["signals"]["protected_call_markers"], 0)
        self.assertGreater(report["signals"]["request_budget_markers"], 0)

    def test_destructive_and_overwrite_api_calls_are_flagged(self):
        self.put("src/Profile.lua", 'Store:SetAsync(key, profile)\nStore:RemoveAsync(key)\n')
        operations = v28.build_report(self.root)["datastore"]["operations"]
        self.assertEqual([item["review_class"] for item in operations], [
            "overwrite-concurrency-review", "destructive-write-review",
        ])

    def test_report_contains_bounded_inventory_and_limitations(self):
        self.put("src/Main.luau", "return true\n")
        report = v28.build_report(self.root)
        self.assertEqual(report["inventory"]["luau_files_read"], 1)
        self.assertTrue(any("not a Luau parser" in item for item in report["limitations"]))


class MigrationManifestTests(Fixture):
    def valid_manifest(self):
        return {
            "schema_version": 1,
            "environment": "synthetic",
            "dry_run": True,
            "production_writes": False,
            "current_schema_version": 1,
            "target_schema_version": 2,
            "preserve_unknown_fields": True,
            "backup": {
                "required": True,
                "verified_in_staging": True,
                "strategy": "Verified isolated fixture snapshot and restore rehearsal",
            },
            "rollback_plan": "Stop the rollout, restore the verified snapshot, and verify records with fixture checks.",
            "migrations": [{
                "from": 1,
                "to": 2,
                "idempotent": True,
                "description": "Normalize the legacy inventory schema and add defaults.",
                "tests": [
                    {"name": "valid profile", "kind": "valid"},
                    {"name": "malformed profile", "kind": "invalid"},
                    {"name": "legacy profile", "kind": "legacy"},
                    {"name": "repeat migration", "kind": "repeat"},
                ],
            }],
        }

    def test_valid_synthetic_manifest_passes(self):
        self.assertEqual(v28.validate_manifest_data(self.valid_manifest()), [])

    def test_production_environment_or_write_is_rejected(self):
        data = self.valid_manifest()
        data["environment"] = "production"
        data["production_writes"] = True
        errors = v28.validate_manifest_data(data)
        self.assertTrue(any("production is not permitted" in item for item in errors))
        self.assertTrue(any("production_writes must be false" in item for item in errors))

    def test_non_idempotent_or_noncontiguous_migration_is_rejected(self):
        data = self.valid_manifest()
        data["migrations"][0]["idempotent"] = False
        data["migrations"][0]["to"] = 3
        errors = v28.validate_manifest_data(data)
        self.assertTrue(any("idempotent must be true" in item for item in errors))
        self.assertTrue(any("advance exactly one" in item for item in errors))

    def test_missing_repeat_or_legacy_case_is_rejected(self):
        data = self.valid_manifest()
        data["migrations"][0]["tests"] = [{"name": "only valid", "kind": "valid"}]
        errors = v28.validate_manifest_data(data)
        self.assertTrue(any("missing named coverage" in item for item in errors))

    def test_manifest_file_must_stay_inside_project_root(self):
        outside = Path(tempfile.mkdtemp())
        try:
            external = outside / "manifest.json"
            external.write_text(json.dumps(self.valid_manifest()), encoding="utf-8")
            errors, _ = v28.validate_manifest(self.root, str(external))
            self.assertTrue(errors)
            self.assertIn("inside the selected project root", errors[0])
        finally:
            for child in outside.iterdir():
                child.unlink()
            outside.rmdir()

    def test_valid_manifest_file_is_read_without_execution(self):
        manifest = self.put("plan.json", json.dumps(self.valid_manifest()))
        errors, path = v28.validate_manifest(self.root, "plan.json")
        self.assertEqual(errors, [])
        self.assertEqual(path, manifest)


class PathSafetyTests(Fixture):
    def test_report_output_rejects_parent_traversal_and_absolute_outside(self):
        with self.assertRaisesRegex(ValueError, "inside the selected project root"):
            v28.safe_output_path(self.root, "../outside.json")
        with self.assertRaisesRegex(ValueError, "inside the selected project root"):
            v28.safe_output_path(self.root, str(self.root.parent / "outside.json"))

    def test_symlinked_sources_are_skipped(self):
        real = self.put("src/real.lua", "return true\n")
        link = self.root / "src" / "linked.lua"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable.")
        warnings = []
        found = v28.iter_luau_files(self.root, warnings)
        self.assertEqual([p.name for p in found], ["real.lua"])
        self.assertTrue(any("symlink" in warning for warning in warnings))


class PackageTests(unittest.TestCase):
    def test_patch_is_idempotent_and_package_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills_root = package / ".agents" / "skills"
            for index in range(213):
                skill = skills_root / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(
                    f"---\nname: legacy-{index:03}\ndescription: Existing skill {index}.\n---\n",
                    encoding="utf-8",
                )
            (package / "AGENTS.md").write_text("# Agent rules\n\nNo gambling.\n", encoding="utf-8")
            stubs = (
                "v23/tools/v23.py", "v23/tests/test_v23.py",
                "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
                "v25/VERSION", "v25/tools/v25.py", "v25/tests/test_v25.py",
                "v26/VERSION", "v26/tools/v26.py", "v26/tests/test_v26.py",
                "v27/VERSION", "v27/tools/v27.py", "v27/tests/test_v27.py",
                "v27/docs/LUAU_STATIC_ANALYSIS.md", "v27/docs/DEPENDENCY_AND_REMOTE_CONTRACTS.md",
                "v27/docs/ROJO_PROJECT_VALIDATION.md", "v27/docs/STRICT_TYPING_MIGRATION.md",
                ".agents/skills/roblox-luau-static-analysis-v27/SKILL.md",
                ".agents/skills/roblox-luau-architecture-and-dependency-governance-v27/SKILL.md",
                ".agents/skills/roblox-remote-contract-and-rojo-validation-v27/SKILL.md",
            )
            for relative in stubs:
                stub = package / relative
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.write_text("stub\n", encoding="utf-8")
            for filename in ("README.md", "LICENSE", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md", "INDEX_V27.md"):
                (package / filename).write_text(
                    "# V28 cumulative toolkit with 216 native Codex skills\nV27 and V26 are included.\n",
                    encoding="utf-8",
                )
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertIn("No gambling.", agents)
            self.assertEqual(audit_cumulative_package.audit(package), [])


if __name__ == "__main__":
    unittest.main()
