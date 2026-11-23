from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v30  # noqa: E402
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

    def staging_plan(self):
        plan = v30.make_plan("1.2.3", "staging", "a" * 40, "Ship the candidate to staging.")
        for gate in plan["gates"]:
            if gate["id"] in v30.STAGING_GATES:
                evidence = self.put(f"evidence/{gate['id']}.txt", f"Verified {gate['id']} evidence.\n")
                gate["status"] = "passed"
                gate["evidence"] = evidence.relative_to(self.root).as_posix()
        return plan


class PlanValidationTests(Fixture):
    def test_new_plan_is_review_only_and_starts_with_unrun_gates(self):
        plan = v30.make_plan("1.2.3", "staging", "a" * 40, "Test release.")
        self.assertEqual(plan["controls"]["publishing_mode"], "manual")
        self.assertIs(plan["controls"]["human_approval_required"], True)
        self.assertTrue(all(gate["status"] == "not_run" for gate in plan["gates"]))
        self.assertTrue(any("does not publish" in item for item in plan["limitations"]))
        self.assertTrue(any("Required release gate" in item for item in v30.validate_plan(plan, self.root)))

    def test_complete_staging_plan_passes_only_with_evidence_files(self):
        plan = self.staging_plan()
        self.assertEqual(v30.validate_plan(plan, self.root), [])

    def test_production_needs_all_gates_staged_rollout_rollback_backup_and_approvals(self):
        plan = v30.make_plan("2.0.0", "production", "b" * 40, "Ship production release.")
        for gate in plan["gates"]:
            if gate["id"] in v30.PRODUCTION_GATES:
                evidence = self.put(f"prod/{gate['id']}.txt", "Reviewed evidence.\n")
                gate["status"] = "passed"
                gate["evidence"] = evidence.relative_to(self.root).as_posix()
        rollback = self.put("release/rollback.md", "Rollback to the previous known-good version.\n")
        backup = self.put("release/backup.txt", "Backup job reference: staging-only drill.\n")
        plan["controls"]["rollback_plan"] = rollback.relative_to(self.root).as_posix()
        plan["controls"]["backup_reference"] = backup.relative_to(self.root).as_posix()
        for role in v30.APPROVAL_ROLES:
            evidence = self.put(f"approvals/{role}.txt", "Approval record for a test fixture.\n")
            plan["approvals"].append({
                "role": role, "name": f"Reviewer {role}", "approved": True,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "evidence": evidence.relative_to(self.root).as_posix(),
            })
        self.assertEqual(v30.validate_plan(plan, self.root), [])

    def test_migration_requires_validation_gate_and_data_owner(self):
        plan = self.make_production_plan()
        plan["controls"]["data_store_migration"] = True
        errors = v30.validate_plan(plan, self.root)
        self.assertTrue(any("migration_validation" in item for item in errors))
        self.assertTrue(any("data_owner" in item for item in errors))

    def make_production_plan(self):
        plan = v30.make_plan("2.0.0", "production", "c" * 40, "Production fixture.")
        for gate in plan["gates"]:
            if gate["id"] in v30.PRODUCTION_GATES:
                evidence = self.put(f"production/{gate['id']}.txt", "Evidence.\n")
                gate["status"] = "passed"
                gate["evidence"] = evidence.relative_to(self.root).as_posix()
        for file_name, field in (("rollback.md", "rollback_plan"), ("backup.txt", "backup_reference")):
            evidence = self.put(f"production/{file_name}", "Reference.\n")
            plan["controls"][field] = evidence.relative_to(self.root).as_posix()
        for role in v30.APPROVAL_ROLES:
            evidence = self.put(f"production/approval-{role}.txt", "Approval evidence.\n")
            plan["approvals"].append({
                "role": role, "name": role, "approved": True,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "evidence": evidence.relative_to(self.root).as_posix(),
            })
        return plan

    def test_evidence_hash_mismatch_fails(self):
        plan = self.staging_plan()
        gate = next(item for item in plan["gates"] if item["id"] == "functional_tests")
        gate["sha256"] = "0" * 64
        self.assertTrue(any("does not match" in item for item in v30.validate_plan(plan, self.root)))

    def test_evidence_path_traversal_and_absolute_paths_fail(self):
        plan = self.staging_plan()
        gate = next(item for item in plan["gates"] if item["id"] == "functional_tests")
        gate["evidence"] = "../outside.txt"
        errors = v30.validate_plan(plan, self.root)
        self.assertTrue(any("inside the selected project root" in item for item in errors))
        gate["evidence"] = str(self.root / "absolute.txt")
        errors = v30.validate_plan(plan, self.root)
        self.assertTrue(any("portable relative paths" in item for item in errors))

    def test_symlinked_evidence_is_rejected(self):
        plan = self.staging_plan()
        real = self.put("evidence/real.txt", "Evidence.\n")
        link = self.root / "evidence" / "linked.txt"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable.")
        gate = next(item for item in plan["gates"] if item["id"] == "functional_tests")
        gate["evidence"] = "evidence/linked.txt"
        self.assertTrue(any("symlink" in item for item in v30.validate_plan(plan, self.root)))

    def test_invalid_environment_revision_timestamp_and_automatic_publish_fail(self):
        plan = self.staging_plan()
        plan["release"]["environment"] = "live"
        plan["release"]["source_revision"] = "not-a-hash"
        plan["release"]["created_at"] = "yesterday"
        plan["controls"]["publishing_mode"] = "automatic"
        errors = v30.validate_plan(plan, self.root)
        self.assertTrue(any("environment" in item for item in errors))
        self.assertTrue(any("source_revision" in item for item in errors))
        self.assertTrue(any("created_at" in item for item in errors))
        self.assertTrue(any("publishing_mode must be manual" in item for item in errors))

    def test_passed_gate_requires_evidence(self):
        plan = self.staging_plan()
        gate = next(item for item in plan["gates"] if item["id"] == "functional_tests")
        gate["evidence"] = ""
        self.assertTrue(any("without an evidence file" in item for item in v30.validate_plan(plan, self.root)))


class HygieneAuditTests(Fixture):
    def test_credential_finding_does_not_copy_the_secret(self):
        secret = "this-is-a-fake-test-token-123456789"
        self.put("src/Config.lua", f'local OPENAI_API_KEY = "{secret}"\n')
        report = v30.audit_project(self.root)
        encoded = json.dumps(report)
        self.assertIn("named_credential_assignment", encoded)
        self.assertNotIn(secret, encoded)
        self.assertEqual(report["execution_status"], "static_local_audit_only")

    def test_env_example_is_not_flagged_but_local_env_is(self):
        self.put(".env.example", "API_KEY=replace-me\n")
        self.put(".env.local", "API_KEY=do-not-commit\n")
        report = v30.audit_project(self.root)
        findings = report["findings"]
        self.assertTrue(any(item["file"] == ".env.local" for item in findings))
        self.assertFalse(any(item["file"] == ".env.example" for item in findings))

    def test_rojo_directory_mappings_are_checked_without_requiring_a_file(self):
        self.put("src/init.server.lua", "return true\n")
        self.put("default.project.json", json.dumps({
            "name": "Game", "tree": {"$className": "DataModel", "ServerScriptService": {"$path": "src"}}
        }))
        report = v30.audit_project(self.root)
        self.assertFalse(any(item["code"] == "rojo_path_invalid" for item in report["findings"]))

    def test_missing_rojo_path_is_reported(self):
        self.put("default.project.json", json.dumps({
            "name": "Game", "tree": {"$className": "DataModel", "ServerScriptService": {"$path": "missing-src"}}
        }))
        report = v30.audit_project(self.root)
        self.assertTrue(any(item["code"] == "rojo_path_invalid" for item in report["findings"]))

    def test_symlinked_files_are_skipped(self):
        real = self.put("src/real.lua", "return true\n")
        link = self.root / "src" / "linked.lua"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable.")
        warnings = []
        found = v30.iter_project_files(self.root, 100, warnings)
        self.assertNotIn(link, found)
        self.assertTrue(any("symlink" in item for item in warnings))

    def test_scan_limit_is_applied(self):
        self.put("a.lua", "return true\n")
        self.put("b.lua", "return true\n")
        report = v30.audit_project(self.root, max_files=1)
        self.assertEqual(report["inventory"]["files_discovered"], 1)
        self.assertTrue(any("file scan limit" in item for item in report["warnings"]))


class PathAndCommandTests(Fixture):
    def test_atomic_json_write_and_output_containment(self):
        output = v30.safe_output_path(self.root, ".codex/reports/validation.json")
        v30.atomic_write_json(output, {"valid": True})
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"valid": True})
        with self.assertRaisesRegex(ValueError, "inside the selected project root"):
            v30.safe_output_path(self.root, "../escape.json")

    def test_plan_template_has_all_named_gates(self):
        plan = v30.make_plan("1.0.0", "production", "d" * 40, "Example.")
        gate_ids = {item["id"] for item in plan["gates"]}
        self.assertTrue(v30.PRODUCTION_GATES.issubset(gate_ids))
        self.assertIn("migration_validation", gate_ids)


class PackageTests(unittest.TestCase):
    def test_patch_is_idempotent_and_package_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            skills = package / ".agents" / "skills"
            for index in range(220):
                skill = skills / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(
                    f"---\nname: legacy-{index:03}\ndescription: Legacy skill {index}.\n---\n",
                    encoding="utf-8",
                )
            (package / "AGENTS.md").write_text("# Agent rules\nNo gambling.\n", encoding="utf-8")
            for relative in audit_cumulative_package.REQUIRED_FILES:
                if relative.startswith(".agents/skills/") or relative.startswith("v30/"):
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
