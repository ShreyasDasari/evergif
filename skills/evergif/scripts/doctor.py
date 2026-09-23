#!/usr/bin/env python3
"""Check that this machine can render evergif demos.

Prints JSON to stdout describing what is installed:
  terminal: "ready" when vhs, ttyd and ffmpeg are present, else "missing"
  web:      "ready" when Node is present (Playwright is fetched on demand)
Exit code is 0 when terminal demos can be rendered, 1 otherwise; install
commands for the detected OS are printed to stderr.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys

TERMINAL = ("vhs", "ttyd", "ffmpeg")
OPTIONAL = ("gifsicle",)


def node_version() -> str | None:
    if not shutil.which("node"):
        return None
    try:
        result = subprocess.run(["node", "--version"], capture_output=True,
                                text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or None if result.returncode == 0 else None


def detect() -> dict:
    tools = {name: shutil.which(name) for name in TERMINAL + OPTIONAL}
    missing = [name for name in TERMINAL if not tools[name]]
    node = node_version()
    return {
        "terminal": "missing" if missing else "ready",
        "web": "ready" if node else "missing",
        "tools": tools,
        "node": node,
        "missing": missing,
        "gifsicle": bool(tools["gifsicle"]),
    }


def linux_distro() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as fh:
            fields = dict(
                line.rstrip("\n").split("=", 1) for line in fh if "=" in line
            )
    except OSError:
        return ""
    ids = f"{fields.get('ID', '')} {fields.get('ID_LIKE', '')}".replace('"', "")
    for family in ("debian", "ubuntu", "fedora", "rhel", "arch", "alpine"):
        if family in ids.split():
            return family
    return ""


def install_commands() -> list[str]:
    system = platform.system()
    if system == "Darwin":
        return ["brew install vhs gifsicle"]
    if system == "Windows":
        return ["scoop install vhs gifsicle",
                "# then run evergif from WSL or Git Bash: tapes use bash"]
    distro = linux_distro()
    if distro in ("debian", "ubuntu"):
        return [
            "sudo apt install -y ffmpeg gifsicle ttyd",
            "# vhs: download the .deb for your architecture from",
            "#   https://github.com/charmbracelet/vhs/releases",
            "#   then: sudo dpkg -i vhs_*.deb",
        ]
    if distro in ("fedora", "rhel"):
        return [
            r"printf '[charm]\nname=Charm\nbaseurl=https://repo.charm.sh/yum/\nenabled=1\ngpgcheck=1\ngpgkey=https://repo.charm.sh/yum/gpg.key\n' | sudo tee /etc/yum.repos.d/charm.repo",
            "sudo yum install -y vhs ffmpeg gifsicle ttyd",
        ]
    if distro == "arch":
        return ["sudo pacman -S vhs gifsicle"]
    return [
        "go install github.com/charmbracelet/vhs@latest",
        "# plus ttyd (https://github.com/tsl0922/ttyd) and ffmpeg",
    ]


def main() -> int:
    report = detect()
    print(json.dumps(report, indent=2))
    if report["terminal"] == "missing":
        print("evergif needs vhs, ttyd and ffmpeg to record a terminal demo. "
              f"Missing: {', '.join(report['missing'])}.", file=sys.stderr)
        for command in install_commands():
            print(f"  {command}", file=sys.stderr)
        return 1
    if not report["gifsicle"]:
        print("note: gifsicle not found; optimizing with ffmpeg instead "
              "(results are larger)", file=sys.stderr)
    if report["web"] == "missing":
        print("note: Node is not installed, so web demos are unavailable "
              "(https://nodejs.org). Terminal demos are unaffected.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
