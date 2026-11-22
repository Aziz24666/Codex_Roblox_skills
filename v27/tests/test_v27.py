from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v27  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402


class V27Fixture(unittest.TestCase):
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


class V27InventoryTests(V27Fixture):
    def test_inventory_counts_gradual_type_modes_and_skips_generated_directories(self):
        self.put("src/strict.luau", "--!strict\nlocal value: number = 3\n")
        self.put("src/nonstrict.lua", "--!nonstrict\nlocal value = 3\n")
        self.put("src/nocheck.lua", "--!nocheck\nlocal value = 3\n")
        self.put("src/default.lua", "local value = 3\n")
        self.put(".codex/cache/ignored.luau", "--!strict\n")
        self.put("node_modules/pkg/ignored.lua", "--!strict\n")
        report = v27.build_report(self.root)
        modes = report["inventory"]["type_mode_counts"]
        self.assertEqual(report["inventory"]["luau_files_read"], 4)
        self.assertEqual(modes, {"strict": 1, "nonstrict": 1, "nocheck": 1, "default": 1})
        self.assertEqual(report["inventory"]["strict_mode_percent"], 25.0)

    def test_source_scanner_skips_symlinks(self):
        target = self.put("src/real.luau", "return true\n")
        link = self.root / "src" / "linked.luau"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable in this environment.")
        warnings: list[str] = []
        files = v27.iter_luau_files(self.root, 100, warnings)
        self.assertEqual([item.name for item in files], ["real.luau"])
        self.assertTrue(any("symlink" in item for item in warnings))

    def test_file_limit_is_bounded(self):
        for index in range(5):
            self.put(f"src/Module{index}.luau", "return true\n")
        warnings: list[str] = []
        files = v27.iter_luau_files(self.root, 3, warnings)
        self.assertEqual(len(files), 3)
        self.assertTrue(any("3-file limit" in item for item in warnings))


class V27DependencyTests(V27Fixture):
    def test_static_require_graph_resolves_edges_and_reports_cycles_and_missing_refs(self):
        self.put("src/Modules/A.lua", 'local B = require(script.Parent.B)\nreturn B\n')
        self.put("src/Modules/B.lua", 'local A = require(script.Parent.A)\nreturn A\n')
        self.put("src/Server/Main.server.lua", 'local A = require(script.Parent.Parent.Modules.A)\nlocal Missing = require(script.Parent.Parent.Modules.DoesNotExist)\n')
        report = v27.build_report(self.root)
        graph = report["dependencies"]
        self.assertEqual(len(graph["resolved_edges"]), 3)
        self.assertEqual(len(graph["cycles"]), 1)
        self.assertEqual(set(graph["cycles"][0]), {"src/Modules/A.lua", "src/Modules/B.lua"})
        self.assertEqual(len(graph["unresolved_static_requires"]), 1)
        self.assertEqual(graph["unresolved_static_requires"][0]["status"], "missing")

    def test_dynamic_requires_are_counted_not_guessed(self):
        self.put("src/Loader.server.lua", 'local module = require(getModuleName())\nlocal asset = require(123456)\n')
        report = v27.build_report(self.root)
        self.assertEqual(report["dependencies"]["dynamic_or_non_script_requires"], 2)
        self.assertEqual(report["dependencies"]["resolved_edges"], [])

    def test_possible_unreferenced_modules_are_explicitly_heuristic(self):
        self.put("src/Modules/Used.lua", "return {}\n")
        self.put("src/Modules/Unused.module.lua", "return {}\n")
        self.put("src/Main.server.lua", "local Used = require(script.Parent.Modules.Used)\n")
        report = v27.build_report(self.root)
        self.assertIn("src/Modules/Unused.module.lua", report["dependencies"]["possible_unreferenced_modules"])
        self.assertNotIn("src/Modules/Used.lua", report["dependencies"]["possible_unreferenced_modules"])
        self.assertIn("review candidates only", report["dependencies"]["note"])


class V27RemoteTests(V27Fixture):
    def test_remote_contracts_compare_constant_client_references_to_server_handlers(self):
        self.put(
            "src/Client.client.lua",
            'local Attack = ReplicatedStorage.Remotes:WaitForChild("AttackRequest")\n'
            'local Mystery = ReplicatedStorage.Remotes:WaitForChild("MysteryRequest")\n'
            'Attack:FireServer("swing")\nMystery:InvokeServer()\n',
        )
        self.put(
            "src/Server.server.lua",
            'local Attack = ReplicatedStorage.Remotes:WaitForChild("AttackRequest")\n'
            'Attack.OnServerEvent:Connect(function(player, action) end)\n',
        )
        report = v27.build_report(self.root)["remote_contracts"]
        self.assertEqual(report["client_to_server_calls"], {"AttackRequest": 1, "MysteryRequest": 1})
        self.assertEqual(report["server_handlers"], {"AttackRequest": 1})
        self.assertEqual(
            [item["remote_reference"] for item in report["potentially_unpaired_client_calls"]],
            ["MysteryRequest"],
        )
        self.assertGreaterEqual(report["static_name_bindings"], 3)

    def test_remote_instance_inventory_does_not_infer_remote_names(self):
        self.put("src/Network.server.lua", 'local remote = Instance.new("RemoteEvent")\n')
        report = v27.build_report(self.root)["remote_contracts"]
        self.assertEqual(report["Instance_new_counts"], {"RemoteEvent": 1})
        self.assertEqual(report["client_to_server_calls"], {})


class V27RojoTests(V27Fixture):
    def test_valid_rojo_project_and_relative_paths(self):
        self.put("src/server/Main.server.lua", "print('ok')\n")
        project = self.put(
            "default.project.json",
            json.dumps({
                "name": "Example",
                "tree": {
                    "$className": "DataModel",
                    "ServerScriptService": {
                        "$className": "ServerScriptService",
                        "$path": "src/server",
                    },
                },
            }),
        )
        result = v27.validate_rojo_project(project, self.root)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["mapped_paths"], ["src/server"])

    def test_rojo_project_rejects_missing_paths_and_escaping_paths(self):
        project = self.put(
            "default.project.json",
            json.dumps({
                "name": "Example",
                "tree": {
                    "$className": "DataModel",
                    "ServerScriptService": {"$path": "missing-folder"},
                    "ReplicatedStorage": {"$path": "../outside"},
                },
            }),
        )
        result = v27.validate_rojo_project(project, self.root)
        self.assertFalse(result["valid"])
        self.assertTrue(any("Missing" in error for error in result["errors"]))
        self.assertTrue(any("escapes project root" in error for error in result["errors"]))

    def test_rojo_project_rejects_symlink_path(self):
        with tempfile.TemporaryDirectory() as outside_temp:
            outside = Path(outside_temp)
            self.put("src/inside.luau", "return true\n")
            link = self.root / "linked"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are unavailable in this environment.")
            project = self.put(
                "default.project.json",
                json.dumps({"name": "Example", "tree": {"ReplicatedStorage": {"$path": "linked"}}}),
            )
            result = v27.validate_rojo_project(project, self.root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("symlink" in error for error in result["errors"]))

    def test_multiple_project_files_require_explicit_selection(self):
        self.put("one.project.json", json.dumps({"name": "One", "tree": {}}))
        self.put("two.project.json", json.dumps({"name": "Two", "tree": {}}))
        with self.assertRaisesRegex(ValueError, "found 2"):
            v27.find_rojo_project(self.root, None)


class V27ToolExecutionTests(V27Fixture):
    @patch("v27.shutil.which", return_value="/tools/luau-analyze")
    @patch("v27.subprocess.run")
    def test_typecheck_invokes_analyzer_without_a_shell_and_respects_project_mode(self, run, which):
        self.put("src/Main.luau", "return true\n")
        files = v27.iter_luau_files(self.root, 100, [])
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        self.assertEqual(v27.run_luau_analyzer(self.root, files, "project"), 0)
        command = run.call_args.args[0]
        self.assertIn("--formatter=plain", command)
        self.assertFalse(any(item.startswith("--mode=") for item in command))
        self.assertNotIn("shell", run.call_args.kwargs)

    @patch("v27.shutil.which", return_value="/tools/luau-analyze")
    @patch("v27.subprocess.run")
    def test_typecheck_can_explicitly_select_strict_mode(self, run, which):
        self.put("src/Main.luau", "--!nonstrict\nreturn true\n")
        files = v27.iter_luau_files(self.root, 100, [])
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        self.assertEqual(v27.run_luau_analyzer(self.root, files, "strict"), 0)
        self.assertIn("--mode=strict", run.call_args.args[0])

    @patch("v27.shutil.which", return_value=None)
    def test_typecheck_fails_clearly_when_analyzer_is_missing(self, which):
        with self.assertRaisesRegex(RuntimeError, "not found on PATH"):
            v27.run_luau_analyzer(self.root, [], "project")


class V27PackageTests(unittest.TestCase):
    def test_patch_is_idempotent_and_cumulative_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills_root = package / ".agents" / "skills"
            for index in range(210):
                skill = skills_root / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(
                    f"---\nname: legacy-{index:03}\ndescription: Existing cumulative skill {index}.\n---\n",
                    encoding="utf-8",
                )
            (package / "AGENTS.md").write_text(
                "# Agent rules\n\nInherited no-gambling requirements remain active.\n",
                encoding="utf-8",
            )
            stubs = (
                "v23/tools/v23.py", "v23/tests/test_v23.py",
                "v23/schemas/opportunity-discovery-report.schema.json", "v23/data/opportunity-catalog.json",
                "v25/VERSION", "v25/tools/v25.py", "v25/tests/test_v25.py",
                "v26/VERSION", "v26/tools/v26.py", "v26/tests/test_v26.py",
                "v26/tools/patch_cumulative_package.py", "v26/tools/audit_cumulative_package.py",
                "v26/docs/STUDIO_MCP_WORKFLOW.md", "v26/docs/MULTIPLAYER_DEVICE_TESTING.md",
                "v26/docs/SAFE_AUTOMATION_BOUNDARIES.md", "v26/schemas/studio-test-plan.schema.json",
                ".agents/skills/roblox-studio-mcp-workflow/SKILL.md",
                ".agents/skills/roblox-studio-multiplayer-device-testing/SKILL.md",
                ".agents/skills/roblox-studio-safe-edit-review/SKILL.md",
            )
            for relative in stubs:
                stub = package / relative
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.write_text("stub\n", encoding="utf-8")
            for filename in ("README.md", "LICENSE", "INDEX.md", "INDEX_V25.md", "INDEX_V26.md"):
                (package / filename).write_text("# V27 — 213 native Codex skills\n", encoding="utf-8")
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertIn("Inherited no-gambling requirements remain active.", agents)
            self.assertEqual(audit_cumulative_package.audit(package), [])


if __name__ == "__main__":
    unittest.main()
