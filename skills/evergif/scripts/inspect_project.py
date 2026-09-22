#!/usr/bin/env python3
"""Collect facts an agent needs to pick demo commands for a CLI project.

Usage: inspect_project.py [ROOT]

Prints JSON: the README pitch, shell commands quoted in the README, declared
entry points with an invocation that works from ROOT, and their --help output.

--help is only executed when the entry point's source visibly handles it
(argparse, click, a `--help` case, ...) or it is declared as a console script /
package bin. It runs twice, with a 5 s timeout, stdin closed, and a minimal
environment, so the output can be flagged as deterministic or not.
"""
from __future__ import annotations

import getpass
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

HELP_MARKERS = re.compile(
    r"--help|argparse|click|typer|docopt|fire\.Fire|commander|yargs|clap|cobra|"
    r"urfave/cli|getopts|usage", re.IGNORECASE)
SHELL_FENCES = ("bash", "sh", "shell", "console", "zsh", "terminal", "")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
             "build", "target", "demo", ".github"}
MAX_HELP_LINES = 40


def read(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def readme_facts(root: Path) -> dict:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        path = root / name
        if path.is_file():
            break
    else:
        return {"path": None, "title": None, "pitch": None, "commands": []}
    text = read(path)
    title = next((line.lstrip("# ").strip() for line in text.splitlines()
                  if line.startswith("# ")), None)
    pitch = None
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if block and not block.startswith(("#", "<", "[!", "!", "```", "|")):
            pitch = " ".join(block.split())[:300]
            break
    commands = []
    for lang, body in re.findall(r"```(\w*)\n(.*?)```", text, re.DOTALL):
        if lang.lower() not in SHELL_FENCES:
            continue
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("$ "):
                line = line[2:]
            elif lang.lower() == "console":
                continue
            if line and not line.startswith("#"):
                commands.append(line)
    return {"path": path.name, "title": title, "pitch": pitch,
            "commands": commands[:20]}


def section(text: str, header: str) -> str:
    match = re.search(rf"^\[{re.escape(header)}\]\s*$(.*?)(?=^\[|\Z)", text,
                      re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def entry_points(root: Path) -> list[dict]:
    found: list[dict] = []

    pyproject = read(root / "pyproject.toml")
    for header in ("project.scripts", "tool.poetry.scripts"):
        for name, target in re.findall(r'^\s*"?([\w.-]+)"?\s*=\s*"([^"]+)"',
                                       section(pyproject, header), re.MULTILINE):
            module = target.split(":")[0]
            found.append({"name": name, "kind": "python-script",
                          "declared_in": "pyproject.toml", "target": target,
                          "fallback": f"python3 -m {module}"})

    setup_cfg = read(root / "setup.cfg")
    for name, target in re.findall(r"^\s*([\w.-]+)\s*=\s*([\w.]+:\w+)",
                                   section(setup_cfg, "options.entry_points"),
                                   re.MULTILINE):
        found.append({"name": name, "kind": "python-script",
                      "declared_in": "setup.cfg", "target": target,
                      "fallback": f"python3 -m {target.split(':')[0]}"})

    package_json = root / "package.json"
    if package_json.is_file():
        try:
            pkg = json.loads(read(package_json))
        except json.JSONDecodeError:
            pkg = {}
        bins = pkg.get("bin") or {}
        if isinstance(bins, str):
            bins = {pkg.get("name", "cli").split("/")[-1]: bins}
        for name, target in bins.items():
            found.append({"name": name, "kind": "node-bin",
                          "declared_in": "package.json", "target": target,
                          "fallback": f"node {target}"})

    cargo = read(root / "Cargo.toml")
    if cargo:
        names = re.findall(r'^\s*name\s*=\s*"([^"]+)"', section(cargo, "[bin]"),
                           re.MULTILINE)
        if not names:
            names = re.findall(r'^\s*name\s*=\s*"([^"]+)"',
                               section(cargo, "package"), re.MULTILINE)[:1]
        for name in names:
            found.append({"name": name, "kind": "rust-bin",
                          "declared_in": "Cargo.toml", "target": name,
                          "fallback": f"cargo run -q --bin {name} --"})

    gomod = read(root / "go.mod")
    if gomod and (root / "main.go").is_file():
        module = re.search(r"^module\s+(\S+)", gomod, re.MULTILINE)
        name = module.group(1).rsplit("/", 1)[-1] if module else root.name
        found.append({"name": name, "kind": "go-main", "declared_in": "go.mod",
                      "target": "main.go", "fallback": "go run ."})

    declared = {ep["name"] for ep in found}
    for path in sorted(scan_files(root)):
        rel = path.relative_to(root).as_posix()
        head = read(path, 200)
        if path.suffix == ".py" and path.name == "__main__.py":
            module = ".".join(path.parent.relative_to(root).parts)
            if module and module not in declared:
                found.append({"name": module, "kind": "python-module",
                              "declared_in": rel, "target": rel,
                              "fallback": f"python3 -m {module}"})
        elif head.startswith("#!") and path.stem not in declared:
            shebang = head.splitlines()[0]
            if os.access(path, os.X_OK):
                invoke = f"./{rel}"
            elif "python" in shebang:
                invoke = f"python3 {rel}"
            else:
                invoke = f"bash {rel}"
            found.append({"name": path.stem, "kind": "script",
                          "declared_in": rel, "target": rel, "fallback": invoke})
    return found


def scan_files(root: Path, depth: int = 2):
    def walk(directory: Path, level: int):
        try:
            entries = list(directory.iterdir())
        except OSError:
            return
        for entry in entries:
            if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue
            if entry.is_dir() and not entry.is_symlink() and level < depth:
                yield from walk(entry, level + 1)
            elif entry.is_file() and entry.stat().st_size < 500_000:
                yield entry
    yield from walk(root, 0)


def minimal_env() -> dict:
    env = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR", "SYSTEMROOT")
           if key in os.environ}
    env.update({"LANG": "en_US.UTF-8", "TERM": "xterm-256color", "NO_COLOR": "1",
                "COLUMNS": "100"})
    return env


def run_help(invoke: str, root: Path) -> dict:
    argv = shlex.split(invoke) + ["--help"]
    outputs = []
    for _ in range(2):
        try:
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                                    timeout=5, stdin=subprocess.DEVNULL,
                                    env=minimal_env())
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ran": False, "error": type(exc).__name__}
        outputs.append((result.returncode, result.stdout + result.stderr))
    code, text = outputs[0]
    lines = text.rstrip().splitlines()
    private = [p for p in (str(Path.home()), getpass.getuser()) if p and len(p) > 2]
    return {
        "ran": True,
        "exit_code": code,
        "lines": len(lines),
        "deterministic": outputs[0] == outputs[1],
        "leaks_private_path": any(p in text for p in private),
        "output": "\n".join(lines[:MAX_HELP_LINES]),
    }


def resolve(ep: dict, root: Path) -> None:
    ep["installed"] = bool(shutil.which(ep["name"]))
    ep["invoke"] = ep["name"] if ep["installed"] else ep["fallback"]
    source = root / ep["target"] if (root / ep["target"]).is_file() else None
    if ep["kind"] in ("python-script", "python-module"):
        module_path = ep["target"].split(":")[0].replace(".", "/")
        for candidate in (root / f"{module_path}.py", root / module_path / "__main__.py",
                          root / "src" / f"{module_path}.py"):
            if candidate.is_file():
                source = candidate
                break
    declared = ep["kind"] in ("python-script", "node-bin", "rust-bin", "go-main")
    handles_help = bool(source and HELP_MARKERS.search(read(source)))
    if declared or handles_help:
        ep["help"] = run_help(ep["invoke"], root)
    else:
        ep["help"] = {"ran": False,
                      "error": "skipped: source shows no --help handling"}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    eps = entry_points(root)
    for ep in eps:
        resolve(ep, root)
    report = {
        "root": str(root),
        "readme": readme_facts(root),
        "entry_points": eps,
        "existing_tape": (root / "demo" / "evergif.tape").is_file(),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
