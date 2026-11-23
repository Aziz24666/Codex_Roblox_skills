from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v33  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402


def valid_plan() -> dict:
    return {
        "schema_version": 1,
        "suite_id": "suite-a13b9c7d2e4f",
        "max_simulated_clients": 4,
        "platforms": ["desktop", "mobile"],
        "network_profiles": ["baseline", "high_latency"],
        "tests": [
            {"id": "TC-STATIC-000", "scenario": "remote_validation", "category": "security",
             "priority": "P1", "execution": "static_local", "clients": 1,
             "platforms": ["desktop"], "expected": "invalid_request_rejected"},
            {"id": "TC-SMOKE-001", "scenario": "baseline_smoke", "category": "smoke",
             "priority": "P0", "execution": "studio_manual", "clients": 1,
             "platforms": ["desktop"], "expected": "no_unhandled_errors"},
            {"id": "TC-JOIN-002", "scenario": "mid_session_join", "category": "multiplayer",
             "priority": "P1", "execution": "studio_scripted", "clients": 4,
             "platforms": ["desktop"], "expected": "players_replicated"},
            {"id": "TC-UI-003", "scenario": "touch_navigation", "category": "ui",
             "priority": "P1", "execution": "studio_manual", "clients": 1,
             "platforms": ["mobile"], "expected": "ui_action_received"},
            {"id": "TC-REMOTE-004", "scenario": "remote_validation", "category": "security",
             "priority": "P0", "execution": "studio_scripted", "clients": 2,
             "platforms": ["desktop"], "expected": "invalid_request_rejected"},
        ],
    }


def valid_report(plan: dict | None = None, run_ref: str = "run-0f1e2d3c4b5a") -> dict:
    plan = plan or valid_plan()
    return {
        "schema_version": 1,
        "suite_id": plan["suite_id"],
        "run_ref": run_ref,
        "created_at": "2026-11-23T13:00:00Z",
        "environment": {
            "runner": "studio_manual",
            "studio_version": "0.700.0.7000000",
            "platform": "desktop",
            "network_profile": "baseline",
            "simulated_clients": 4,
        },
        "results": [
            {"test_id": "TC-STATIC-000", "status": "pass", "outcome_code": "passed",
             "executed_at": "2026-11-23T12:10:00Z", "evidence_ref": "ev-111122223333"},
            {"test_id": "TC-SMOKE-001", "status": "pass", "outcome_code": "passed",
             "executed_at": "2026-11-23T12:12:00Z"},
            {"test_id": "TC-JOIN-002", "status": "pass", "outcome_code": "passed",
             "executed_at": "2026-11-23T12:20:00Z", "evidence_ref": "ev-222233334444"},
            {"test_id": "TC-UI-003", "status": "blocked", "outcome_code": "device_profile_unavailable",
             "executed_at": None},
            {"test_id": "TC-REMOTE-004", "status": "pass", "outcome_code": "passed",
             "executed_at": "2026-11-23T12:40:00Z", "evidence_ref": "ev-333344445555"},
        ],
    }


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def put(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class PlanTests(Fixture):
    def test_valid_plan(self) -> None:
        self.assertEqual(v33.validate_plan(valid_plan()), [])

    def test_duplicate_test_ids_rejected(self) -> None:
        plan = valid_plan()
        plan["tests"][1]["id"] = plan["tests"][0]["id"]
        self.assertTrue(any("Duplicate test ID" in item for item in v33.validate_plan(plan)))

    def test_max_simulated_clients_cannot_exceed_eight(self) -> None:
        plan = valid_plan()
        plan["max_simulated_clients"] = 9
        self.assertTrue(any("between 1 and 8" in item for item in v33.validate_plan(plan)))

    def test_case_client_count_must_fit_plan(self) -> None:
        plan = valid_plan()
        plan["tests"][1]["clients"] = 5
        self.assertTrue(any("exceeds max_simulated_clients" in item for item in v33.validate_plan(plan)))

    def test_unknown_fields_rejected(self) -> None:
        plan = valid_plan()
        plan["private_notes"] = "should not be accepted"
        self.assertTrue(any("unsupported fields" in item for item in v33.validate_plan(plan)))

    def test_invalid_scenario_rejected(self) -> None:
        plan = valid_plan()
        plan["tests"][0]["scenario"] = "unknown_scenario"
        self.assertTrue(any("scenario" in item for item in v33.validate_plan(plan)))

    def test_malformed_unhashable_values_do_not_crash(self) -> None:
        plan = valid_plan()
        plan["tests"][0]["scenario"] = ["unexpected"]
        plan["tests"][0]["category"] = {"bad": "value"}
        plan["tests"][0]["execution"] = []
        self.assertTrue(v33.validate_plan(plan))

    def test_unhashable_plan_platform_values_do_not_crash(self) -> None:
        plan = valid_plan()
        plan["platforms"] = [{"unexpected": "value"}]
        self.assertTrue(v33.validate_plan(plan))

    def test_boolean_is_not_accepted_as_client_integer(self) -> None:
        plan = valid_plan()
        plan["max_simulated_clients"] = True
        self.assertTrue(any("max_simulated_clients" in item for item in v33.validate_plan(plan)))


class ReportTests(Fixture):
    def test_valid_complete_report(self) -> None:
        self.assertEqual(v33.validate_report(valid_report(), valid_plan()), [])

    def test_missing_result_is_not_a_pass(self) -> None:
        report = valid_report()
        report["results"].pop()
        self.assertTrue(any("missing results" in item for item in v33.validate_report(report, valid_plan())))

    def test_duplicate_result_rejected(self) -> None:
        report = valid_report()
        report["results"][1]["test_id"] = report["results"][0]["test_id"]
        self.assertTrue(any("Duplicate result" in item for item in v33.validate_report(report, valid_plan())))

    def test_unknown_report_fields_rejected(self) -> None:
        report = valid_report()
        report["raw_logs"] = "private details"
        self.assertTrue(any("unsupported fields" in item for item in v33.validate_report(report, valid_plan())))

    def test_player_identity_fields_rejected(self) -> None:
        report = valid_report()
        report["player_user_id"] = 1234
        self.assertTrue(any("unsupported fields" in item for item in v33.validate_report(report, valid_plan())))

    def test_pass_requires_pass_outcome(self) -> None:
        report = valid_report()
        report["results"][0]["outcome_code"] = "assertion_failed"
        self.assertTrue(any("pass status requires" in item for item in v33.validate_report(report, valid_plan())))

    def test_fail_requires_failure_outcome(self) -> None:
        report = valid_report()
        report["results"][0]["status"] = "fail"
        report["results"][0]["outcome_code"] = "passed"
        self.assertTrue(any("fail status requires" in item for item in v33.validate_report(report, valid_plan())))

    def test_not_run_requires_null_timestamp(self) -> None:
        report = valid_report()
        report["results"][0]["status"] = "not_run"
        report["results"][0]["outcome_code"] = "not_executed"
        report["results"][0]["executed_at"] = "2026-11-23T12:10:00Z"
        self.assertTrue(any("must be null for a not_run" in item for item in v33.validate_report(report, valid_plan())))

    def test_report_suite_must_match_plan(self) -> None:
        report = valid_report()
        report["suite_id"] = "suite-ffffeeee1111"
        self.assertTrue(any("must match" in item for item in v33.validate_report(report, valid_plan())))

    def test_evidence_reference_must_be_opaque(self) -> None:
        report = valid_report()
        report["results"][0]["evidence_ref"] = "../private/player-log.txt"
        self.assertTrue(any("opaque ev-" in item for item in v33.validate_report(report, valid_plan())))

    def test_local_static_cannot_pass_a_studio_case(self) -> None:
        report = valid_report()
        report["environment"] = {
            "runner": "local_static", "studio_version": "not_applicable",
            "platform": "desktop", "network_profile": "baseline", "simulated_clients": 1,
        }
        for result in report["results"]:
            if result["test_id"] != "TC-STATIC-000":
                result.update(status="not_run", outcome_code="not_executed", executed_at=None)
        self.assertEqual(v33.validate_report(report, valid_plan()), [])

    def test_local_static_studio_pass_is_rejected(self) -> None:
        report = valid_report()
        report["environment"] = {
            "runner": "local_static", "studio_version": "not_applicable",
            "platform": "desktop", "network_profile": "baseline", "simulated_clients": 1,
        }
        self.assertTrue(any("cannot pass or fail a Studio test" in item for item in v33.validate_report(report, valid_plan())))

    def test_malformed_unhashable_status_values_do_not_crash(self) -> None:
        report = valid_report()
        report["results"][0]["status"] = ["pass"]
        report["results"][0]["outcome_code"] = {"code": "passed"}
        self.assertTrue(v33.validate_report(report, valid_plan()))

    def test_fail_status_with_unhashable_outcome_does_not_crash(self) -> None:
        report = valid_report()
        report["results"][0]["status"] = "fail"
        report["results"][0]["outcome_code"] = {"code": "assertion_failed"}
        self.assertTrue(v33.validate_report(report, valid_plan()))

    def test_report_timestamp_requires_timezone(self) -> None:
        report = valid_report()
        report["created_at"] = "2026-11-23T13:00:00"
        self.assertTrue(any("timezone" in item for item in v33.validate_report(report, valid_plan())))


class ComparisonTests(Fixture):
    def test_regression_blocker_gap_and_improvement_are_separated(self) -> None:
        baseline = valid_report(run_ref="run-aaaaaaaaaaaa")
        current = valid_report(run_ref="run-bbbbbbbbbbbb")
        current["results"][1].update(status="fail", outcome_code="assertion_failed")
        current["results"][2].update(status="blocked", outcome_code="studio_unavailable", executed_at=None)
        current["results"][3].update(status="not_run", outcome_code="not_executed", executed_at=None)
        current["results"][4].update(status="pass", outcome_code="passed")
        baseline["results"][3].update(status="fail", outcome_code="ui_input_missing", executed_at="2026-11-23T12:30:00Z")
        comparison = v33.compare_reports(baseline, current)
        self.assertEqual(comparison["counts"]["regressions"], 1)
        self.assertEqual(comparison["counts"]["newly_blocked"], 1)
        self.assertEqual(comparison["counts"]["coverage_gaps"], 1)
        self.assertEqual(comparison["counts"]["improvements"], 1)

    def test_comparison_never_calls_a_blocked_test_a_pass(self) -> None:
        baseline = valid_report(run_ref="run-aaaaaaaaaaaa")
        current = valid_report(run_ref="run-bbbbbbbbbbbb")
        current["results"][0].update(status="blocked", outcome_code="setup_incomplete", executed_at=None)
        comparison = v33.compare_reports(baseline, current)
        self.assertEqual(comparison["counts"]["newly_blocked"], 1)
        self.assertEqual(comparison["counts"]["regressions"], 0)


class PathAndAuditTests(Fixture):
    def test_project_path_rejects_parent_traversal(self) -> None:
        with self.assertRaises(ValueError):
            v33.safe_project_path(self.root, "../outside.json")

    def test_project_path_rejects_absolute_path(self) -> None:
        with self.assertRaises(ValueError):
            v33.safe_project_path(self.root, str(self.root / "outside.json"))

    def test_symlink_path_is_rejected(self) -> None:
        outside = self.root.parent / "outside-v33-test.txt"
        outside.write_text("x", encoding="utf-8")
        link = self.root / "linked.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable in this environment.")
        with self.assertRaises(ValueError):
            v33.safe_project_path(self.root, "linked.txt", must_exist=True)

    def test_audit_is_static_and_inventory_only(self) -> None:
        self.put("ServerScriptService/Main.server.lua",
                 'local service = game:GetService("StudioTestService")\n'
                 'local simulator = game:GetService("StudioDeviceSimulatorService")\n'
                 'local input = UserInputService:CreateVirtualInput()\n')
        self.put("Tests/Join.spec.luau", "return {}\n")
        report = v33.audit_project(self.root)
        self.assertEqual(report["inventory"]["luau_files_discovered"], 2)
        self.assertEqual(report["inventory"]["test_candidate_files"], 1)
        self.assertEqual(report["inventory"]["studio_test_service_references"], 1)
        self.assertEqual(report["inventory"]["device_simulator_service_references"], 1)
        self.assertEqual(report["inventory"]["virtual_input_references"], 1)
        self.assertFalse(report["studio_execution_performed"])
        self.assertEqual(report["execution_status"], "static_inventory_only")

    def test_json_non_finite_constants_rejected(self) -> None:
        self.put("plan.json", '{"value": NaN}')
        with self.assertRaises(ValueError):
            v33.load_json(self.root, "plan.json")


class PatcherAndPackageTests(Fixture):
    def create_source(self) -> Path:
        source = self.root / "repo" / "v33"
        (source / "tools").mkdir(parents=True)
        (source / "skills").mkdir()
        (source / "VERSION").write_text("33.0.0\n", encoding="utf-8")
        (source / "tools" / "v33.py").write_text("# cli\n", encoding="utf-8")
        for name in (
            "roblox-studio-automated-playtesting-v33",
            "roblox-multiplayer-regression-testing-v33",
            "roblox-device-and-input-testing-v33",
            "roblox-test-evidence-and-defect-triage-v33",
        ):
            skill = source / "skills" / name / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(f"---\nname: {name}\ndescription: test skill\n---\n", encoding="utf-8")
        repo = source.parent
        for name in ("README.md", "INDEX.md", "INDEX_V32.md", "INDEX_V33.md",
                     "RELEASE_NOTES_V32.md", "RELEASE_NOTES_V33.md"):
            (repo / name).write_text("V33 236 native Codex skills\n", encoding="utf-8")
        (repo / "tools").mkdir(exist_ok=True)
        (repo / "tools" / "repository_audit.py").write_text("# audit\n", encoding="utf-8")
        workflow = repo / ".github" / "workflows"
        workflow.mkdir(parents=True)
        (workflow / "v32-quality.yml").write_text("v32\n", encoding="utf-8")
        (workflow / "v33-quality.yml").write_text("v33\n", encoding="utf-8")
        return source

    def create_package(self, *, collision: bool = False) -> Path:
        package = self.root / ("package-collision" if collision else "package")
        skills = package / ".agents" / "skills"
        skills.mkdir(parents=True)
        (package / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
        for index in range(232):
            name = "roblox-studio-automated-playtesting-v33" if collision and index == 0 else f"legacy-{index:03d}"
            target = skills / name / "SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("---\nname: test\ndescription: legacy\n---\n", encoding="utf-8")
        return package

    def test_patcher_installs_four_skills_and_is_idempotent(self) -> None:
        source = self.create_source()
        package = self.create_package()
        self.assertEqual(patch_cumulative_package.patch(package, source), 236)
        self.assertEqual(len(list((package / ".agents" / "skills").glob("*/SKILL.md"))), 236)
        self.assertIn(patch_cumulative_package.MARKER, (package / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(patch_cumulative_package.patch(package, source), 236)

    def test_patcher_rejects_name_collision(self) -> None:
        source = self.create_source()
        package = self.create_package(collision=True)
        with self.assertRaises(ValueError):
            patch_cumulative_package.patch(package, source)

    def test_package_auditor_reports_missing_v33_files(self) -> None:
        problems = audit_cumulative_package.audit(self.root)
        self.assertTrue(any("Expected 236 native skills" in item for item in problems))
        self.assertTrue(any("Missing required file" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
