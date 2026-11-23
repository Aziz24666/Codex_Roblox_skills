from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v31  # noqa: E402
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

    def catalog(self):
        return {
            "schema_version": 1,
            "events": [
                {
                    "name": "MissionCompleted",
                    "method": "LogCustomEvent",
                    "purpose": "Count completed missions by finite mission category.",
                    "privacy_reviewed": True,
                    "fields": [
                        {"name": "mission_type", "slot": "CustomField01", "allowed_values": ["story", "daily", "side"]},
                        {"name": "difficulty", "slot": "CustomField02", "allowed_values": ["easy", "normal", "hard"]},
                    ],
                }
            ],
        }

    def policy(self):
        return {
            "schema_version": 1,
            "minimum_sample_size": 100,
            "maximum_age_hours": 48,
            "metrics": {
                "server_error_rate_pct": {
                    "direction": "max", "threshold": 2.0, "warning_threshold": 1.0,
                    "description": "Share of server sessions with a recorded error.",
                },
                "onboarding_completion_pct": {
                    "direction": "min", "threshold": 25.0, "warning_threshold": 35.0,
                    "description": "Aggregate completion of the onboarding path.",
                },
            },
        }

    def snapshot(self, **metrics):
        return {
            "schema_version": 1,
            "environment": "staging",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic aggregate test fixture",
            "sample_size": 500,
            "metrics": metrics or {
                "server_error_rate_pct": 0.5,
                "onboarding_completion_pct": 42.0,
            },
        }


class CatalogTests(Fixture):
    def test_valid_small_catalog_passes(self):
        self.assertEqual(v31.validate_catalog(self.catalog()), [])

    def test_duplicate_event_names_fail(self):
        data = self.catalog()
        data["events"].append(dict(data["events"][0]))
        self.assertTrue(any("Duplicate custom event name" in item for item in v31.validate_catalog(data)))

    def test_too_many_custom_events_fail(self):
        data = self.catalog()
        template = data["events"][0]
        data["events"] = [
            dict(template, name=f"Event{index}") for index in range(v31.CUSTOM_EVENT_LIMIT + 1)
        ]
        self.assertTrue(any("100-event" in item for item in v31.validate_catalog(data)))

    def test_too_many_custom_fields_fail(self):
        data = self.catalog()
        data["events"][0]["fields"] = [
            {"name": f"field_{index}", "slot": f"CustomField0{index + 1}", "allowed_values": ["a", "b", "c"]}
            for index in range(4)
        ]
        self.assertTrue(any("3-custom-field" in item for item in v31.validate_catalog(data)))

    def test_identifiers_and_personal_data_fields_fail(self):
        data = self.catalog()
        data["events"][0]["fields"].append(
            {"name": "user_id", "slot": "CustomField03", "allowed_values": ["one", "two"]}
        )
        self.assertTrue(any("identifiers and personal data" in item for item in v31.validate_catalog(data)))

    def test_custom_field_slots_must_match_roblox_enum_and_be_unique(self):
        data = self.catalog()
        data["events"][0]["fields"][0]["slot"] = "mission_type"
        self.assertTrue(any(".slot must be CustomField01" in item for item in v31.validate_catalog(data)))
        data = self.catalog()
        data["events"][0]["fields"][1]["slot"] = "CustomField01"
        self.assertTrue(any("maps more than one semantic field" in item for item in v31.validate_catalog(data)))

    def test_email_guid_and_long_numeric_values_fail(self):
        data = self.catalog()
        data["events"][0]["fields"][0]["allowed_values"] = [
            "test@example.com", "1234567890123", "123e4567-e89b-12d3-a456-426614174000"
        ]
        self.assertTrue(any("non-identifying strings" in item for item in v31.validate_catalog(data)))

    def test_custom_field_cartesian_combination_limit_is_checked(self):
        data = self.catalog()
        data["events"][0]["fields"] = [
            {"name": "mission_type", "slot": "CustomField01", "allowed_values": [f"mission_{i}" for i in range(90)]},
            {"name": "difficulty", "slot": "CustomField02", "allowed_values": [f"difficulty_{i}" for i in range(90)]},
        ]
        self.assertTrue(any("8,000-combination limit" in item for item in v31.validate_catalog(data)))


    def test_privacy_review_is_required(self):
        data = self.catalog()
        data["events"][0]["privacy_reviewed"] = False
        self.assertTrue(any("privacy_reviewed must be true" in item for item in v31.validate_catalog(data)))

    def test_telemetry_budget_cannot_exceed_documented_capacity(self):
        data = self.catalog()
        data["telemetry_budget"] = {
            "expected_calls_per_minute": 500,
            "maximum_concurrent_users": 10,
        }
        self.assertTrue(any("exceeds the documented global limit" in item for item in v31.validate_catalog(data)))


class SourceAuditTests(Fixture):
    def test_literal_custom_event_is_compared_with_catalog(self):
        self.put(
            "ServerScriptService/Analytics.server.lua",
            'local AnalyticsService = game:GetService("AnalyticsService")\\n'
            'AnalyticsService:LogCustomEvent(player, "MissionCompleted")\\n'
            'AnalyticsService:LogCustomEvent(player, "UnknownEvent")\\n',
        )
        report = v31.audit_project(self.root, self.catalog())
        self.assertEqual(report["catalog_status"], "valid")
        self.assertTrue(any(item["code"] == "event_missing_from_catalog" for item in report["findings"]))

    def test_client_custom_event_call_is_flagged(self):
        self.put(
            "StarterPlayer/StarterPlayerScripts/Tracker.client.lua",
            'local AnalyticsService = game:GetService("AnalyticsService")\\n'
            'AnalyticsService:LogCustomEvent(player, "MissionCompleted")\\n',
        )
        report = v31.audit_project(self.root, self.catalog())
        self.assertTrue(any(item["code"] == "analytics_api_in_client_context" for item in report["findings"]))

    def test_deprecated_analytics_method_is_flagged(self):
        self.put(
            "Server/Old.server.lua",
            'AnalyticsService:FireCustomEvent(player, "OldEvent", {})\\n',
        )
        report = v31.audit_project(self.root)
        self.assertTrue(any(item["code"] == "deprecated_analytics_api" for item in report["findings"]))

    def test_journey_event_is_included_in_current_api_inventory(self):
        self.put(
            "ServerScriptService/Analytics.server.lua",
            'AnalyticsService:LogJourneyEvent(player, "Onboarding", "Started", "session")\\n',
        )
        report = v31.audit_project(self.root)
        self.assertEqual(report["inventory"]["analytics_method_calls"]["LogJourneyEvent"], 1)

    def test_dynamic_custom_event_name_needs_review(self):
        self.put(
            "Server/Tracker.server.lua",
            'AnalyticsService:LogCustomEvent(player, eventName)\\n',
        )
        report = v31.audit_project(self.root)
        self.assertTrue(any(item["code"] == "dynamic_event_name_requires_review" for item in report["findings"]))

    def test_possible_personal_field_near_custom_call_is_flagged_without_copying_value(self):
        self.put(
            "Server/Tracker.server.lua",
            'AnalyticsService:LogCustomEvent(player, "MissionCompleted", 1, {account = player.UserId})\\n',
        )
        report = v31.audit_project(self.root)
        encoded = json.dumps(report)
        self.assertIn("possible_personal_data_in_event_arguments", encoded)
        self.assertNotIn("123456789", encoded)

    def test_invalid_catalog_is_reported_not_used_as_an_approval_list(self):
        self.put(
            "Server/Tracker.server.lua",
            'AnalyticsService:LogCustomEvent(player, "UnknownEvent")\\n',
        )
        catalog = self.catalog()
        catalog["events"][0]["privacy_reviewed"] = False
        report = v31.audit_project(self.root, catalog)
        self.assertEqual(report["catalog_status"], "invalid")
        self.assertTrue(report["catalog_errors"])
        self.assertFalse(any(item["code"] == "event_missing_from_catalog" for item in report["findings"]))

    def test_symlinked_source_is_skipped(self):
        real = self.put("Server/real.lua", "return true\\n")
        link = self.root / "Server" / "linked.lua"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable.")
        warnings = []
        found = v31.iter_luau_files(self.root, 100, warnings)
        self.assertNotIn(link, found)
        self.assertTrue(any("symlink" in item for item in warnings))

    def test_scan_limit_is_applied(self):
        self.put("a.lua", "return true\\n")
        self.put("b.lua", "return true\\n")
        report = v31.audit_project(self.root, max_files=1)
        self.assertEqual(report["inventory"]["luau_files_discovered"], 1)
        self.assertTrue(any("file scan limit" in item for item in report["warnings"]))


class HealthPolicyTests(Fixture):
    def test_policy_and_healthy_aggregate_snapshot_pass(self):
        policy = self.policy()
        self.assertEqual(v31.validate_health_policy(policy), [])
        report = v31.evaluate_health(policy, self.snapshot())
        self.assertEqual(report["status"], "clear")
        self.assertEqual(report["alert_count"], 0)
        self.assertEqual(report["warning_count"], 0)

    def test_warning_thresholds_are_reported_without_making_up_scores(self):
        snapshot = self.snapshot(server_error_rate_pct=1.5, onboarding_completion_pct=32)
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "warning")
        self.assertEqual(report["warning_count"], 2)
        self.assertTrue(all(item["value"] in {1.5, 32.0} for item in report["metrics"]))

    def test_hard_threshold_breach_is_alert(self):
        snapshot = self.snapshot(server_error_rate_pct=2.5, onboarding_completion_pct=40)
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "alert")
        self.assertEqual(report["alert_count"], 1)

    def test_stale_snapshot_is_held(self):
        snapshot = self.snapshot()
        snapshot["captured_at"] = (datetime.now(timezone.utc) - timedelta(hours=60)).isoformat()
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("older than" in item for item in report["hold_reasons"]))
        self.assertEqual(report["metrics"], [])

    def test_future_dated_snapshot_is_held(self):
        snapshot = self.snapshot()
        snapshot["captured_at"] = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("future" in item.lower() for item in report["hold_reasons"]))

    def test_small_sample_is_held(self):
        snapshot = self.snapshot()
        snapshot["sample_size"] = 20
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("below the policy minimum" in item for item in report["hold_reasons"]))

    def test_missing_metric_is_held_not_filled_with_zero(self):
        snapshot = self.snapshot()
        del snapshot["metrics"]["onboarding_completion_pct"]
        report = v31.evaluate_health(self.policy(), snapshot)
        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("missing policy metrics" in item for item in report["hold_reasons"]))

    def test_unknown_metric_is_rejected(self):
        snapshot = self.snapshot()
        snapshot["metrics"]["player_lifetime_value"] = 123
        with self.assertRaisesRegex(ValueError, "not defined in policy"):
            v31.evaluate_health(self.policy(), snapshot)

    def test_bad_min_max_warning_order_is_rejected(self):
        policy = self.policy()
        policy["metrics"]["server_error_rate_pct"]["warning_threshold"] = 3
        self.assertTrue(any("warning_threshold must be less than" in item for item in v31.validate_health_policy(policy)))

    def test_boolean_and_nonfinite_metric_values_are_rejected(self):
        snapshot = self.snapshot()
        snapshot["metrics"]["server_error_rate_pct"] = True
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            v31.evaluate_health(self.policy(), snapshot)


class PathAndPackageTests(Fixture):
    def test_path_escape_and_symlink_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "inside the selected project root"):
            v31.safe_project_path(self.root, "../outside.json")
        outside = Path(tempfile.mkdtemp())
        try:
            link = self.root / "outside-link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks are unavailable.")
            with self.assertRaisesRegex(ValueError, "symlink"):
                v31.safe_project_path(self.root, "outside-link/file.json")
        finally:
            outside.rmdir()

    def test_atomic_json_output(self):
        output = v31.safe_output_path(self.root, ".codex/reports/health.json")
        v31.atomic_write_json(output, {"status": "clear"})
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"status": "clear"})

    def test_patch_is_idempotent_and_cumulative_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills = package / ".agents" / "skills"
            for index in range(224):
                path = skills / f"legacy-{index:03}" / "SKILL.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    f"---\\nname: legacy-{index:03}\\ndescription: Legacy skill {index}.\\n---\\n",
                    encoding="utf-8",
                )
            (package / "AGENTS.md").write_text("# Agent rules\\nNo gambling.\\n", encoding="utf-8")
            for relative in audit_cumulative_package.REQUIRED_FILES:
                if relative.startswith(".agents/skills/") or relative.startswith("v31/"):
                    continue
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("{}\\n" if relative.endswith(".json") else "# Fixture\\n", encoding="utf-8")
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertEqual(audit_cumulative_package.audit(package), [])


if __name__ == "__main__":
    unittest.main()
