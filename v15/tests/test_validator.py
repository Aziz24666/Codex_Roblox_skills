import importlib.util
import tempfile
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
        skill_files = list((ROOT / "codex-skills").glob("*/SKILL.md"))
        self.assertEqual(len(skill_files), 8)
        for path in skill_files:
            self.assertIn("Mandatory current-source research gate", path.read_text(encoding="utf-8"))

    def test_package_patcher_removes_generated_python_caches(self):
        patcher_path = ROOT / "tools" / "patch_cumulative_package.py"
        patcher_spec = importlib.util.spec_from_file_location("v15_package_patcher", patcher_path)
        patcher = importlib.util.module_from_spec(patcher_spec)
        sys.modules[patcher_spec.name] = patcher
        patcher_spec.loader.exec_module(patcher)
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            cache = package / "v15" / "tools" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "stale.cpython-313.pyc").write_bytes(b"generated")
            (package / "v15" / "tests").mkdir(parents=True)
            (package / "v15" / "tests" / "leftover.pyc").write_bytes(b"generated")
            removed = patcher.clean_generated_python_artifacts(package)
            self.assertEqual(removed, 3)
            self.assertFalse(cache.exists())
            self.assertFalse((package / "v15" / "tests" / "leftover.pyc").exists())


if __name__ == "__main__":
    unittest.main()
