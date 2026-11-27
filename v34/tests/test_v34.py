from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v34  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402


def valid_capture(
    run_id: str = "perf-run-a13b9c7d2e4f",
    build_id: str = "build-before",
    memory_start: float = 500.0,
    lua_heap_start: float = 100.0,
    instance_start: int = 5000,
    heartbeat: float = 60.0,
    client_count: int = 4,
    source: str = "developer_console",
) -> dict:
    samples = []
    for index in range(7):
        samples.append({
            "elapsed_seconds": index * 600,
            "server_age_minutes": 100 + index * 10,
            "connected_clients": client_count,
            "metrics": {
                "server_memory_mb": memory_start + index * 4,
                "lua_heap_mb": lua_heap_start + index * 1.5,
                "instance_count": instance_start + index * 5,
                "server_cpu_ms_per_frame": 8.0 + index * 0.2,
                "server_heartbeat_fps": heartbeat,
                "replication_kbps": 220.0 + index,
            },
        })
    return {
        "schema_version": 1,
        "run_id": run_id,
        "build_id": build_id,
        "scenario": "steady_gameplay",
        "target": "server",
        "device_profile": "server",
        "measurement_source": source,
        "network_profile": "baseline",
        "player_count": 4,
        "started_at": "2026-11-27T10:00:00Z",
        "warmup_minutes": 5,
        "duration_minutes": 60,
        "sample_interval_seconds": 600,
        "evidence_ref": "ev-111122223333",
        "samples": samples,
    }


def valid_manifest() -> dict:
    return {
        "schema_version": 1,
        "suite_id": "perf-suite-a13b9c7d2e4f",
        "scenario": "steady_gameplay",
        "target": "server",
        "device_profile": "server",
        "measurement_source": "developer_console",
        "network_profile": "baseline",
        "player_count": 4,
        "duration_minutes": 60,
        "sample_interval_seconds": 600,
        "baseline_build": "build-before",
        "candidate_build": "build-after",
        "threshold_pct": 5.0,
        "baseline_captures": [
            ".codex/perf/base-1.json",
            ".codex/perf/base-2.json",
            ".codex/perf/base-3.json",
        ],
        "candidate_captures": [
            ".codex/perf/candidate-1.json",
            ".codex/perf/candidate-2.json",
            ".codex/perf/candidate-3.json",
        ],
    }


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def put_json(self, relative: str, payload: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path


class CaptureValidationTests(Fixture):
    def test_valid_capture_passes(self) -> None:
        self.assertEqual(v34.validate_capture(valid_capture()), [])

    def test_unknown_fields_rejected(self) -> None:
        capture = valid_capture()
        capture["player_user_id"] = 1234
        self.assertTrue(any("unsupported fields" in item for item in v34.validate_capture(capture)))

    def test_less_than_five_samples_rejected(self) -> None:
        capture = valid_capture()
        capture["samples"] = capture["samples"][:4]
        self.assertTrue(any("5-250" in item for item in v34.validate_capture(capture)))

    def test_elapsed_time_must_increase(self) -> None:
        capture = valid_capture()
        capture["samples"][3]["elapsed_seconds"] = capture["samples"][2]["elapsed_seconds"]
        self.assertTrue(any("increase strictly" in item for item in v34.validate_capture(capture)))

    def test_server_age_must_increase(self) -> None:
        capture = valid_capture()
        capture["samples"][4]["server_age_minutes"] = capture["samples"][3]["server_age_minutes"]
        self.assertTrue(any("server_age_minutes must increase" in item for item in v34.validate_capture(capture)))

    def test_sample_interval_is_checked(self) -> None:
        capture = valid_capture()
        capture["samples"][2]["elapsed_seconds"] = 1500
        self.assertTrue(any("sample interval" in item for item in v34.validate_capture(capture)))

    def test_duration_coverage_is_required(self) -> None:
        capture = valid_capture()
        capture["samples"] = capture["samples"][:5]
        self.assertTrue(any("75% of the declared" in item for item in v34.validate_capture(capture)))

    def test_metric_set_must_be_stable_across_samples(self) -> None:
        capture = valid_capture()
        del capture["samples"][2]["metrics"]["lua_heap_mb"]
        self.assertTrue(any("same metric set" in item for item in v34.validate_capture(capture)))

    def test_metric_boolean_is_not_a_number(self) -> None:
        capture = valid_capture()
        capture["samples"][0]["metrics"]["server_memory_mb"] = True
        self.assertTrue(any("finite non-negative number" in item for item in v34.validate_capture(capture)))

    def test_instance_count_must_be_integer(self) -> None:
        capture = valid_capture()
        capture["samples"][0]["metrics"]["instance_count"] = 5.5
        self.assertTrue(any("non-negative integer" in item for item in v34.validate_capture(capture)))

    def test_client_count_cannot_exceed_plan(self) -> None:
        capture = valid_capture()
        capture["samples"][1]["connected_clients"] = 5
        self.assertTrue(any("cannot exceed" in item for item in v34.validate_capture(capture)))

    def test_server_capture_requires_server_profile(self) -> None:
        capture = valid_capture()
        capture["device_profile"] = "desktop"
        self.assertTrue(any("server-target capture" in item for item in v34.validate_capture(capture)))

    def test_client_capture_requires_client_metrics_and_profile(self) -> None:
        capture = valid_capture()
        capture["target"] = "client"
        capture["device_profile"] = "low_end_mobile"
        for sample in capture["samples"]:
            del sample["metrics"]["replication_kbps"]
        self.assertTrue(any("client-side metric" in item for item in v34.validate_capture(capture)))

    def test_capture_rejects_naive_timestamp(self) -> None:
        capture = valid_capture()
        capture["started_at"] = "2026-11-27T10:00:00"
        self.assertTrue(any("timezone" in item for item in v34.validate_capture(capture)))

    def test_evidence_reference_must_be_opaque(self) -> None:
        capture = valid_capture()
        capture["evidence_ref"] = "../private/log.txt"
        self.assertTrue(any("opaque ev-" in item for item in v34.validate_capture(capture)))

    def test_bad_schema_version_rejected(self) -> None:
        capture = valid_capture()
        capture["schema_version"] = True
        self.assertTrue(any("integer 1" in item for item in v34.validate_capture(capture)))

    def test_malformed_enum_type_does_not_crash(self) -> None:
        capture = valid_capture()
        capture["scenario"] = ["steady_gameplay"]
        self.assertTrue(v34.validate_capture(capture))


class SoakAnalysisTests(Fixture):
    def test_stable_upward_memory_trend_emits_review_signal(self) -> None:
        report = v34.analyze_soak(valid_capture(), growth_threshold_pct=4, min_r_squared=0.7)
        memory = next(item for item in report["metrics"] if item["metric"] == "server_memory_mb")
        self.assertTrue(memory["growth_signal"])
        self.assertGreater(memory["slope_per_server_hour"], 0)
        self.assertEqual(report["execution_status"], "offline_analysis_of_supplied_capture")

    def test_unstable_client_load_suppresses_growth_signal(self) -> None:
        capture = valid_capture()
        capture["samples"][3]["connected_clients"] = 2
        report = v34.analyze_soak(capture, growth_threshold_pct=1, max_client_variance=1)
        self.assertFalse(report["connected_clients"]["stable_within_tolerance"])
        self.assertTrue(all(not item["growth_signal"] for item in report["metrics"]))

    def test_downward_memory_trend_is_not_growth_signal(self) -> None:
        capture = valid_capture()
        for index, sample in enumerate(capture["samples"]):
            sample["metrics"]["server_memory_mb"] = 700 - index * 10
        report = v34.analyze_soak(capture, growth_threshold_pct=1)
        memory = next(item for item in report["metrics"] if item["metric"] == "server_memory_mb")
        self.assertFalse(memory["growth_signal"])
        self.assertLess(memory["slope_per_server_hour"], 0)

    def test_noisy_trend_below_r_squared_threshold_not_flagged(self) -> None:
        capture = valid_capture()
        values = [500, 570, 510, 560, 515, 555, 520]
        for sample, value in zip(capture["samples"], values):
            sample["metrics"]["server_memory_mb"] = value
        report = v34.analyze_soak(capture, growth_threshold_pct=1, min_r_squared=0.95)
        memory = next(item for item in report["metrics"] if item["metric"] == "server_memory_mb")
        self.assertFalse(memory["growth_signal"])

    def test_first_value_zero_has_no_percentage_growth_claim(self) -> None:
        capture = valid_capture()
        for index, sample in enumerate(capture["samples"]):
            sample["metrics"]["instance_count"] = index * 100
        report = v34.analyze_soak(capture, growth_threshold_pct=1)
        count = next(item for item in report["metrics"] if item["metric"] == "instance_count")
        self.assertIsNone(count["delta_pct"])
        self.assertFalse(count["growth_signal"])

    def test_missing_memory_metrics_rejected(self) -> None:
        capture = valid_capture()
        for sample in capture["samples"]:
            del sample["metrics"]["server_memory_mb"]
            del sample["metrics"]["lua_heap_mb"]
            del sample["metrics"]["instance_count"]
        with self.assertRaisesRegex(ValueError, "no supported"):
            v34.analyze_soak(capture)

    def test_invalid_thresholds_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v34.analyze_soak(valid_capture(), growth_threshold_pct=0)
        with self.assertRaises(ValueError):
            v34.analyze_soak(valid_capture(), min_r_squared=1.2)
        with self.assertRaises(ValueError):
            v34.analyze_soak(valid_capture(), max_client_variance=-1)

    def test_linear_trend_returns_exact_slope(self) -> None:
        slope, intercept, r2 = v34.linear_trend([0, 1, 2, 3], [10, 12, 14, 16])
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 10.0)
        self.assertAlmostEqual(r2, 1.0)


class SuiteValidationTests(Fixture):
    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(v34.validate_suite(valid_manifest()), [])

    def test_two_runs_per_build_rejected(self) -> None:
        manifest = valid_manifest()
        manifest["baseline_captures"].pop()
        self.assertTrue(any("3-8 project-relative" in item for item in v34.validate_suite(manifest)))

    def test_same_build_identifiers_rejected(self) -> None:
        manifest = valid_manifest()
        manifest["candidate_build"] = manifest["baseline_build"]
        self.assertTrue(any("must differ" in item for item in v34.validate_suite(manifest)))

    def test_duplicate_paths_rejected(self) -> None:
        manifest = valid_manifest()
        manifest["candidate_captures"][0] = manifest["baseline_captures"][0]
        self.assertTrue(any("must be distinct" in item for item in v34.validate_suite(manifest)))

    def test_threshold_must_be_positive_and_bounded(self) -> None:
        manifest = valid_manifest()
        manifest["threshold_pct"] = 0
        self.assertTrue(any("threshold_pct" in item for item in v34.validate_suite(manifest)))
        manifest["threshold_pct"] = 101
        self.assertTrue(any("threshold_pct" in item for item in v34.validate_suite(manifest)))

    def test_unhashable_manifest_scenario_does_not_crash(self) -> None:
        manifest = valid_manifest()
        manifest["scenario"] = ["steady_gameplay"]
        self.assertTrue(v34.validate_suite(manifest))

    def test_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v34.safe_project_path(self.root, "../outside.json")

    def test_absolute_paths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v34.safe_project_path(self.root, str(self.root / "outside.json"))

    def test_windows_absolute_paths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            v34.safe_project_path(self.root, "C:/outside.json")

    def test_load_suite_accepts_matched_captures(self) -> None:
        manifest = valid_manifest()
        for index, path in enumerate(manifest["baseline_captures"]):
            self.put_json(path, valid_capture(f"perf-run-base{index:08d}", "build-before", 500 + index * 3))
        for index, path in enumerate(manifest["candidate_captures"]):
            self.put_json(path, valid_capture(f"perf-run-cand{index:08d}", "build-after", 650 + index * 3))
        self.put_json(".codex/perf/repeat-suite.json", manifest)
        loaded, baseline, candidate, errors = v34.load_suite(self.root, ".codex/perf/repeat-suite.json")
        self.assertEqual(errors, [])
        self.assertEqual(len(baseline), 3)
        self.assertEqual(len(candidate), 3)
        self.assertEqual(loaded["suite_id"], manifest["suite_id"])

    def test_load_suite_rejects_mismatched_capture_environment(self) -> None:
        manifest = valid_manifest()
        for index, path in enumerate(manifest["baseline_captures"]):
            capture = valid_capture(f"perf-run-base{index:08d}", "build-before")
            if index == 1:
                capture["player_count"] = 3
                for sample in capture["samples"]:
                    sample["connected_clients"] = 3
            self.put_json(path, capture)
        for index, path in enumerate(manifest["candidate_captures"]):
            self.put_json(path, valid_capture(f"perf-run-cand{index:08d}", "build-after"))
        self.put_json(".codex/perf/repeat-suite.json", manifest)
        _, _, _, errors = v34.load_suite(self.root, ".codex/perf/repeat-suite.json")
        self.assertTrue(any("does not match the repeat suite environment" in item for item in errors))

    def test_load_suite_rejects_wrong_build_ids(self) -> None:
        manifest = valid_manifest()
        for index, path in enumerate(manifest["baseline_captures"]):
            self.put_json(path, valid_capture(f"perf-run-base{index:08d}", "build-wrong"))
        for index, path in enumerate(manifest["candidate_captures"]):
            self.put_json(path, valid_capture(f"perf-run-cand{index:08d}", "build-after"))
        self.put_json(".codex/perf/repeat-suite.json", manifest)
        _, _, _, errors = v34.load_suite(self.root, ".codex/perf/repeat-suite.json")
        self.assertTrue(any("does not match the declared baseline_build" in item for item in errors))


class RepeatedComparisonTests(Fixture):
    def captures(self, build: str, prefix: str, memory: float, heartbeat: float = 60.0) -> list[dict]:
        return [
            valid_capture(f"perf-run-{prefix}{index:08d}", build, memory + index * 3, heartbeat=heartbeat)
            for index in range(3)
        ]

    def test_repeated_comparison_flags_memory_and_heartbeat_regressions(self) -> None:
        manifest = valid_manifest()
        baseline = self.captures("build-before", "base", 500, 60)
        candidate = self.captures("build-after", "cand", 650, 54)
        report = v34.compare_repeated(manifest, baseline, candidate)
        self.assertGreaterEqual(report["regression_count"], 2)
        memory = next(item for item in report["metrics"] if item["metric"] == "server_memory_mb")
        heartbeat = next(item for item in report["metrics"] if item["metric"] == "server_heartbeat_fps")
        self.assertGreater(memory["delta_pct"], 5)
        self.assertLess(heartbeat["delta_pct"], -5)
        self.assertTrue(memory["regression"])
        self.assertTrue(heartbeat["regression"])

    def test_improved_build_does_not_flag_higher_is_better_heartbeat(self) -> None:
        manifest = valid_manifest()
        baseline = self.captures("build-before", "base", 600, 58)
        candidate = self.captures("build-after", "cand", 500, 60)
        report = v34.compare_repeated(manifest, baseline, candidate)
        self.assertEqual(report["regression_count"], 0)
        self.assertEqual(report["gate_status"], "no_thresholded_regression_detected")

    def test_replication_is_context_only_not_auto_regression(self) -> None:
        manifest = valid_manifest()
        baseline = self.captures("build-before", "base", 500)
        candidate = self.captures("build-after", "cand", 500)
        for run in baseline:
            for sample in run["samples"]:
                sample["metrics"]["replication_kbps"] = 100
        for run in candidate:
            for sample in run["samples"]:
                sample["metrics"]["replication_kbps"] = 500
        report = v34.compare_repeated(manifest, baseline, candidate)
        replication = next(item for item in report["metrics"] if item["metric"] == "replication_kbps")
        self.assertEqual(replication["direction"], "context_only")
        self.assertIsNone(replication["regression"])

    def test_no_common_metrics_rejected(self) -> None:
        manifest = valid_manifest()
        baseline = self.captures("build-before", "base", 500)
        candidate = self.captures("build-after", "cand", 500)
        for run in baseline:
            for sample in run["samples"]:
                sample["metrics"] = {"server_memory_mb": sample["metrics"]["server_memory_mb"]}
        for run in candidate:
            for sample in run["samples"]:
                sample["metrics"] = {"server_heartbeat_fps": 60}
        with self.assertRaisesRegex(ValueError, "no common"):
            v34.compare_repeated(manifest, baseline, candidate)

    def test_zero_baseline_does_not_divide_by_zero(self) -> None:
        manifest = valid_manifest()
        baseline = self.captures("build-before", "base", 0)
        candidate = self.captures("build-after", "cand", 20)
        for run in baseline:
            for sample in run["samples"]:
                sample["metrics"]["server_memory_mb"] = 0
        report = v34.compare_repeated(manifest, baseline, candidate)
        memory = next(item for item in report["metrics"] if item["metric"] == "server_memory_mb")
        self.assertIsNone(memory["delta_pct"])
        self.assertIsNone(memory["regression"])


class PackageAndPathTests(Fixture):
    def create_source(self) -> Path:
        source = self.root / "repository" / "v34"
        (source / "tools").mkdir(parents=True)
        (source / "skills").mkdir()
        (source / "VERSION").write_text("34.0.0\n", encoding="utf-8")
        (source / "tools" / "v34.py").write_text("# V34 CLI\n", encoding="utf-8")
        names = (
            "roblox-performance-soak-and-memory-trend-v34",
            "roblox-microprofiler-capture-triage-v34",
            "roblox-repeated-benchmark-and-regression-v34",
            "roblox-live-performance-rollout-monitoring-v34",
        )
        for name in names:
            skill = source / "skills" / name / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(f"---\nname: {name}\ndescription: test skill\n---\n", encoding="utf-8")
        repo = source.parent
        for name in ("README.md", "INDEX.md", "INDEX_V31.md", "INDEX_V32.md", "INDEX_V33.md",
                     "INDEX_V34.md", "RELEASE_NOTES_V31.md", "RELEASE_NOTES_V32.md",
                     "RELEASE_NOTES_V33.md", "RELEASE_NOTES_V34.md"):
            (repo / name).write_text("V34 240 native Codex skills\n", encoding="utf-8")
        (repo / "tools").mkdir()
        (repo / "tools" / "repository_audit.py").write_text("# root audit\n", encoding="utf-8")
        workflow = repo / ".github" / "workflows"
        workflow.mkdir(parents=True)
        (workflow / "v33-quality.yml").write_text("v33\n", encoding="utf-8")
        (workflow / "v34-quality.yml").write_text("v34\n", encoding="utf-8")
        return source

    def create_package(self, collision: bool = False) -> Path:
        package = self.root / ("package-collision" if collision else "package")
        skills = package / ".agents" / "skills"
        skills.mkdir(parents=True)
        (package / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
        for index in range(236):
            name = "roblox-performance-soak-and-memory-trend-v34" if collision and index == 0 else f"legacy-{index:03d}"
            skill = skills / name / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: legacy\ndescription: baseline skill\n---\n", encoding="utf-8")
        return package

    def test_patcher_installs_four_skills_and_is_idempotent(self) -> None:
        source = self.create_source()
        package = self.create_package()
        self.assertEqual(patch_cumulative_package.patch(package, source), 240)
        self.assertEqual(len(list((package / ".agents" / "skills").glob("*/SKILL.md"))), 240)
        self.assertIn(patch_cumulative_package.MARKER, (package / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(patch_cumulative_package.patch(package, source), 240)

    def test_patcher_rejects_skill_collision(self) -> None:
        source = self.create_source()
        package = self.create_package(collision=True)
        with self.assertRaises(ValueError):
            patch_cumulative_package.patch(package, source)

    def test_cumulative_auditor_reports_missing_v34_package_files(self) -> None:
        problems = audit_cumulative_package.audit(self.root)
        self.assertTrue(any("Expected 240 native skills" in item for item in problems))
        self.assertTrue(any("Missing required file" in item for item in problems))

    def test_output_writer_creates_json(self) -> None:
        path = self.root / "nested" / "report.json"
        path.parent.mkdir(parents=True)
        v34.write_json(path, {"ok": True, "count": 3})
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True, "count": 3})

    def test_json_nan_constant_rejected(self) -> None:
        self.put_json("dummy.json", {"x": 1})
        bad = self.root / "bad.json"
        bad.write_text('{"x": NaN}', encoding="utf-8")
        with self.assertRaises(ValueError):
            v34.load_json(self.root, "bad.json")

    def test_symlink_input_rejected(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside-v34.json"
        outside.write_text("{}", encoding="utf-8")
        link = self.root / "linked.json"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable in this environment.")
        try:
            with self.assertRaises(ValueError):
                v34.safe_project_path(self.root, "linked.json", must_exist=True)
        finally:
            link.unlink(missing_ok=True)
            outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
