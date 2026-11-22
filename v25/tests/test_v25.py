from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import v25  # noqa: E402
import patch_cumulative_package  # noqa: E402
import audit_cumulative_package  # noqa: E402

class SessionContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = v25.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def start(self):
        code, out, err = self.run_cli(
            "start", "--root", str(self.root), "--goal", "Build a stable Roblox game",
            "--stage", "Baseline and project audit"
        )
        self.assertEqual(code, 0, err)
        return out

    def test_start_checkpoint_and_resume_handoff(self):
        self.start()
        code, out, err = self.run_cli(
            "checkpoint", "--root", str(self.root),
            "--completed", "Inspected project structure",
            "--next", "Add server-side validation tests",
            "--decision", "Keep currency mutations server-authoritative",
            "--test", "python -m unittest: PASS",
            "--file", "src/Server/EconomyService.luau",
            "--branch", "feature/gameplay"
        )
        self.assertEqual(code, 0, err)
        self.assertIn("Checkpoint 2 saved", out)
        code, _, err = self.run_cli(
            "handoff", "--root", str(self.root), "--stage", "Server-side validation",
            "--next", "Write receipt validation tests", "--note", "Safe stopping point"
        )
        self.assertEqual(code, 0, err)
        prompt = self.root / ".codex" / "session" / "RESUME_PROMPT.md"
        self.assertTrue(prompt.is_file())
        prompt_text = prompt.read_text(encoding="utf-8")
        self.assertIn("Build a stable Roblox game", prompt_text)
        self.assertIn("Inspected project structure", prompt_text)
        self.assertIn("Write receipt validation tests", prompt_text)
        self.assertIn("Keep currency mutations server-authoritative", prompt_text)
        code, out, err = self.run_cli("verify", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertIn("PASS: V25 checkpoint integrity verified", out)

    def test_resume_recovers_previous_valid_backup(self):
        self.start()
        self.run_cli("checkpoint", "--root", str(self.root), "--completed", "First safe stage")
        self.run_cli("checkpoint", "--root", str(self.root), "--next", "Second safe stage")
        state_file = self.root / ".codex" / "session" / "checkpoint.json"
        state_file.write_text("{incomplete", encoding="utf-8")
        code, out, err = self.run_cli("resume", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertIn("First safe stage", out)
        self.assertIn("recovered from checkpoint.json.bak", err)
        self.assertEqual(v25.parse_state_file(state_file)[0]["checkpoint_count"], 2)

    def test_event_journal_repairs_only_an_incomplete_tail(self):
        self.start()
        event_file = self.root / ".codex" / "session" / "events.jsonl"
        with event_file.open("ab") as stream:
            stream.write(b'{"sequence":')
        code, out, err = self.run_cli("checkpoint", "--root", str(self.root), "--completed", "Journal tail test")
        self.assertEqual(code, 0, err)
        events, tail, _ = v25.read_events(event_file)
        self.assertFalse(tail)
        self.assertEqual(len(events), 2)
        self.assertIn("Checkpoint 2 saved", out)

    def test_secret_like_values_are_rejected(self):
        code, _, err = self.run_cli("start", "--root", str(self.root),
                                    "--goal", "Use token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456")
        self.assertEqual(code, 1)
        self.assertIn("Do not put secrets", err)
        self.assertFalse((self.root / ".codex" / "session" / "checkpoint.json").exists())

    def test_start_does_not_overwrite_existing_session(self):
        self.start()
        code, _, err = self.run_cli("start", "--root", str(self.root), "--goal", "A different goal")
        self.assertEqual(code, 1)
        self.assertIn("A session already exists", err)

    def test_complete_status_and_blocker_clearing(self):
        self.start()
        self.run_cli("checkpoint", "--root", str(self.root), "--blocker", "Waiting for test asset")
        code, _, err = self.run_cli("checkpoint", "--root", str(self.root), "--status", "completed",
                                    "--clear-blockers", "--next", "Archive final report")
        self.assertEqual(code, 0, err)
        state, error = v25.parse_state_file(self.root / ".codex" / "session" / "checkpoint.json")
        self.assertIsNone(error)
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["blockers"], [])
        self.assertEqual(state["next_actions"], ["Archive final report"])

class PackagePatchTests(unittest.TestCase):
    def test_patch_is_idempotent_and_audit_passes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            (package / ".agents" / "skills").mkdir(parents=True)
            for index in range(205):
                skill = package / ".agents" / "skills" / f"legacy-{index:03}" / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text(f"# Legacy skill {index}\n", encoding="utf-8")
            (package / "AGENTS.md").write_text("# Agent rules\n\nInherited V18 no-gambling rules remain active.\n", encoding="utf-8")
            patch_cumulative_package.patch(package, source)
            patch_cumulative_package.patch(package, source)
            agents = (package / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count(patch_cumulative_package.MARKER), 1)
            self.assertIn("Inherited V18 no-gambling rules remain active.", agents)
            self.assertEqual(audit_cumulative_package.audit(package), [])

if __name__ == "__main__":
    unittest.main()
