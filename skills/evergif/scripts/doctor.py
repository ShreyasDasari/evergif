#!/usr/bin/env python3
"""Detect the evergif rendering toolchain and choose a render mode.

Prints JSON to stdout:
  mode: "local"  -> vhs, ttyd and ffmpeg are on PATH
        "docker" -> something is missing, but Docker works (ghcr.io/charmbracelet/vhs)
        "none"   -> neither; exact install commands are printed to stderr
Exit code is 0 for local/docker and 1 for none.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys

VHS_IMAGE = "ghcr.io/charmbracelet/vhs"
REQUIRED = ("vhs", "ttyd", "ffmpeg")
OPTIONAL = ("gifsicle",)


def docker_available() -> bool:
    """True only if the docker CLI exists and the daemon answers."""
    if not shutil.which("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def detect() -> dict:
    tools = {name: shutil.which(name) for name in REQUIRED + OPTIONAL}
    docker = docker_available()
    missing = [name for name in REQUIRED if not tools[name]]
    if not missing:
        mode = "local"
    elif docker:
        mode = "docker"
    else:
        mode = "none"
    return {
        "mode": mode,
        "tools": tools,
        "docker": docker,
        "missing": missing,
        "gifsicle": bool(tools["gifsicle"]),
        "image": VHS_IMAGE,
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
        return ["scoop install vhs gifsicle"]
    distro = linux_distro()
    if distro in ("debian", "ubuntu"):
        return [
            "sudo mkdir -p /etc/apt/keyrings",
            "curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg",
            'echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list',
            "sudo apt update && sudo apt install -y vhs ffmpeg gifsicle",
            "# ttyd: https://github.com/tsl0922/ttyd/releases (or: sudo apt install ttyd on Ubuntu 22.04+)",
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
        "# plus ttyd (https://github.com/tsl0922/ttyd) and ffmpeg from your package manager",
    ]


def main() -> int:
    report = detect()
    print(json.dumps(report, indent=2))
    if report["mode"] == "docker":
        print(f"note: using Docker fallback ({VHS_IMAGE}); missing: "
              + ", ".join(report["missing"]), file=sys.stderr)
    if report["mode"] == "none":
        print("evergif needs vhs (with ttyd + ffmpeg) or Docker. Install vhs with:",
              file=sys.stderr)
        for cmd in install_commands():
            print(f"  {cmd}", file=sys.stderr)
        print("or install Docker: https://docs.docker.com/get-docker/", file=sys.stderr)
        return 1
    if not report["gifsicle"]:
        print("note: gifsicle not found; optimizing with ffmpeg instead "
              "(results are larger)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
