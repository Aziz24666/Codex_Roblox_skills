import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "v15_validate.py"
SPEC = importlib.util.spec_from_file_location("v15_validate", VALIDATOR)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class V15ValidatorTests(unittest.TestCase):
    def test_repository_examples_and_native_skills_validate(self):
        result = subprocess.run([sys.executable, str(VALIDATOR), "--root", str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS native Codex skills", result.stdout)

    def test_pass_without_evidence_is_rejected(self):
        evidence = {
            "schema_version": 1, "run_id": "r1", "environment": "studio",
            "scenario_id": "s1", "status": "PASS", "started_at": "2026-11-17T00:00:00Z",
            "client_count": 1, "artifacts": [], "logs": [],
        }
        with self.assertRaises(ValueError):
            MODULE.validate_evidence(evidence, "test-evidence.json")

    def test_unknown_environment_is_rejected(self):
        evidence = {
            "schema_version": 1, "run_id": "r1", "environment": "imaginary",
            "scenario_id": "s1", "status": "NOT_RUN", "started_at": "2026-11-17T00:00:00Z",
        }
        with self.assertRaises(ValueError):
            MODULE.validate_evidence(evidence, "test-evidence.json")

    def test_malformed_manifest_type_is_rejected_cleanly(self):
        with self.assertRaises(ValueError):
            MODULE.validate_manifest([], "bad-manifest.json")

    def test_pass_task_cannot_contain_not_run_criteria(self):
        evaluation = {
            "schema_version": 1, "task_id": "sample",
            "selected_skills": ["roblox-project-intelligence"],
            "criteria": [{"id": "c1", "description": "Verified", "status": "NOT_RUN"}],
            "result": "PASS",
        }
        with self.assertRaises(ValueError):
            MODULE.validate_task_evaluation(evaluation, "bad-evaluation.json")

    def test_native_skills_are_codex_entrypoints(self):
        MODULE.validate_skills(ROOT)
        self.assertEqual(len(list((ROOT / "codex-skills").glob("*/SKILL.md"))), 8)


if __name__ == "__main__":
    unittest.main()
