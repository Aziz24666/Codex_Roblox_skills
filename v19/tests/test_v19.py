import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V19_ROOT = REPO / "v19"
SPEC = importlib.util.spec_from_file_location("v19_cli_tests", V19_ROOT / "tools" / "v19.py")
V19 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V19)
PATCH_SPEC = importlib.util.spec_from_file_location(
    "v19_patcher_tests", V19_ROOT / "tools" / "patch_cumulative_package.py"
)
PATCHER = importlib.util.module_from_spec(PATCH_SPEC)
PATCH_SPEC.loader.exec_module(PATCHER)


def fixture_root(temp):
    root = Path(temp)
    (root / "v18/tools").mkdir(parents=True)
    (root / "v18/workflow").mkdir(parents=True)
    (root / "v19/workflow").mkdir(parents=True)
    (root / "v19/evals").mkdir(parents=True)
    (root / "v19/schemas").mkdir(parents=True)
    shutil.copy2(REPO / "v18/tools/v18.py", root / "v18/tools/v18.py")
    shutil.copy2(REPO / "v18/workflow/skill-routing.json", root / "v18/workflow/skill-routing.json")
    shutil.copy2(V19_ROOT / "workflow/routing-additions.json", root / "v19/workflow/routing-additions.json")
    shutil.copy2(V19_ROOT / "evals/routing-cases.json", root / "v19/evals/routing-cases.json")
    for schema in (V19_ROOT / "schemas").glob("*.schema.json"):
        shutil.copy2(schema, root / "v19/schemas" / schema.name)
    (root / ".agents/skills").mkdir(parents=True)
    route = json.loads((root / "v18/workflow/skill-routing.json").read_text(encoding="utf-8"))
    skill_names = {name for domain in route["domains"].values() for name in domain["skills"]}
    additions = json.loads((root / "v19/workflow/routing-additions.json").read_text(encoding="utf-8"))
    skill_names |= {name for domain in additions["additions"].values() for name in domain["skills"]}
    skill_names.update({
        "roblox-end-to-end-development-orchestrator",
        "roblox-task-intake-and-requirements",
        "roblox-impact-aware-skill-routing",
        "roblox-evidence-first-completion",
        "roblox-game-builder",
        "roblox-cross-system-contract-governance",
        "roblox-dependency-aware-workstream-planning",
        "roblox-risk-and-approval-gating",
    })
    for name in skill_names:
        (root / ".agents/skills" / name).mkdir(parents=True)
        (root / ".agents/skills" / name / "SKILL.md").write_text("fixture\n", encoding="utf-8")
    PATCHER.merge_routing(root)
    return root


class V19Tests(unittest.TestCase):
    def test_routing_benchmark_covers_all_regression_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            report = V19.evaluate_routing(root, max_specialists=20)
            self.assertEqual(report["status"], "PASS", json.dumps(report["cases"], indent=2))
            self.assertEqual(report["summary"]["failed_cases"], 0)

    def test_plan_selects_security_and_multiplayer_for_remote_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            plan = V19.build_test_plan(
                root,
                "Review multiplayer RemoteEvent server validation and ownership security",
                ["src/Server/RemoteHandler.luau"],
            )
            ids = {check["check_id"] for check in plan["checks"]}
            self.assertIn("luau-static-analysis", ids)
            self.assertIn("server-boundary-security", ids)
            self.assertIn("multi-client-studio", ids)
            self.assertTrue(all(check["status"] == "NOT_RUN" for check in plan["checks"]))
            self.assertIn("does not execute", plan["execution_note"])

    def test_plan_rejects_paths_that_escape_project_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            with self.assertRaises(ValueError):
                V19.build_test_plan(root, "Change a module", ["../outside.luau"])

    def test_evidence_pass_requires_existing_nonempty_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            artifact = root / "artifacts/test.log"
            artifact.parent.mkdir()
            artifact.write_text("test suite passed\n", encoding="utf-8")
            record = {
                "schema_version": 1,
                "work_item_id": "sample-test",
                "build_identity": "commit-abc123",
                "checks": [{
                    "check_id": "unit-suite",
                    "category": "unit",
                    "status": "PASS",
                    "environment": "CI runner",
                    "tool_version": "Python 3.13",
                    "command": "python -m unittest",
                    "expected": "All tests pass",
                    "actual": "12 tests passed",
                    "evidence_paths": ["artifacts/test.log"],
                    "limitations": [],
                    "scenario": "unit regression suite"
                }]
            }
            path = root / "evidence.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            result = V19.validate_evidence(root, path)
            self.assertEqual(result["status"], "PASS")
            record["checks"][0]["evidence_paths"] = []
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(ValueError):
                V19.validate_evidence(root, path)

    def test_evidence_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            record = {
                "schema_version": 1,
                "work_item_id": "sample-test",
                "build_identity": "commit-abc123",
                "checks": [{
                    "check_id": "unit-suite",
                    "category": "unit",
                    "status": "PASS",
                    "environment": "CI runner",
                    "tool_version": "Python 3.13",
                    "command": "python -m unittest",
                    "expected": "All tests pass",
                    "actual": "Passed",
                    "evidence_paths": ["../secret.txt"],
                    "limitations": []
                }]
            }
            path = root / "evidence.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(ValueError):
                V19.validate_evidence(root, path)

    def test_not_run_requires_an_explanation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(temp)
            record = {
                "schema_version": 1,
                "work_item_id": "sample-test",
                "checks": [{
                    "check_id": "studio-test",
                    "category": "studio",
                    "status": "NOT_RUN",
                    "environment": "Roblox Studio",
                    "tool_version": "Not recorded",
                    "command": "Run test scenario",
                    "expected": "Feature works",
                    "actual": "",
                    "evidence_paths": [],
                    "limitations": []
                }]
            }
            path = root / "evidence.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(ValueError):
                V19.validate_evidence(root, path)

    def test_v19_contract_append_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "SKILL.md"
            skill.write_text("---\nname: example\ndescription: Example skill\n---\n\nBody\n", encoding="utf-8")
            self.assertTrue(PATCHER.add_v19_contract(skill))
            self.assertFalse(PATCHER.add_v19_contract(skill))
            self.assertEqual(skill.read_text(encoding="utf-8").count("## V19 verification and evaluation contract"), 1)

    def test_successful_migration_updates_both_inherited_audits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            v17audit = root / "v17/tools/audit_cumulative_package.py"
            v17audit.parent.mkdir(parents=True)
            v17audit.write_text(
                "EXPECTED_INSTALLED_SKILLS = 175\n" + PATCHER.OLD_V17_MANIFESTS + "\n",
                encoding="utf-8",
            )
            v18audit = root / "v18/tools/audit_cumulative_package.py"
            v18audit.parent.mkdir(parents=True)
            v18audit.write_text(
                "if len(skills)!=175:\n" + PATCHER.OLD_V18_POLICIES + "\n",
                encoding="utf-8",
            )
            PATCHER.migrate_cumulative_audits(root)
            migrated_v17 = v17audit.read_text(encoding="utf-8")
            migrated_v18 = v18audit.read_text(encoding="utf-8")
            self.assertIn("EXPECTED_INSTALLED_SKILLS = 180", migrated_v17)
            self.assertIn("V19_SHA256SUMS.txt", migrated_v17)
            self.assertIn("if len(skills)!=180:", migrated_v18)
            self.assertIn("V19_SHA256SUMS.txt", migrated_v18)

    def test_v19_audit_migration_fails_closed_on_unexpected_v17_manifest_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            audit = root / "v17/tools/audit_cumulative_package.py"
            audit.parent.mkdir(parents=True)
            audit.write_text(
                'EXPECTED_INSTALLED_SKILLS = 175\n' + PATCHER.OLD_V17_MANIFESTS.replace(
                    '"V18_SHA256SUMS.txt"', '"V17_SHA256SUMS.txt"'
                ) + "\n",
                encoding="utf-8",
            )
            v18audit = root / "v18/tools/audit_cumulative_package.py"
            v18audit.parent.mkdir(parents=True)
            v18audit.write_text(
                "if len(skills)!=175:\n" + PATCHER.OLD_V18_POLICIES + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                PATCHER.migrate_cumulative_audits(root)
            self.assertIn("175", audit.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
