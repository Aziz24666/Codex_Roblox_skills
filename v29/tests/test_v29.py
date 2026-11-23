from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v29  # noqa: E402
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

class StaticAuditTests(Fixture):
    def test_static_audit_finds_hot_path_signals_without_claiming_measurements(self):
        self.put("src/Loop.server.lua",
            "while true do\n    task.wait(0.01)\nend\n"
            "RunService.Heartbeat:Connect(function()\n"
            "    local all = workspace:GetDescendants()\n"
            "    local clone = template:Clone()\nend)\n")
        report = v29.audit_source(self.root)
        self.assertGreaterEqual(report["finding_counts"]["high"], 1)
        self.assertGreaterEqual(report["finding_counts"]["medium"], 1)
        self.assertEqual(report["measurement_status"], "not_measured_by_static_scan")
        self.assertTrue(any("not a Luau parser" in item for item in report["limitations"]))

    def test_comments_and_non_luau_files_are_ignored(self):
        self.put("src/Main.lua", "-- while true do\nreturn true\n")
        self.put("src/notes.txt", "Instance.new('Part')\n")
        report = v29.audit_source(self.root)
        self.assertEqual(report["inventory"]["luau_files_discovered"], 1)
        self.assertEqual(sum(report["finding_counts"].values()), 0)

    def test_symlinked_sources_are_skipped(self):
        real = self.put("src/real.lua", "return true\n")
        link = self.root / "src" / "linked.lua"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable.")
        warnings = []
        found = v29.iter_luau_files(self.root, 100, warnings)
        self.assertEqual([p.name for p in found], ["real.lua"])
        self.assertTrue(any("symlink" in item for item in warnings))

    def test_report_stops_at_finding_cap(self):
        self.put("src/Main.luau", "local x = Instance.new('Folder')\n" * 600)
        report = v29.audit_source(self.root)
        self.assertEqual(len(report["findings"]), 500)
        self.assertTrue(any("500-finding" in warning for warning in report["warnings"]))

class BudgetTests(Fixture):
    def sample_budgets(self):
        return {"schema_version": 1, "budgets": {
            "low_end_mobile": {"frame_time_ms_p95": 33.3, "memory_mb": 450},
            "high_end_mobile": {"frame_time_ms_p95": 25, "memory_mb": 600},
            "desktop": {"frame_time_ms_p95": 16.7, "memory_mb": 1000},
        }}

    def test_all_device_profiles_and_positive_limits_pass(self):
        self.assertEqual(v29.validate_budgets(self.sample_budgets()), [])

    def test_missing_profile_unknown_metric_and_nonpositive_limit_fail(self):
        data = self.sample_budgets()
        del data["budgets"]["desktop"]
        data["budgets"]["low_end_mobile"]["fps"] = 60
        data["budgets"]["high_end_mobile"]["memory_mb"] = 0
        errors = v29.validate_budgets(data)
        self.assertTrue(any("Missing device profiles" in item for item in errors))
        self.assertTrue(any("Unknown metrics" in item for item in errors))
        self.assertTrue(any("finite positive number" in item for item in errors))

class MeasurementComparisonTests(Fixture):
    def capture(self, build, profile="low_end_mobile", **metrics):
        return {"schema_version": 1, "build": build, "device_profile": profile,
            "measurement_source": "Studio profiler capture on test hardware",
            "metrics": metrics or {"frame_time_ms_p50": 18, "frame_time_ms_p95": 30, "memory_mb": 400}}

    def test_comparison_detects_regression_and_budget_violation(self):
        baseline = self.capture("base", frame_time_ms_p50=18, frame_time_ms_p95=30, memory_mb=400)
        candidate = self.capture("next", frame_time_ms_p50=18.5, frame_time_ms_p95=36, memory_mb=470)
        budgets = {"schema_version": 1, "budgets": {
            "low_end_mobile": {"frame_time_ms_p95": 33.3, "memory_mb": 450},
            "high_end_mobile": {"memory_mb": 600}, "desktop": {"memory_mb": 1000}}}
        result = v29.compare_measurements(baseline, candidate, budgets, 5.0)
        self.assertEqual(result["regression_count"], 2)
        self.assertEqual(result["budget_violation_count"], 2)
        p95 = next(item for item in result["metrics"] if item["metric"] == "frame_time_ms_p95")
        self.assertEqual(p95["delta_pct"], 20.0)
        self.assertTrue(p95["regression"])
        self.assertTrue(p95["over_budget"])

    def test_invalid_capture_unknown_metric_and_p95_order_fail(self):
        data = self.capture("bad", frame_time_ms_p50=35, frame_time_ms_p95=20)
        self.assertTrue(any("cannot be lower" in item for item in v29.validate_measurement(data)))
        data["metrics"]["fps"] = 60
        self.assertTrue(any("Unknown metrics" in item for item in v29.validate_measurement(data)))

    def test_profiles_and_builds_must_match_appropriately(self):
        base = self.capture("same")
        with self.assertRaisesRegex(ValueError, "same device_profile"):
            v29.compare_measurements(base, self.capture("new", "desktop"))
        with self.assertRaisesRegex(ValueError, "build identifiers must differ"):
            v29.compare_measurements(base, self.capture("same"))

    def test_missing_metric_is_reported_not_fabricated(self):
        baseline = self.capture("base", frame_time_ms_p95=30, memory_mb=400)
        candidate = self.capture("next", memory_mb=390, script_cpu_ms=4)
        result = v29.compare_measurements(baseline, candidate)
        self.assertEqual(result["missing_from_candidate"], ["frame_time_ms_p95"])
        self.assertEqual(result["new_in_candidate"], ["script_cpu_ms"])
        self.assertEqual([item["metric"] for item in result["metrics"]], ["memory_mb"])

    def test_nonfinite_and_boolean_measurements_are_rejected(self):
        data = self.capture("bad", frame_time_ms_p95=float("nan"), memory_mb=True)
        self.assertGreaterEqual(len(v29.validate_measurement(data)), 2)

class PathAndCommandTests(Fixture):
    def test_paths_cannot_escape_project_or_follow_symlinks(self):
        with self.assertRaisesRegex(ValueError, "inside the selected project root"):
            v29.safe_project_path(self.root, "../outside.json")
        outside = Path(tempfile.mkdtemp())
        try:
            link = self.root / "outside-link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks are unavailable.")
            with self.assertRaisesRegex(ValueError, "symlink"):
                v29.safe_project_path(self.root, "outside-link/capture.json")
        finally:
            outside.rmdir()

    def test_atomic_json_and_combined_report(self):
        self.put("src/Main.lua", "local part = Instance.new('Part')\n")
        audit = v29.audit_source(self.root)
        audit_path = self.root / ".codex/reports/audit.json"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        v29.atomic_write_json(audit_path, audit)
        baseline = {"schema_version": 1, "build": "base", "device_profile": "desktop",
            "measurement_source": "manual repeatable run", "metrics": {"frame_time_ms_p95": 20}}
        candidate = dict(baseline, build="candidate", metrics={"frame_time_ms_p95": 18})
        comparison = v29.compare_measurements(baseline, candidate)
        summary = v29.build_summary(audit, comparison)
        self.assertEqual(summary["report_type"], "v29_performance_review")
        self.assertEqual(summary["measurement_comparison"]["candidate_build"], "candidate")
        self.assertTrue(audit_path.is_file())

class PackageTests(unittest.TestCase):
    def test_patch_is_idempotent_and_package_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills = package / ".agents" / "skills"
            for index in range(216):
                skill = skills / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(f"---\nname: legacy-{index:03}\ndescription: Legacy skill {index}.\n---\n", encoding="utf-8")
            (package / "AGENTS.md").write_text("# Agent rules\nNo gambling.\n", encoding="utf-8")
            for relative in audit_cumulative_package.REQUIRED_FILES:
                if relative.startswith(".agents/skills/") or relative.startswith("v29/"):
                    continue
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("{}\n" if relative.endswith(".json") else "# Fixture\n", encoding="utf-8")
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertEqual(audit_cumulative_package.audit(package), [])

if __name__ == "__main__":
    unittest.main()
