#!/usr/bin/env python3
"""V27 Luau architecture inventory, dependency analysis, type-checking, and Rojo validation."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "27.0.0"
DEFAULT_REPORT = ".codex/reports/v27-architecture-report.json"
SKIP_DIRS = {
    ".git", ".codex", ".agents", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "__pycache__", "node_modules", "build", "dist", "target", ".venv", "venv",
}
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_PROJECT_FILES = 64
MAX_ANALYZE_FILES = 10_000
TYPE_MODES = {"strict", "nonstrict", "nocheck"}

# Conservative patterns: only constant script-relative require expressions are resolved.
STATIC_REQUIRE_RE = re.compile(
    r"""require\s*\(\s*(?P<expr>script(?:\s*(?:\.\s*[A-Za-z_]\w*|\[\s*["'][^"']+["']\s*\]|:\s*WaitForChild\s*\(\s*["'][^"']+["']\s*\))*)\s*\)""",
    re.S,
)
CHAIN_SEGMENT_RE = re.compile(
    r"""\s*(?:\.\s*(?P<prop>[A-Za-z_]\w*)|:\s*WaitForChild\s*\(\s*["'](?P<wait>[^"']+)["']\s*\)|\[\s*["'](?P<index>[^"']+)["']\s*\])"""
)
REMOTE_BIND_RE = re.compile(
    r"""\b(?:local\s+)?(?P<var>[A-Za-z_]\w*)\s*=\s*[^=\n;]*?(?:WaitForChild|FindFirstChild)\s*\(\s*["'](?P<name>[^"']+)["']\s*\)"""
)
REMOTE_API_RE = re.compile(
    r"\b(?P<var>[A-Za-z_]\w*)\s*:\s*(?P<api>FireServer|InvokeServer|OnServerEvent|OnServerInvoke|FireClient|FireAllClients|InvokeClient|OnClientEvent)\b"
)
REMOTE_INSTANCE_RE = re.compile(r"""Instance\.new\s*\(\s*["'](RemoteEvent|RemoteFunction)["']\s*\)""")
TYPE_MODE_RE = re.compile(r"^\s*--!\s*(strict|nonstrict|nocheck)\b", re.I)


def resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Project root could not be resolved safely.") from exc
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return root


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def safe_output_path(root: Path, raw: str) -> Path:
    supplied = Path(raw).expanduser()
    candidate = supplied if supplied.is_absolute() else root / supplied
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Report output must be inside the selected project root.") from exc
    if not relative.parts or ".." in relative.parts:
        raise ValueError("Report output must be a safe path inside the selected project root.")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ValueError("Report output cannot traverse a symlinked directory.")
    current.mkdir(parents=True, exist_ok=True)
    parent = current.resolve(strict=True)
    if not parent.is_relative_to(root):
        raise ValueError("Report output resolves outside the selected project root.")
    target = parent / relative.name
    if target.is_symlink():
        raise ValueError("Report output cannot replace a symlink.")
    if target.exists() and not target.is_file():
        raise ValueError("Report output path is not a regular file.")
    return target


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def iter_luau_files(root: Path, max_files: int, warnings: list[str]) -> list[Path]:
    found: list[Path] = []
    total_bytes = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            item = current / dirname
            if dirname in SKIP_DIRS or item.is_symlink():
                continue
            if not path_is_within(item, root):
                warnings.append(f"Skipped directory outside project root: {item.relative_to(root)}")
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in sorted(filenames):
            path = current / filename
            if path.suffix.lower() not in {".lua", ".luau"}:
                continue
            if path.is_symlink() or not path_is_within(path, root):
                warnings.append(f"Skipped symlink/out-of-root source: {path.relative_to(root)}")
                continue
            try:
                size = path.stat().st_size
            except OSError:
                warnings.append(f"Could not stat source file: {path.relative_to(root)}")
                continue
            if size > MAX_FILE_BYTES:
                warnings.append(f"Skipped oversized source file ({size} bytes): {path.relative_to(root)}")
                continue
            if total_bytes + size > MAX_TOTAL_BYTES:
                warnings.append("Stopped scanning at the 256 MiB aggregate source-size safety limit.")
                return found
            found.append(path)
            total_bytes += size
            if len(found) >= max_files:
                warnings.append(f"Stopped scanning at the configured {max_files}-file limit.")
                return found
    return found


def script_instance_path(root: Path, path: Path) -> tuple[str, ...]:
    relative = path.relative_to(root)
    parts = list(relative.parts)
    filename = parts.pop()
    lower = filename.lower()
    if lower.endswith(".luau"):
        stem = filename[:-5]
    elif lower.endswith(".lua"):
        stem = filename[:-4]
    else:
        stem = filename
    for suffix in (".server", ".client", ".module"):
        if stem.lower().endswith(suffix):
            stem = stem[:-len(suffix)]
            break
    if stem.lower() == "init":
        return tuple(parts)
    return tuple(parts + [stem])


def type_mode(source: str) -> str:
    for line in source.splitlines()[:5]:
        match = TYPE_MODE_RE.match(line)
        if match:
            return match.group(1).lower()
    return "default"


def resolve_script_require(
    expression: str,
    source_path: Path,
    root: Path,
    instance_map: dict[tuple[str, ...], list[Path]],
) -> tuple[Path | None, str, str]:
    parts = list(script_instance_path(root, source_path))
    remainder = expression[len("script"):]
    consumed = ""
    while remainder.strip():
        match = CHAIN_SEGMENT_RE.match(remainder)
        if not match:
            return None, "unsupported", consumed
        prop = match.group("prop")
        segment = match.group("wait") or match.group("index")
        if prop == "Parent":
            if not parts:
                return None, "above_root", "/".join(parts)
            parts.pop()
        elif prop is not None:
            parts.append(prop)
        else:
            parts.append(segment)
        consumed += match.group(0)
        remainder = remainder[match.end():]
    key = tuple(parts)
    matches = instance_map.get(key, [])
    if len(matches) == 1:
        return matches[0], "resolved", "/".join(parts)
    if len(matches) > 1:
        return None, "ambiguous", "/".join(parts)
    return None, "missing", "/".join(parts)


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(graph.get(node, set())):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or (len(component) == 1 and component[0] in graph.get(component[0], set())):
                cycles.append(sorted(component))

    all_nodes = set(graph)
    for targets in graph.values():
        all_nodes.update(targets)
    for node in sorted(all_nodes):
        if node not in indices:
            visit(node)
    return sorted(cycles)


def module_candidate(path: Path) -> bool:
    name = path.name.lower()
    if ".server." in name or ".client." in name:
        return False
    return True


def inspect_remotes(sources: dict[Path, str], root: Path) -> dict[str, Any]:
    client_to_server: Counter[str] = Counter()
    server_handlers: Counter[str] = Counter()
    server_to_client: Counter[str] = Counter()
    client_handlers: Counter[str] = Counter()
    api_counts: Counter[str] = Counter()
    variable_bindings = 0
    generated_instances: Counter[str] = Counter()
    unresolved_variables: Counter[str] = Counter()

    for path, source in sources.items():
        bindings = {match.group("var"): match.group("name") for match in REMOTE_BIND_RE.finditer(source)}
        variable_bindings += len(bindings)
        generated_instances.update(match.group(1) for match in REMOTE_INSTANCE_RE.finditer(source))
        for match in REMOTE_API_RE.finditer(source):
            variable = match.group("var")
            api = match.group("api")
            name = bindings.get(variable, variable)
            api_counts[api] += 1
            if variable not in bindings:
                unresolved_variables[variable] += 1
            if api in {"FireServer", "InvokeServer"}:
                client_to_server[name] += 1
            elif api in {"OnServerEvent", "OnServerInvoke"}:
                server_handlers[name] += 1
            elif api in {"FireClient", "FireAllClients", "InvokeClient"}:
                server_to_client[name] += 1
            elif api == "OnClientEvent":
                client_handlers[name] += 1

    unmatched = []
    for name, count in sorted(client_to_server.items()):
        if server_handlers[name] == 0:
            unmatched.append({
                "remote_reference": name,
                "client_to_server_calls": count,
                "warning": "No matching statically named OnServerEvent/OnServerInvoke handler was found.",
            })
    return {
        "static_name_bindings": variable_bindings,
        "Instance_new_counts": dict(sorted(generated_instances.items())),
        "client_to_server_calls": dict(sorted(client_to_server.items())),
        "server_handlers": dict(sorted(server_handlers.items())),
        "server_to_client_calls": dict(sorted(server_to_client.items())),
        "client_handlers": dict(sorted(client_handlers.items())),
        "api_call_counts": dict(sorted(api_counts.items())),
        "potentially_unpaired_client_calls": unmatched,
        "unresolved_remote_variables": dict(sorted(unresolved_variables.items())),
        "limitations": [
            "Remote references are matched only when a local variable is assigned from a constant WaitForChild/FindFirstChild name.",
            "Dynamic registries, aliases, generated names, wrappers, and cross-module data flow can hide valid handlers or calls.",
            "A missing static match is a review candidate, not proof of a runtime vulnerability or broken remote.",
        ],
    }


def discover_rojo_projects(root: Path) -> list[Path]:
    projects: list[Path] = []
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        dirnames[:] = [
            name for name in sorted(dirnames)
            if name not in SKIP_DIRS and not (current / name).is_symlink()
        ]
        for filename in filenames:
            if filename.endswith(".project.json"):
                candidate = current / filename
                if not candidate.is_symlink() and path_is_within(candidate, root):
                    projects.append(candidate)
                    if len(projects) >= MAX_PROJECT_FILES:
                        return projects
    return projects


def validate_rojo_project(project_path: Path, root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "project_file": project_path.relative_to(root).as_posix(),
        "valid": False,
        "mapped_paths": [],
        "errors": [],
        "warnings": [],
    }
    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result["errors"].append(f"Project file is unreadable or invalid JSON: {type(exc).__name__}.")
        return result
    if not isinstance(project, dict):
        result["errors"].append("Project root must be a JSON object.")
        return result
    if not isinstance(project.get("name"), str) or not project["name"].strip():
        result["errors"].append("Project needs a non-empty name string.")
    tree = project.get("tree")
    if not isinstance(tree, dict):
        result["errors"].append("Project needs a tree object.")
        return result

    seen_paths: set[str] = set()

    def walk(node: dict[str, Any], logical_path: str) -> None:
        raw_path = node.get("$path")
        if raw_path is not None:
            if not isinstance(raw_path, str) or not raw_path.strip():
                result["errors"].append(f"$path at {logical_path or '<root>'} must be a non-empty string.")
            else:
                candidate = Path(raw_path)
                if candidate.is_absolute():
                    result["errors"].append(f"Absolute $path is not accepted at {logical_path or '<root>'}.")
                else:
                    resolved = (project_path.parent / candidate)
                    try:
                        resolved_final = resolved.resolve(strict=True)
                    except (OSError, RuntimeError):
                        result["errors"].append(f"Missing or unresolvable $path at {logical_path or '<root>'}: {raw_path}")
                    else:
                        if not resolved_final.is_relative_to(root):
                            result["errors"].append(f"$path escapes project root at {logical_path or '<root>'}: {raw_path}")
                        else:
                            # Reject symlink traversal even when the final target remains inside the root.
                            probe = project_path.parent
                            has_symlink = False
                            for part in candidate.parts:
                                probe = probe / part
                                if probe.is_symlink():
                                    has_symlink = True
                                    break
                            if has_symlink:
                                result["errors"].append(f"$path traverses a symlink at {logical_path or '<root>'}: {raw_path}")
                            else:
                                relative = resolved_final.relative_to(root).as_posix()
                                result["mapped_paths"].append(relative)
                                if relative in seen_paths:
                                    result["warnings"].append(f"Path is mapped more than once: {relative}")
                                seen_paths.add(relative)
        class_name = node.get("$className")
        if class_name is not None and not isinstance(class_name, str):
            result["errors"].append(f"$className at {logical_path or '<root>'} must be a string.")
        for key, child in node.items():
            if key.startswith("$"):
                continue
            if not isinstance(child, dict):
                result["errors"].append(f"Instance descriptor {logical_path + '/' + key} must be an object.")
                continue
            walk(child, f"{logical_path}/{key}".strip("/"))

    walk(tree, "")
    result["valid"] = not result["errors"]
    result["mapped_paths"] = sorted(set(result["mapped_paths"]))
    return result


def build_report(root: Path, max_files: int = 10_000) -> dict[str, Any]:
    warnings: list[str] = []
    files = iter_luau_files(root, max_files, warnings)
    sources: dict[Path, str] = {}
    modes: Counter[str] = Counter()
    instance_map: dict[tuple[str, ...], list[Path]] = defaultdict(list)
    read_failures: list[str] = []

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            read_failures.append(relative)
            continue
        sources[path] = source
        modes[type_mode(source)] += 1
        instance_map[script_instance_path(root, path)].append(path)

    edges: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    graph: dict[str, set[str]] = defaultdict(set)
    incoming: Counter[str] = Counter()
    dynamic_requires = 0
    for path, source in sources.items():
        origin = path.relative_to(root).as_posix()
        static_matches = list(STATIC_REQUIRE_RE.finditer(source))
        for match in static_matches:
            target, status, logical_target = resolve_script_require(
                match.group("expr"), path, root, instance_map
            )
            if status == "resolved" and target is not None:
                destination = target.relative_to(root).as_posix()
                edges.append({"from": origin, "to": destination, "expression": match.group("expr"), "status": status})
                graph[origin].add(destination)
                incoming[destination] += 1
            else:
                unresolved.append({
                    "from": origin,
                    "expression": match.group("expr"),
                    "logical_target": logical_target,
                    "status": status,
                })
        dynamic_requires += max(0, len(re.findall(r"\brequire\s*\(", source)) - len(static_matches))

    cycles = find_cycles(graph)
    candidates = {
        path.relative_to(root).as_posix()
        for path in sources
        if module_candidate(path)
    }
    referenced = set(incoming)
    possible_unused = sorted(candidates - referenced)
    project_paths = discover_rojo_projects(root)
    rojo_projects = [validate_rojo_project(path, root) for path in project_paths]
    strict_candidates = [
        path for path in possible_unused
        if modes  # keep this list deterministic while ensuring no mutation
    ]
    strict_percent = round((modes["strict"] / max(1, len(sources))) * 100, 2)

    remote_report = inspect_remotes(sources, root)
    return {
        "schema_version": 1,
        "toolkit_version": VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project_root": str(root),
        "inventory": {
            "luau_files_discovered": len(files),
            "luau_files_read": len(sources),
            "read_failures": read_failures,
            "type_mode_counts": {key: modes.get(key, 0) for key in ("strict", "nonstrict", "nocheck", "default")},
            "strict_mode_percent": strict_percent,
            "recommended_migration_policy": "Adopt --!strict incrementally at stable module and contract boundaries; do not mass-change every script.",
        },
        "dependencies": {
            "resolution_basis": "Filesystem-relative static require(script.Parent...) heuristic; Rojo mappings and dynamic aliases may alter instance relationships.",
            "resolved_edges": sorted(edges, key=lambda item: (item["from"], item["to"], item["expression"])),
            "unresolved_static_requires": unresolved,
            "dynamic_or_non_script_requires": dynamic_requires,
            "cycles": cycles,
            "possible_unreferenced_modules": possible_unused,
            "note": "Unreferenced files are review candidates only; runtime entrypoints, reflection, generated require names, and plugin wiring can make them intentional.",
        },
        "remote_contracts": remote_report,
        "rojo_projects": rojo_projects,
        "tools": {
            "luau_analyze": shutil.which("luau-analyze"),
            "rojo": shutil.which("rojo"),
        },
        "warnings": warnings,
        "limitations": [
            "This inventory is a conservative text-based analysis, not a full Luau parser or Roblox DataModel emulator.",
            "Only constant require(script.Parent...) chains are resolved; dynamic requires and custom module registries need manual inspection.",
            "The dependency graph's filesystem hierarchy may differ from a Rojo project's logical Instance tree.",
            "Remote matching is heuristic and does not prove server-side validation, authorization, rate limiting, or payload safety.",
            "No source file is changed by this report command.",
        ],
    }


def doctor_report(root: Path) -> dict[str, Any]:
    projects = discover_rojo_projects(root)
    return {
        "toolkit_version": VERSION,
        "project_root": str(root),
        "luau_files_present": any(
            path.suffix.lower() in {".lua", ".luau"}
            for path in root.rglob("*")
            if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        ),
        "luau_analyze": shutil.which("luau-analyze"),
        "rojo": shutil.which("rojo"),
        "rojo_project_files": [path.relative_to(root).as_posix() for path in projects],
        "guidance": [
            "Install Luau's luau-analyze CLI and Rojo CLI separately if you want V27 to run those tools.",
            "The doctor only checks PATH availability; it does not install tools or modify the project.",
            "Use the Roblox Studio Script Analysis window as an additional source of diagnostics.",
        ],
    }


def run_luau_analyzer(root: Path, files: list[Path], mode: str, timeout: int = 180) -> int:
    executable = shutil.which("luau-analyze")
    if not executable:
        raise RuntimeError("luau-analyze was not found on PATH. Install the official Luau CLI or run V27's offline audit.")
    if not files:
        print("PASS: no Luau source files were found.")
        return 0
    failures = 0
    batch_size = 80
    for batch_number, start in enumerate(range(0, len(files), batch_size), 1):
        batch = files[start:start + batch_size]
        command = [executable, "--formatter=plain"]
        if mode in {"strict", "nonstrict"}:
            command.append(f"--mode={mode}")
        command.extend(str(path.relative_to(root)) for path in batch)
        print(f"Running Luau analysis batch {batch_number} ({len(batch)} files)...")
        try:
            completed = subprocess.run(
                command, cwd=root, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired:
            print(f"FAIL: Luau analyzer timed out on batch {batch_number}.", file=sys.stderr)
            failures += 1
            continue
        except OSError as exc:
            print(f"FAIL: Could not start luau-analyze: {exc}", file=sys.stderr)
            return 1
        if completed.stdout:
            print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n")
        if completed.returncode:
            failures += 1
    if failures:
        print(f"FAIL: Luau analysis reported errors in {failures} batch(es).", file=sys.stderr)
        return 1
    print("PASS: Luau analyzer completed with no reported errors.")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    report = doctor_report(root)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"V27 Luau architecture doctor — {VERSION}")
        print(f"Project root: {root}")
        print(f"Luau analyzer: {report['luau_analyze'] or 'not found'}")
        print(f"Rojo CLI: {report['rojo'] or 'not found'}")
        print(f"Rojo project files: {len(report['rojo_project_files'])}")
        for message in report["guidance"]:
            print(f"INFO: {message}")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    report = build_report(root, args.max_files)
    target = safe_output_path(root, args.output)
    if target.exists() and not args.force:
        raise FileExistsError(f"Report already exists; use --force to replace it: {target}")
    atomic_write_json(target, report)
    dependencies = report["dependencies"]
    print(f"PASS: V27 architecture report generated: {target}")
    print(f"Luau files: {report['inventory']['luau_files_read']}")
    print(f"Static dependency edges: {len(dependencies['resolved_edges'])}")
    print(f"Potential dependency cycles: {len(dependencies['cycles'])}")
    print(f"Unresolved static requires: {len(dependencies['unresolved_static_requires'])}")
    print(f"Potentially unreferenced modules: {len(dependencies['possible_unreferenced_modules'])}")
    print("No source scripts were modified.")
    return 0


def find_rojo_project(root: Path, raw_project: str | None) -> Path:
    if raw_project:
        supplied = Path(raw_project).expanduser()
        project = supplied if supplied.is_absolute() else root / supplied
        try:
            resolved = project.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise ValueError("Rojo project file could not be resolved.") from exc
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError("Rojo project file must be a regular file inside the selected project root.")
        if project.is_symlink():
            raise ValueError("Rojo project file cannot be a symlink.")
        return resolved
    projects = discover_rojo_projects(root)
    if len(projects) != 1:
        raise ValueError(f"Expected exactly one .project.json file; found {len(projects)}. Pass --project to select one.")
    return projects[0]


def command_rojo_check(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    project = find_rojo_project(root, args.project)
    report = validate_rojo_project(project, root)
    if report["errors"]:
        for error in report["errors"]:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")
    print(f"PASS: Rojo project structure and {len(report['mapped_paths'])} path mapping(s) validated.")
    if args.build:
        executable = shutil.which("rojo")
        if not executable:
            print("FAIL: --build was requested but the Rojo CLI was not found on PATH.", file=sys.stderr)
            return 1
        with tempfile.TemporaryDirectory(prefix="v27-rojo-build-") as temporary:
            output = Path(temporary) / "v27-validation.rbxlx"
            command = [executable, "build", str(project), "-o", str(output)]
            try:
                completed = subprocess.run(
                    command, cwd=project.parent, capture_output=True, text=True, timeout=args.timeout, check=False
                )
            except subprocess.TimeoutExpired:
                print("FAIL: Rojo build timed out.", file=sys.stderr)
                return 1
            except OSError as exc:
                print(f"FAIL: Could not start Rojo: {exc}", file=sys.stderr)
                return 1
            if completed.stdout:
                print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
            if completed.stderr:
                print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n")
            if completed.returncode or not output.is_file():
                print("FAIL: Rojo build failed; no source or place file was modified.", file=sys.stderr)
                return 1
            print(f"PASS: Rojo build succeeded; temporary output size={output.stat().st_size} bytes.")
            print("The temporary place file was deleted after validation.")
    return 0


def command_typecheck(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    warnings: list[str] = []
    files = iter_luau_files(root, args.max_files, warnings)
    for warning in warnings:
        print(f"WARNING: {warning}")
    return run_luau_analyzer(root, files, args.mode, args.timeout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Check project and local tool availability.")
    doctor.add_argument("--root", required=True)
    doctor.add_argument("--format", choices=("text", "json"), default="text")
    doctor.set_defaults(handler=command_doctor)

    audit = sub.add_parser("audit", help="Generate an offline Luau architecture report.")
    audit.add_argument("--root", required=True)
    audit.add_argument("--output", default=DEFAULT_REPORT)
    audit.add_argument("--max-files", type=int, default=10_000)
    audit.add_argument("--force", action="store_true")
    audit.set_defaults(handler=command_audit)

    rojo = sub.add_parser("rojo-check", help="Validate Rojo project JSON and path mappings.")
    rojo.add_argument("--root", required=True)
    rojo.add_argument("--project", help="Optional .project.json path inside the project root.")
    rojo.add_argument("--build", action="store_true", help="Run rojo build to a temporary file and delete it afterwards.")
    rojo.add_argument("--timeout", type=int, default=180)
    rojo.set_defaults(handler=command_rojo_check)

    typecheck = sub.add_parser("typecheck", help="Run the official luau-analyze CLI over project scripts.")
    typecheck.add_argument("--root", required=True)
    typecheck.add_argument("--mode", choices=("project", "strict", "nonstrict"), default="project")
    typecheck.add_argument("--max-files", type=int, default=10_000)
    typecheck.add_argument("--timeout", type=int, default=180)
    typecheck.set_defaults(handler=command_typecheck)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "max_files", 1) < 1 or getattr(args, "max_files", 1) > MAX_ANALYZE_FILES:
        print(f"FAIL: --max-files must be between 1 and {MAX_ANALYZE_FILES}.", file=sys.stderr)
        return 1
    if getattr(args, "timeout", 1) < 1 or getattr(args, "timeout", 1) > 900:
        print("FAIL: --timeout must be between 1 and 900 seconds.", file=sys.stderr)
        return 1
    try:
        return args.handler(args)
    except (OSError, RuntimeError, ValueError, FileExistsError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
