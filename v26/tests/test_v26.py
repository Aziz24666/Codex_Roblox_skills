from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v26  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402


class V26DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = self.root / "mcp.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = v26.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_doctor_without_config_does_not_claim_connection(self):
        code, out, err = self.run_cli("doctor", "--root", str(self.root), "--format", "json")
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["mcp_config"]["state"], "not_checked")
        self.assertTrue(any("does not prove" in warning for warning in report["warnings"]))

    def test_doctor_accepts_documented_windows_configuration_without_execution(self):
        self.config.write_text(json.dumps({
            "mcpServers": {
                "Roblox_Studio": {
                    "command": "cmd.exe",
                    "args": ["/c", "%LOCALAPPDATA%\\Roblox\\mcp.bat"],
                }
            }
        }), encoding="utf-8")
        code, out, err = self.run_cli("doctor", "--root", str(self.root), "--config", str(self.config), "--format", "json")
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["mcp_config"]["state"], "pass")
        self.assertEqual(report["mcp_config"]["command_kind"], "official_windows_example")

    def test_doctor_accepts_studio_mcp_binary(self):
        self.config.write_text(json.dumps({
            "mcpServers": {"Roblox_Studio": {"command": "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"}}
        }), encoding="utf-8")
        self.assertEqual(v26.inspect_mcp_config(self.config)["state"], "pass")

    def test_doctor_rejects_invalid_json_without_echoing_secrets(self):
        secret = "fake-test-secret-DO-NOT-PRINT"
        self.config.write_text('{"broken": "' + secret, encoding="utf-8")
        code, out, err = self.run_cli("doctor", "--root", str(self.root), "--config", str(self.config))
        self.assertEqual(code, 1)
        self.assertNotIn(secret, out + err)
        self.assertIn("not readable UTF-8 JSON", err)

    def test_doctor_rejects_missing_server_entry(self):
        self.config.write_text('{"mcpServers": {"other": {"command": "safe"}}}', encoding="utf-8")
        self.assertEqual(v26.inspect_mcp_config(self.config)["state"], "fail")

    def test_custom_command_is_review_not_automatically_executed_or_trusted(self):
        self.config.write_text(json.dumps({
            "mcpServers": {"Roblox_Studio": {"command": "custom-launcher", "args": ["private-value"]}}
        }), encoding="utf-8")
        report = v26.inspect_mcp_config(self.config)
        self.assertEqual(report["state"], "review")
        self.assertNotIn("private-value", json.dumps(report))


class V26PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = v26.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_plan_generates_and_verifies_safe_matrix(self):
        code, out, err = self.run_cli("plan", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        plan_path = self.root / v26.DEFAULT_PLAN
        self.assertTrue(plan_path.is_file())
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["execution_mode"], "manual_review_only")
        self.assertIn(8, next(stage for stage in plan["stages"] if stage["id"] == "multiplayer")["client_counts"])
        code, out, err = self.run_cli("verify-plan", "--path", str(plan_path))
        self.assertEqual(code, 0, err)
        self.assertIn("PASS:", out)

    def test_plan_refuses_overwrite_without_force(self):
        path = self.root / "plan.json"
        v26.write_plan(self.root, "plan.json")
        with self.assertRaises(FileExistsError):
            v26.write_plan(self.root, "plan.json")
        v26.write_plan(self.root, "plan.json", force=True)
        self.assertTrue(path.is_file())

    def test_plan_rejects_path_traversal_and_symlinked_parent(self):
        with self.assertRaises(ValueError):
            v26.plan_output_path(self.root, "../escape.json")
        outside = Path(self.temp.name).parent / (Path(self.temp.name).name + "-outside")
        outside.mkdir(exist_ok=True)
        link = self.root / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are not supported in this environment.")
        with self.assertRaises(ValueError):
            v26.plan_output_path(self.root, "linked/escape.json")

    def test_verify_plan_rejects_removed_approval_or_unsafe_mutation(self):
        plan = v26.build_test_plan(self.root)
        plan["requires_human_approval_before"].remove("publishing")
        plan["production_data_access"] = True
        errors = v26.verify_plan_document(plan)
        self.assertTrue(any("approval" in error for error in errors))
        self.assertTrue(any("production data" in error for error in errors))

    def test_verify_plan_rejects_client_count_above_documented_ceiling(self):
        plan = v26.build_test_plan(self.root)
        plan["stages"][3]["client_counts"] = [2, 9]
        self.assertTrue(any("1-8" in error for error in v26.verify_plan_document(plan)))


class V26PackageTests(unittest.TestCase):
    def test_patch_is_idempotent_and_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills_root = package / ".agents" / "skills"
            for index in range(207):
                skill = skills_root / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(
                    f"---\nname: legacy-{index:03}\ndescription: Existing cumulative skill {index}.\n---\n",
                    encoding="utf-8",
                )
            (package / "AGENTS.md").write_text(
                "# Agent rules\n\nInherited V18 no-gambling and fair-monetization rules remain active.\n",
                encoding="utf-8",
            )
            required_stubs = (
                "v23/tools/v23.py", "v23/tests/test_v23.py",
                "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
                "v25/VERSION", "v25/tools/v25.py", "v25/tests/test_v25.py",
            )
            for relative in required_stubs:
                stub = package / relative
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.write_text("25.0.1\n", encoding="utf-8")
            (package / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (package / "INDEX.md").write_text("# Index\n", encoding="utf-8")
            (package / "INDEX_V25.md").write_text("# V25\n", encoding="utf-8")
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertIn("Inherited V18 no-gambling and fair-monetization rules remain active.", agents)
            self.assertEqual(audit_cumulative_package.audit(package), [])


if __name__ == "__main__":
    unittest.main()
