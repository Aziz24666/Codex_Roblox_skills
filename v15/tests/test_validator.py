import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "v15_validate.py"

class V15ValidatorTests(unittest.TestCase):
    def test_repository_examples_validate(self):
        result = subprocess.run([sys.executable, str(VALIDATOR), "--root", str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pass_without_evidence_is_rejected(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location("v15_validate", VALIDATOR)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        evidence = {
            "schema_version": 1, "run_id": "r1", "environment": "studio",
            "scenario_id": "s1", "status": "PASS", "started_at": "2026-11-17T00:00:00Z",
            "client_count": 1, "artifacts": [], "logs": []
        }
        with self.assertRaises(ValueError):
            module.validate_evidence(evidence, "test-evidence.json")

    def test_unknown_environment_is_rejected(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location("v15_validate", VALIDATOR)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        evidence = {
            "schema_version": 1, "run_id": "r1", "environment": "imaginary",
            "scenario_id": "s1", "status": "NOT_RUN", "started_at": "2026-11-17T00:00:00Z"
        }
        with self.assertRaises(ValueError):
            module.validate_evidence(evidence, "test-evidence.json")

if __name__ == "__main__":
    unittest.main()
