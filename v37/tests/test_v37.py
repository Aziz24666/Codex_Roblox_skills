from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v37


def criterion(key: str, kind: str = "static") -> dict:
    return {"criterion_id": key, "description": f"Verify {key} behavior.", "verification_kind": kind}


def task(key: str, paths: list[str], *, dependencies: list[str] | None = None, criteria: list[dict] | None = None, risk: str = "low", human: bool = False) -> dict:
    return {
        "task_id": key,
        "title": f"Implement {key}",
        "objective": f"Complete the scoped implementation for {key}.",
        "depends_on": dependencies or [],
        "allowed_paths": paths,
        "risk": risk,
        "human_review_required": human,
        "acceptance_criteria": criteria or [criterion(f"{key}-checks")],
    }


def plan(*tasks: dict) -> dict:
    selected = list(tasks) if tasks else [
        task("server-contract", ["src/server"], criteria=[criterion("server-authority"), criterion("server-tests", "automated_test")], risk="medium", human=True),
        task("client-ui", ["src/client"], dependencies=["server-contract"], criteria=[criterion("client-ui"), criterion("studio-smoke", "studio_manual")], risk="medium", human=True),
        task("regression-checks", ["tests"], dependencies=["client-ui"], criteria=[criterion("regression-suite", "automated_test")]),
    ]
    return {
        "schema_version": 1,
        "plan_id": "impl-plan-a13b9c7d2e4f",
        "project_key": "sample-game",
        "generated_at": "2026-11-27T12:00:00Z",
        "goal": "Implement a server-owned feature with a client interface and regression coverage.",
        "scope": {"included_paths": ["src", "tests"], "excluded_paths": ["src/legacy"]},
        "tasks": selected,
    }


def report(data: dict | None = None) -> dict:
    p = data or plan()
    return {
        "schema_version": 1,
        "plan_id": p["plan_id"],
        "generated_at": "2026-11-27T13:00:00Z",
        "task_results": [
            {
                "task_id": "server-contract",
                "status": "completed",
                "changed_files": ["src/server/FeatureService.lua"],
                "evidence_refs": [],
                "criteria_results": [
                    {"criterion_id": "server-authority", "result": "pass"},
                    {"criterion_id": "server-tests", "result": "pass"},
                ],
            },
            {
                "task_id": "client-ui",
                "status": "completed",
                "changed_files": ["src/client/FeaturePanel.client.lua"],
                "evidence_refs": ["ev-111122223333"],
                "criteria_results": [
                    {"criterion_id": "client-ui", "result": "pass"},
                    {"criterion_id": "studio-smoke", "result": "pass"},
                ],
            },
            {
                "task_id": "regression-checks",
                "status": "completed",
                "changed_files": ["tests/FeatureService.spec.lua"],
                "evidence_refs": [],
                "criteria_results": [{"criterion_id": "regression-suite", "result": "pass"}],
            },
        ],
    }


class V37Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        self.temp.cleanup()


class PlanValidationTests(V37Fixture):
    def test_valid_plan(self) -> None:
        self.assertEqual(v37.validate_plan(plan()), [])

    def test_topological_order_is_stable_and_respects_dependencies(self) -> None:
        result = v37.audit_plan(plan())
        order = result["execution_order"]
        self.assertLess(order.index("server-contract"), order.index("client-ui"))
        self.assertLess(order.index("client-ui"), order.index("regression-checks"))

    def test_unknown_plan_field_is_rejected(self) -> None:
        data = plan()
        data["private_player_records"] = []
        self.assertTrue(any("unsupported field" in item for item in v37.validate_plan(data)))

    def test_unknown_task_field_is_rejected(self) -> None:
        data = plan()
        data["tasks"][0]["unreviewed_note"] = "not permitted"
        self.assertTrue(any("unsupported field" in item for item in v37.validate_plan(data)))

    def test_duplicate_task_id_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/a"]), task("feature-a", ["src/b"]))
        self.assertTrue(any("Duplicate task_id" in item for item in v37.validate_plan(data)))

    def test_missing_dependency_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/a"], dependencies=["missing-task"]))
        self.assertTrue(any("missing dependency" in item for item in v37.validate_plan(data)))

    def test_dependency_cycle_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/a"], dependencies=["feature-b"]), task("feature-b", ["src/b"], dependencies=["feature-a"]))
        self.assertTrue(any("contains a cycle" in item for item in v37.validate_plan(data)))

    def test_self_dependency_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/a"], dependencies=["feature-a"]))
        self.assertTrue(any("cannot depend on itself" in item for item in v37.validate_plan(data)))

    def test_independent_overlapping_scopes_are_rejected(self) -> None:
        data = plan(task("feature-a", ["src"]), task("feature-b", ["src/server"]))
        self.assertTrue(any("overlapping allowed_paths" in item for item in v37.validate_plan(data)))

    def test_overlapping_scopes_are_allowed_when_dependency_ordered(self) -> None:
        data = plan(task("feature-a", ["src"]), task("feature-b", ["src/server"], dependencies=["feature-a"]))
        self.assertEqual(v37.validate_plan(data), [])

    def test_task_path_outside_included_scope_is_rejected(self) -> None:
        data = plan(task("feature-a", ["plugins"]))
        self.assertTrue(any("outside included_paths" in item for item in v37.validate_plan(data)))

    def test_task_path_overlapping_excluded_scope_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/legacy"]))
        self.assertTrue(any("is inside excluded_paths" in item for item in v37.validate_plan(data)))

    def test_included_path_inside_excluded_scope_is_rejected(self) -> None:
        data = plan()
        data["scope"]["included_paths"] = ["src/legacy"]
        self.assertTrue(any("is entirely within an excluded path" in item for item in v37.validate_plan(data)))

    def test_high_risk_requires_human_review(self) -> None:
        data = plan(task("feature-a", ["src/a"], risk="high", human=False))
        self.assertTrue(any("high risk" in item for item in v37.validate_plan(data)))

    def test_manual_verification_requires_human_review(self) -> None:
        data = plan(task("feature-a", ["src/a"], criteria=[criterion("studio-check", "studio_manual")], human=False))
        self.assertTrue(any("Studio/runtime criteria" in item for item in v37.validate_plan(data)))

    def test_duplicate_criterion_id_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/a"], criteria=[criterion("same-id"), criterion("same-id")]))
        self.assertTrue(any("duplicates criterion_id" in item for item in v37.validate_plan(data)))

    def test_path_traversal_is_rejected(self) -> None:
        data = plan(task("feature-a", ["src/../outside"]))
        self.assertTrue(any("not a safe project-relative path" in item for item in v37.validate_plan(data)))

    def test_malformed_risk_type_does_not_crash(self) -> None:
        data = plan()
        data["tasks"][0]["risk"] = []
        self.assertTrue(v37.validate_plan(data))

    def test_malformed_dependency_type_does_not_crash(self) -> None:
        data = plan()
        data["tasks"][0]["depends_on"] = None
        self.assertTrue(v37.validate_plan(data))


class ReportValidationTests(V37Fixture):
    def test_valid_complete_report(self) -> None:
        p = plan()
        self.assertEqual(v37.validate_report(p, report(p)), [])

    def test_complete_report_audit_is_complete(self) -> None:
        p = plan()
        result = v37.audit_report(p, report(p))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["summary"]["status_counts"]["completed"], 3)

    def test_report_must_match_plan_id(self) -> None:
        p = plan()
        data = report(p)
        data["plan_id"] = "impl-plan-aaaaaaaa"
        self.assertTrue(any("does not match" in item for item in v37.validate_report(p, data)))

    def test_report_requires_each_planned_task(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"].pop()
        self.assertTrue(any("exactly one result" in item for item in v37.validate_report(p, data)))

    def test_report_rejects_duplicate_task_result(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][2]["task_id"] = "client-ui"
        self.assertTrue(any("Duplicate task result" in item for item in v37.validate_report(p, data)))

    def test_changed_file_outside_task_scope_is_rejected(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["changed_files"] = ["src/client/Unexpected.lua"]
        self.assertTrue(any("outside task server-contract allowed_paths" in item for item in v37.validate_report(p, data)))

    def test_changed_file_in_excluded_scope_is_rejected(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["changed_files"] = ["src/legacy/Old.lua"]
        self.assertTrue(any("outside project scope or is excluded" in item for item in v37.validate_report(p, data)))

    def test_manual_pass_requires_evidence_reference(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][1]["evidence_refs"] = []
        self.assertTrue(any("needs an evidence_ref" in item for item in v37.validate_report(p, data)))

    def test_completed_task_requires_all_criteria_passed(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["criteria_results"].pop()
        self.assertTrue(any("missing acceptance result" in item for item in v37.validate_report(p, data)))

    def test_completed_task_requires_completed_dependencies(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["status"] = "in_progress"
        self.assertTrue(any("completed before dependency" in item for item in v37.validate_report(p, data)))

    def test_bad_evidence_reference_is_rejected(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][1]["evidence_refs"] = ["https://private.example/evidence"]
        self.assertTrue(any("opaque ev-" in item for item in v37.validate_report(p, data)))

    def test_not_started_task_cannot_report_changes(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][2]["status"] = "not_started"
        self.assertTrue(any("cannot report changed files" in item for item in v37.validate_report(p, data)))

    def test_malformed_task_status_does_not_crash(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["status"] = []
        self.assertTrue(v37.validate_report(p, data))

    def test_malformed_criterion_result_does_not_crash(self) -> None:
        p = plan()
        data = report(p)
        data["task_results"][0]["criteria_results"][0]["result"] = []
        self.assertTrue(v37.validate_report(p, data))


class PathSafetyTests(V37Fixture):
    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v37.safe_project_path(self.root, "C:/outside.json")

    def test_parent_traversal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v37.safe_project_path(self.root, "../outside.json")

    def test_symlink_traversal_is_rejected(self) -> None:
        outside = self.root.parent / "v37-outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "linked-file.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            outside.unlink()
            self.skipTest("Symlinks are unavailable on this runner.")
        with self.assertRaises(ValueError):
            v37.safe_project_path(self.root, "linked-file.txt")
        outside.unlink()

    def test_atomic_json_output_is_project_local(self) -> None:
        v37.write_json(self.root, "reports/summary.json", {"status": "complete"})
        parsed = json.loads((self.root / "reports/summary.json").read_text(encoding="utf-8"))
        self.assertEqual(parsed["status"], "complete")

    def test_output_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v37.write_json(self.root, "../escape.json", {"status": "complete"})


if __name__ == "__main__":
    unittest.main()
