#!/usr/bin/env python3
"""V25 session checkpoint, handoff, and recovery CLI (Python standard library only)."""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, tempfile, time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

VERSION = "25.0.0"
SCHEMA_VERSION = 1
SESSION_RELATIVE = Path(".codex") / "session"
SECRET_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(password|passwd|api[_-]?key|access[_-]?token)\s*[:=]\s*\S+"),
)

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def state_digest(state: dict[str, Any]) -> str:
    body = {key: value for key, value in state.items() if key != "_integrity"}
    return hashlib.sha256(canonical_json(body)).hexdigest()

def seal_state(state: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(state)
    sealed.pop("_integrity", None)
    sealed["_integrity"] = state_digest(sealed)
    return sealed

def validate_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise ValueError("Checkpoint must be a JSON object.")
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported checkpoint schema: {state.get('schema_version')!r}.")
    expected = state.get("_integrity")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Checkpoint is missing a valid integrity digest.")
    if state_digest(state) != expected:
        raise ValueError("Checkpoint integrity check failed; file may be incomplete or modified.")
    required = ("goal", "project_root", "project_name", "current_stage", "status")
    missing = [key for key in required if not isinstance(state.get(key), str)]
    if missing:
        raise ValueError("Checkpoint is missing required string fields: " + ", ".join(missing))
    for key in ("completed", "next_actions", "decisions", "blockers", "tests", "changed_files"):
        if not isinstance(state.get(key), list) or not all(isinstance(item, str) for item in state[key]):
            raise ValueError(f"Checkpoint field {key!r} must be a list of strings.")
    return state

def safe_text(value: str, field: str) -> str:
    value = value.strip()
    if len(value) > 2000:
        raise ValueError(f"{field} is too long (maximum 2,000 characters).")
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            raise ValueError(f"{field} looks like it may contain a credential. Do not put secrets in checkpoints.")
    return value

def safe_items(items: Iterable[str] | None, field: str) -> list[str]:
    result: list[str] = []
    for item in items or []:
        clean = safe_text(item, field)
        if clean and clean not in result:
            result.append(clean)
    return result

def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as temporary:
        temp_path = Path(temporary.name)
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
    try:
        os.replace(temp_path, path)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass

def atomic_json(path: Path, value: Any) -> None:
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")

def resolve_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Project root does not exist or is not a directory: {root}")
    return root

def session_paths(root: Path) -> dict[str, Path]:
    session_dir = root / SESSION_RELATIVE
    resolved = session_dir.resolve()
    if os.path.commonpath((str(root), str(resolved))) != str(root):
        raise ValueError("Session directory resolves outside the project root; refusing to write.")
    return {"dir": session_dir, "state": session_dir / "checkpoint.json",
            "backup": session_dir / "checkpoint.json.bak", "events": session_dir / "events.jsonl",
            "resume": session_dir / "RESUME_PROMPT.md", "lock": session_dir / ".write.lock",
            "gitignore": session_dir / ".gitignore"}

@contextmanager
def session_lock(lock_path: Path, timeout: float = 10.0):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, f"pid={os.getpid()} time={now_iso()}\n".encode("utf-8"))
        except FileExistsError:
            try:
                if time.time() - lock_path.stat().st_mtime > 180:
                    lock_path.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise RuntimeError("Another checkpoint operation holds the session lock. Retry shortly.")
            time.sleep(0.1)
    try:
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        lock_path.unlink(missing_ok=True)

def ensure_session_dir(paths: dict[str, Path]) -> None:
    paths["dir"].mkdir(parents=True, exist_ok=True)
    if not paths["gitignore"].exists():
        atomic_write(paths["gitignore"], b"*\n!.gitignore\n")

def parse_state_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"Checkpoint not found: {path}"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        return validate_state(state), None
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return None, str(exc)

def load_state(paths: dict[str, Path], allow_backup: bool = False) -> tuple[dict[str, Any], bool]:
    state, error = parse_state_file(paths["state"])
    if state is not None:
        return state, False
    if allow_backup:
        backup, backup_error = parse_state_file(paths["backup"])
        if backup is not None:
            return backup, True
        raise ValueError(f"Primary checkpoint is invalid ({error}); backup is unavailable ({backup_error}).")
    raise ValueError(error or "Unable to read checkpoint.")

def save_state(paths: dict[str, Path], state: dict[str, Any]) -> dict[str, Any]:
    current, _ = parse_state_file(paths["state"])
    if current is not None:
        atomic_write(paths["backup"], paths["state"].read_bytes())
    sealed = seal_state(state)
    atomic_json(paths["state"], sealed)
    return sealed

def read_events(path: Path, repair_tail: bool = False) -> tuple[list[dict[str, Any]], bool, str]:
    if not path.exists():
        return [], False, "0" * 64
    raw = path.read_bytes()
    boundary = raw.rfind(b"\n") + 1
    tail_incomplete = boundary != len(raw)
    complete = raw[:boundary]
    events: list[dict[str, Any]] = []
    previous = "0" * 64
    for line_number, raw_line in enumerate(complete.splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Event journal is corrupt at complete line {line_number}: {exc}") from exc
        expected = event.get("hash")
        body = {key: value for key, value in event.items() if key != "hash"}
        if event.get("previous_hash") != previous:
            raise ValueError(f"Event journal chain mismatch at line {line_number}.")
        actual = hashlib.sha256(canonical_json(body)).hexdigest()
        if expected != actual:
            raise ValueError(f"Event journal digest mismatch at line {line_number}.")
        previous = expected
        events.append(event)
    if tail_incomplete and repair_tail:
        atomic_write(path, complete)
    return events, tail_incomplete, previous

def append_event(paths: dict[str, Path], state: dict[str, Any], event_type: str, note: str = "") -> None:
    events, _, previous = read_events(paths["events"], repair_tail=True)
    body = {"sequence": len(events) + 1, "timestamp": now_iso(), "type": event_type,
            "stage": state["current_stage"], "status": state["status"],
            "checkpoint_count": state["checkpoint_count"], "state_integrity": state["_integrity"],
            "note": note, "previous_hash": previous}
    record = dict(body)
    record["hash"] = hashlib.sha256(canonical_json(body)).hexdigest()
    encoded = canonical_json(record) + b"\n"
    paths["events"].parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(str(paths["events"]), os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, encoded)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)

def make_initial_state(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    goal = safe_text(args.goal, "goal")
    if not goal:
        raise ValueError("A non-empty --goal is required.")
    stage = safe_text(args.stage, "stage") or "Discovery and baseline"
    return {"schema_version": SCHEMA_VERSION, "toolkit_version": VERSION,
            "project_root": str(root), "project_name": root.name or str(root),
            "created_at": now_iso(), "updated_at": now_iso(), "goal": goal,
            "status": "active", "current_stage": stage, "completed": [],
            "next_actions": ["Inspect the project and define a small, testable first stage."],
            "decisions": [], "blockers": [], "tests": [], "changed_files": [],
            "git_branch": None, "git_commit": None, "checkpoint_count": 0,
            "last_checkpoint_note": "Session started."}

def mutate_state(state: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    updated = dict(state)
    for attr, field in (("completed", "completed"), ("decisions", "decisions"),
                        ("tests", "tests"), ("files", "changed_files")):
        values = safe_items(getattr(args, attr, None), attr)
        if values:
            updated[field] = list(dict.fromkeys(updated.get(field, []) + values))
    next_values = safe_items(getattr(args, "next_actions", None), "next action")
    if getattr(args, "clear_next", False):
        updated["next_actions"] = next_values
    elif next_values:
        updated["next_actions"] = next_values
    blocker_values = safe_items(getattr(args, "blockers", None), "blocker")
    if getattr(args, "clear_blockers", False):
        updated["blockers"] = blocker_values
    elif blocker_values:
        updated["blockers"] = list(dict.fromkeys(updated.get("blockers", []) + blocker_values))
    for attr, field in (("stage", "current_stage"), ("goal", "goal"), ("status", "status"),
                        ("branch", "git_branch"), ("commit", "git_commit")):
        value = getattr(args, attr, None)
        if value is not None:
            updated[field] = safe_text(value, attr) if isinstance(value, str) else value
    updated["last_checkpoint_note"] = safe_text(getattr(args, "note", "") or "", "note")
    updated["checkpoint_count"] = int(updated.get("checkpoint_count", 0)) + 1
    updated["updated_at"] = now_iso()
    return updated

def render_resume_prompt(state: dict[str, Any]) -> str:
    def section(title: str, values: list[str]) -> str:
        return "\n".join([f"## {title}"] + ([f"- {item}" for item in values] if values else ["None recorded."]))
    return "\n".join([
        "# Codex session handoff", "",
        "You are resuming an existing Roblox development task after a conversation or tool interruption.",
        "Treat this checkpoint as a concise progress record, not as proof that unverified work exists.", "",
        f"- Project: {state['project_name']}", f"- Project root: {state['project_root']}",
        f"- Goal: {state['goal']}", f"- Status: {state['status']}",
        f"- Current stage: {state['current_stage']}", f"- Checkpoints saved: {state['checkpoint_count']}",
        f"- Last updated (UTC): {state['updated_at']}",
        f"- Git branch: {state.get('git_branch') or 'Not recorded'}",
        f"- Git commit: {state.get('git_commit') or 'Not recorded'}", "",
        section("Completed and verified", state["completed"]), "",
        section("Next actions", state["next_actions"]), "",
        section("Decisions to preserve", state["decisions"]), "",
        section("Open blockers", state["blockers"]), "",
        section("Tests and validation", state["tests"]), "",
        section("Changed files", state["changed_files"]), "",
        "## Resume procedure",
        "1. Inspect the current repository, branch, working tree, and checkpoint files before editing.",
        "2. Verify completed items against actual files, commits, and test results; do not redo verified work unnecessarily.",
        "3. Continue with the first unfinished next action. Keep each implementation stage small and independently testable.",
        "4. Run relevant tests after each stage, then save another checkpoint.",
        "5. Do not claim a task, test, build, push, or release succeeded unless current evidence confirms it.",
        "6. Never store or request passwords, API keys, access tokens, private user data, or raw conversation transcripts in checkpoints.",
        "7. Preserve all existing Roblox platform-compliance, fair-monetization, and no-gambling rules in the toolkit.", "",
        "## First action",
        "Report the verified repository state in one or two sentences, then continue the next action without asking the user to repeat recorded information.", ""
    ])

def write_resume(paths: dict[str, Path], state: dict[str, Any]) -> str:
    atomic_write(paths["resume"], render_resume_prompt(state).encode("utf-8"))
    return str(paths["resume"])

def add_mutation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stage", help="Current small, testable stage.")
    parser.add_argument("--status", choices=("active", "paused", "blocked", "completed"))
    parser.add_argument("--completed", action="append", help="Verified completed item; repeatable.")
    parser.add_argument("--next", dest="next_actions", action="append", help="Next action; repeatable and replaces the next-action list.")
    parser.add_argument("--clear-next", action="store_true", help="Clear next actions before applying any --next values.")
    parser.add_argument("--decision", dest="decisions", action="append", help="Decision to preserve; repeatable.")
    parser.add_argument("--blocker", dest="blockers", action="append", help="Open blocker; repeatable.")
    parser.add_argument("--clear-blockers", action="store_true", help="Clear blockers before applying any --blocker values.")
    parser.add_argument("--test", dest="tests", action="append", help="Test or validation result; repeatable.")
    parser.add_argument("--file", dest="files", action="append", help="Changed project file; repeatable.")
    parser.add_argument("--branch", help="Current Git branch, if known.")
    parser.add_argument("--commit", help="Current Git commit SHA, if known.")
    parser.add_argument("--note", default="", help="Short checkpoint note; do not include secrets.")

def command_start(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    ensure_session_dir(paths)
    with session_lock(paths["lock"]):
        if paths["state"].exists() or paths["backup"].exists():
            raise ValueError("A session already exists. Use checkpoint/resume, not start, to continue it.")
        state = make_initial_state(root, args)
        state["checkpoint_count"] = 1
        state["updated_at"] = now_iso()
        sealed = save_state(paths, state)
        append_event(paths, sealed, "start", "Session initialized.")
        prompt = write_resume(paths, sealed)
    print(f"Session started for {root}")
    print(f"Checkpoint: {paths['state']}")
    print(f"Resume prompt: {prompt}")
    return 0

def command_checkpoint(args: argparse.Namespace, handoff: bool = False) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    ensure_session_dir(paths)
    with session_lock(paths["lock"]):
        state, recovered = load_state(paths, allow_backup=True)
        if recovered:
            print("WARNING: restored the previous valid backup because the primary checkpoint was invalid.", file=sys.stderr)
            atomic_json(paths["state"], seal_state(state))
        updated = mutate_state(state, args)
        sealed = save_state(paths, updated)
        append_event(paths, sealed, "handoff" if handoff else "checkpoint", args.note)
        prompt = write_resume(paths, sealed) if handoff else None
    print(f"Checkpoint {sealed['checkpoint_count']} saved.")
    if prompt:
        print(f"Resume prompt ready: {prompt}")
    if sealed["blockers"]:
        print(f"Open blockers: {len(sealed['blockers'])}")
    return 0

def command_resume(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    state, recovered = load_state(paths, allow_backup=True)
    if recovered:
        atomic_json(paths["state"], seal_state(state))
        print("WARNING: recovered from checkpoint.json.bak; the primary checkpoint was unreadable.", file=sys.stderr)
    prompt = write_resume(paths, state)
    print(paths["resume"].read_text(encoding="utf-8"), end="")
    print(f"\nSaved handoff file: {prompt}", file=sys.stderr)
    return 0

def command_recover(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    if not paths["backup"].exists():
        raise ValueError("No previous checkpoint backup exists.")
    backup, error = parse_state_file(paths["backup"])
    if backup is None:
        raise ValueError(f"Backup checkpoint is invalid: {error}")
    atomic_json(paths["state"], seal_state(backup))
    print(f"Restored checkpoint {backup['checkpoint_count']} from {paths['backup']}")
    return 0

def command_status(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    state, recovered = load_state(paths, allow_backup=True)
    for label, value in (("Project", state["project_name"]), ("Goal", state["goal"]),
                         ("Status", state["status"]), ("Stage", state["current_stage"]),
                         ("Checkpoint count", state["checkpoint_count"]),
                         ("Completed items", len(state["completed"])), ("Next actions", len(state["next_actions"])),
                         ("Open blockers", len(state["blockers"])), ("Updated", state["updated_at"])):
        print(f"{label}: {value}")
    if recovered:
        print("WARNING: primary checkpoint is invalid; showing the last valid backup.")
    return 0

def command_verify(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    paths = session_paths(root)
    state, error = parse_state_file(paths["state"])
    if state is None:
        print(f"FAIL: {error}", file=sys.stderr)
        backup, backup_error = parse_state_file(paths["backup"])
        if backup is not None:
            print(f"RECOVERY AVAILABLE: checkpoint.json.bak (checkpoint {backup['checkpoint_count']}).", file=sys.stderr)
        elif backup_error:
            print(f"Backup: {backup_error}", file=sys.stderr)
        return 1
    if Path(state["project_root"]).resolve() != root:
        print("FAIL: checkpoint project_root does not match the selected project.", file=sys.stderr)
        return 1
    try:
        events, tail_incomplete, _ = read_events(paths["events"])
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if tail_incomplete:
        print("WARNING: event journal has an incomplete final line; the next checkpoint will repair it.")
    backup, backup_error = parse_state_file(paths["backup"])
    if paths["backup"].exists() and backup is None:
        print(f"WARNING: backup checkpoint is invalid: {backup_error}")
    print(f"PASS: V25 checkpoint integrity verified; checkpoint={state['checkpoint_count']}; journal_events={len(events)}; project={state['project_name']}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="V25: durable session checkpoints and recoverable Codex handoffs for Roblox projects.")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start", help="Create a new durable project session.")
    start.add_argument("--root", default=".", help="Roblox project root (default: current directory).")
    start.add_argument("--goal", required=True, help="The project's durable goal.")
    start.add_argument("--stage", default="Discovery and baseline", help="Initial small, testable stage.")
    start.set_defaults(func=command_start)
    for name, help_text in (("checkpoint", "Save progress after a stage, decision, or meaningful change."),
                            ("handoff", "Save progress and generate a ready-to-paste resume prompt.")):
        item = sub.add_parser(name, help=help_text)
        item.add_argument("--root", default=".", help="Roblox project root.")
        add_mutation_arguments(item)
        item.set_defaults(func=(lambda a, h=(name == "handoff"): command_checkpoint(a, h)))
    for name, help_text, func in (
        ("resume", "Print the latest verified handoff prompt.", command_resume),
        ("recover", "Restore the previous valid checkpoint backup.", command_recover),
        ("status", "Show the current saved project state.", command_status),
        ("verify", "Verify checkpoint integrity and event-journal continuity.", command_verify),
    ):
        item = sub.add_parser(name, help=help_text)
        item.add_argument("--root", default=".", help="Roblox project root.")
        item.set_defaults(func=func)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
