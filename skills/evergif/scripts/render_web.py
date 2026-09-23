#!/usr/bin/env python3
"""Run a generated Playwright script and turn its video into an optimized GIF.

Usage: render_web.py [--name NAME | --script PATH] [--all]
                     [--fps 12] [--width 1000] [--target-mb 2] [--max-mb 5]
                     [--keep-webm]

Starts the app (the `serve` command recorded in the script), waits for the URL
to answer, records the demo, converts the video to a GIF, and optimizes it.

--docker records with the official Playwright image instead of a local Node,
for machines with no Node at all. It needs a Linux host: the container reaches
the app through --network host, which Docker Desktop and Colima do not provide.

Freshness: the script writes demo/<name>.transcript.txt, the visible text after
each step. Its hash goes in demo/<name>.lock, so a web demo is only considered
changed when the page's content changed, not when a pixel moved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from render import MB, WEB_GIFSICLE_LEVELS, optimize

PLAYWRIGHT_VERSION = "1.63.0"
PLAYWRIGHT_IMAGE = f"mcr.microsoft.com/playwright:v{PLAYWRIGHT_VERSION}-noble"
SERVE_TIMEOUT = 90


def read_config(script: Path) -> dict:
    settings = script.with_suffix(".json")
    if not settings.is_file():
        sys.exit(f"error: {settings} not found (regenerate with web_tape.py)")
    return json.loads(settings.read_text(encoding="utf-8"))


def wait_for(url: str, process: subprocess.Popen | None) -> None:
    """Poll the app until it answers, so recording never races the server."""
    deadline = time.monotonic() + SERVE_TIMEOUT
    last = ""
    while time.monotonic() < deadline:
        if process and process.poll() is not None:
            sys.exit(f"error: the serve command exited with {process.returncode} "
                     "before the app was reachable")
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last = str(exc)
        time.sleep(1)
    sys.exit(f"error: {url} did not answer within {SERVE_TIMEOUT}s ({last})")


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / "evergif" / "node"


def node_env() -> dict | None:
    """Environment in which the runner can resolve Playwright.

    Uses the project's own Playwright when it has one. Otherwise installs it
    into evergif's cache directory -- never into the user's project -- and
    points NODE_PATH there, which is what `createRequire` in the generated
    runner looks at.
    """
    env = os.environ.copy()
    probe = "console.log(require.resolve('playwright'))"
    try:
        local = subprocess.run(["node", "-e", probe], capture_output=True, text=True,
                               timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        print("error: Node 18+ is required for web demos (https://nodejs.org)",
              file=sys.stderr)
        return None
    if local.returncode == 0 and local.stdout.strip():
        return env

    cache = cache_dir()
    modules = cache / "node_modules"
    if not (modules / "playwright").is_dir():
        print(f"+ fetching playwright@{PLAYWRIGHT_VERSION} into {cache} "
              "(one time, not added to your project)", file=sys.stderr)
        cache.mkdir(parents=True, exist_ok=True)
        install = subprocess.run(
            ["npm", "install", "--prefix", str(cache), "--no-audit", "--no-fund",
             "--silent", f"playwright@{PLAYWRIGHT_VERSION}"], timeout=900)
        if install.returncode != 0 or not (modules / "playwright").is_dir():
            print("error: could not install Playwright; run with --docker instead",
                  file=sys.stderr)
            return None
    env["NODE_PATH"] = str(modules)
    return env


def ensure_browser(env: dict) -> None:
    """Download the matching Chromium if it is not already cached."""
    cli = cache_dir() / "node_modules" / ".bin" / "playwright"
    command = [str(cli)] if cli.is_file() else ["npx", "--yes",
                                                f"playwright@{PLAYWRIGHT_VERSION}"]
    subprocess.run(command + ["install", "chromium"], env=env, check=False)


def run_script(script: Path, cwd: Path, docker: bool) -> None:
    if docker:
        cmd = ["docker", "run", "--rm", "--ipc=host", "--init",
               "-v", f"{cwd}:/work", "-w", "/work", "--network", "host"]
        if hasattr(os, "getuid"):
            # Without this the recording lands in the repo owned by root.
            cmd += ["--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp"]
        # The image ships the browsers, not the npm package, so fetch the
        # matching package into a writable prefix and point NODE_PATH at it.
        # The browsers are already in /ms-playwright; skip downloading them.
        inner = (
            "set -e; export HOME=/tmp PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1; "
            f"npm install --prefix /tmp/pw --no-audit --no-fund --silent "
            f"playwright@{PLAYWRIGHT_VERSION} >/dev/null; "
            "export NODE_PATH=/tmp/pw/node_modules; "
            f"exec node {script.as_posix()}"
        )
        cmd += [PLAYWRIGHT_IMAGE, "sh", "-c", inner]
        env = None
    else:
        env = node_env()
        if env is None:
            sys.exit("error: could not set up Playwright; see the message above")
        ensure_browser(env)
        cmd = ["node", script.as_posix()]
    print("+ " + " ".join(cmd), file=sys.stderr)
    if subprocess.run(cmd, cwd=cwd, env=env).returncode != 0:
        sys.exit(f"error: {script} failed; see the output above")


def to_gif(webm: Path, gif: Path, fps: int, width: int) -> None:
    # width 0 keeps the recording's own pixels. Downscaling a UI recording
    # softens every label in it, so it is a last resort, not a default.
    scaling = f",scale={width}:-1:flags=lanczos" if width else ""
    graph = (f"fps={fps}{scaling},split[a][b];"
             "[a]palettegen=max_colors=256:stats_mode=diff[p];"
             "[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(webm), "-vf", graph,
           "-loop", "0", str(gif)]
    if subprocess.run(cmd).returncode != 0 or not gif.is_file():
        sys.exit(f"error: could not convert {webm} to a GIF")


def render_one(script: Path, args: argparse.Namespace, cwd: Path) -> dict:
    config = read_config(script)
    name = script.name.removesuffix(".web.mjs")
    gif = Path(f"demo/{name}.gif")
    webm = Path(config["videoPath"])
    transcript = Path(config["transcriptPath"])
    lock = Path(f"demo/{name}.lock")
    previous = lock.read_text(encoding="utf-8").strip() if lock.is_file() else None

    server = None
    if config.get("serve"):
        print(f"+ {config['serve']}", file=sys.stderr)
        server = subprocess.Popen(config["serve"], shell=True, cwd=cwd,
                                  start_new_session=True)
    try:
        wait_for(config["url"], server)
        shutil.rmtree(config["videoDir"], ignore_errors=True)
        run_script(script, cwd, args.docker)
    finally:
        if server and server.poll() is None:
            os.killpg(os.getpgid(server.pid), signal.SIGTERM)
        shutil.rmtree(config["videoDir"], ignore_errors=True)

    if not webm.is_file():
        sys.exit(f"error: no video at {webm}")
    # Hash the settings with the transcript: changing the viewport or the steps
    # must re-render even when the page's text is unchanged. Must stay
    # byte-identical to what the workflow computes.
    digest = hashlib.sha256(
        script.with_suffix(".json").read_bytes()
        + (transcript.read_bytes() if transcript.is_file() else b"")
    ).hexdigest()
    transcript.unlink(missing_ok=True)  # the hash in the lock file is the record

    backup = gif.with_suffix(".gif.previous") if gif.is_file() else None
    if backup:
        gif.replace(backup)
    try:
        to_gif(webm, gif, args.fps, args.width)
    except SystemExit:
        if backup:
            backup.replace(gif)
        raise
    finally:
        if backup and backup.is_file() and gif.is_file():
            backup.unlink()
    if not args.keep_webm:
        webm.unlink(missing_ok=True)

    result = optimize(gif, cwd, int(args.target_mb * MB),
                      levels=WEB_GIFSICLE_LEVELS)
    lock.write_text(digest, encoding="utf-8")
    result.update({"demo": name, "script": script.as_posix(), "gif": gif.as_posix(),
                   "mb": round(result["bytes"] / MB, 2),
                   "content_hash": digest,
                   "content_changed": previous != digest,
                   "under_target": result["bytes"] <= args.target_mb * MB,
                   "over_limit": result["bytes"] > args.max_mb * MB})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default=None, help="demo name to render")
    parser.add_argument("--script", default=None, help="default: demo/<name>.web.mjs")
    parser.add_argument("--all", action="store_true",
                        help="render every demo/*.web.mjs")
    parser.add_argument("--docker", action="store_true",
                        help=f"run inside {PLAYWRIGHT_IMAGE}")
    parser.add_argument("--fps", type=int, default=10,
                        help="UI motion reads as smooth at 10; fewer frames "
                             "leaves more bytes for each one")
    parser.add_argument("--width", type=int, default=0,
                        help="downscale to this width; 0 keeps the recording's "
                             "own resolution, which keeps UI text crisp")
    parser.add_argument("--target-mb", type=float, default=2.0)
    parser.add_argument("--max-mb", type=float, default=5.0)
    parser.add_argument("--keep-webm", action="store_true")
    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    if args.all:
        scripts = sorted(Path("demo").glob("*.web.mjs"))
        if not scripts:
            sys.exit("error: no demo/*.web.mjs (run web_tape.py first)")
    else:
        name = args.name or "evergif-web"
        scripts = [Path(args.script) if args.script
                   else Path("demo") / f"{name}.web.mjs"]
        if not scripts[0].is_file():
            sys.exit(f"error: {scripts[0]} not found (run web_tape.py first)")
    if not shutil.which("ffmpeg") and not args.docker:
        sys.exit("error: ffmpeg is needed to turn the video into a GIF")

    results = [render_one(script, args, cwd) for script in scripts]
    print(json.dumps(results if args.all else results[0], indent=2))
    oversized = [r for r in results if r["over_limit"]]
    for result in oversized:
        print(f"error: {result['gif']} is {result['mb']} MB (limit {args.max_mb} MB); "
              "record fewer steps or lower --fps/--width", file=sys.stderr)
    return 1 if oversized else 0


if __name__ == "__main__":
    sys.exit(main())
