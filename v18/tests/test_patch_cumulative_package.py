import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

V18_ROOT=Path(__file__).resolve().parents[1]
PATCHER_PATH=V18_ROOT/'tools'/'patch_cumulative_package.py'
SPEC=importlib.util.spec_from_file_location('v18_package_patcher',PATCHER_PATH)
PATCHER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCHER)

OLD_MANIFESTS='''CURRENT_MANIFESTS = {
    "SHA256SUMS.txt": {"SHA256SUMS.txt", "V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V17_SHA256SUMS.txt": {"V14_SHA256SUMS.txt", "V17_SHA256SUMS.txt"},
    "V14_SHA256SUMS.txt": {"V14_SHA256SUMS.txt"},
}'''

class CumulativePatchTests(unittest.TestCase):
    def _v17_audit_fixture(self):
        return '''EXPECTED_INSTALLED_SKILLS = 163
'''+OLD_MANIFESTS+'''

def run_audit():
    source_files = []
    for path in source_files:
        installed = installed_root / path.parent.name / "SKILL.md"
        if not installed.is_file() or installed.read_bytes() != path.read_bytes():
            errors.append(f"V17 source/installed skill mismatch: {path.parent.name}")
'''

    def test_v17_audit_migration_updates_count_manifests_and_only_exempts_upgrades(self):
        with tempfile.TemporaryDirectory() as temp:
            audit=Path(temp)/'audit_cumulative_package.py'
            audit.write_text(self._v17_audit_fixture(),encoding='utf-8')
            PATCHER.migrate_v17_audit(audit)
            migrated=audit.read_text(encoding='utf-8')
            self.assertIn('EXPECTED_INSTALLED_SKILLS = 175',migrated)
            self.assertIn('V18_SHA256SUMS.txt',migrated)
            self.assertNotIn('"V17_SHA256SUMS.txt"',migrated)
            self.assertIn('if path.parent.name in V18_UPGRADED_SKILLS:',migrated)
            self.assertIn('continue',migrated)
            for name in PATCHER.UPGRADE_EXISTING_SKILLS:
                self.assertIn(f'"{name}"',migrated)

    def test_v17_audit_migration_fails_closed_when_baseline_count_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            audit=Path(temp)/'audit_cumulative_package.py'
            audit.write_text(self._v17_audit_fixture().replace('= 163','= 164',1),encoding='utf-8')
            before=audit.read_text(encoding='utf-8')
            with self.assertRaises(ValueError):
                PATCHER.migrate_v17_audit(audit)
            self.assertEqual(audit.read_text(encoding='utf-8'),before)

    def test_incomplete_remote_validation_example_is_marked_once(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            sample=root/'examples'/'luau-patterns'/'RemoteRequestValidation.server.luau'
            sample.parent.mkdir(parents=True)
            sample.write_text('-- existing teaching sample\n',encoding='utf-8')
            PATCHER.mark_remote_validation_example(root)
            PATCHER.mark_remote_validation_example(root)
            content=sample.read_text(encoding='utf-8')
            self.assertEqual(content.count('-- V18 SAFETY NOTE: TEACHING EXAMPLE ONLY'),1)
            for term in ('world-state','ownership','distance','cooldown','duplicate-request'):
                self.assertIn(term,content)

    def test_doctor_runs_without_third_party_site_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            command=[sys.executable,'-S',str(V18_ROOT/'tools'/'v18.py'),'doctor','--root',temp,'--json']
            result=subprocess.run(command,capture_output=True,text=True,check=False)
            self.assertEqual(result.returncode,0,msg=result.stderr)
            self.assertIn('"source_of_truth"',result.stdout)

if __name__=='__main__':
    unittest.main()
