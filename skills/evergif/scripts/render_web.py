#!/usr/bin/env python3
"""Run a generated Playwright script and turn its video into an optimized GIF.

Usage: render_web.py [--name NAME | --script PATH] [--all]
                     [--fps 12] [--width 1000] [--target-mb 2] [--max-mb 5]
                     [--keep-webm]

Starts the app (the `serve` command recorded in the script), waits for the URL
to answer, records the demo, converts the video to a GIF, and optimizes it.

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

from render import MB, optimize

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


def node_env() -> tuple[list[str], dict] | None:
    """How to run node so that `import 'playwright'` resolves.

    Prefers a playwright already in the project, then npm's package cache. Both
    avoid installing anything into the user's project.
    """
    env = os.environ.copy()
    probe = "console.log(require.resolve('playwright'))"
    try:
        local = subprocess.run(["node", "-e", probe], capture_output=True, text=True,
                               timeout=30)
        if local.returncode == 0 and local.stdout.strip():
            return ["node"], env
    except (OSError, subprocess.TimeoutExpired):
        return None
    fetched = subprocess.run(
        ["npm", "exec", "--yes", f"--package=playwright@{PLAYWRIGHT_VERSION}", "--",
         "node", "-e", probe],
        capture_output=True, text=True, timeout=600)
    if fetched.returncode != 0 or not fetched.stdout.strip():
        return None
    # .../node_modules/playwright/index.js -> .../node_modules
    modules = Path(fetched.stdout.strip().splitlines()[-1]).parent.parent
    env["NODE_PATH"] = str(modules)
    return ["node"], env


def ensure_browser(env: dict) -> None:
    subprocess.run(["npx", "--yes", f"playwright@{PLAYWRIGHT_VERSION}", "install",
                    "chromium"], env=env, check=False)


def run_script(script: Path, cwd: Path, docker: bool) -> None:
    if docker:
        cmd = ["docker", "run", "--rm", "--ipc=host", "--init",
               "-v", f"{cwd}:/work", "-w", "/work", "--network", "host",
               PLAYWRIGHT_IMAGE, "node", script.as_posix()]
        env = None
    else:
        resolved = node_env()
        if resolved is None:
            sys.exit("error: could not resolve Playwright; install Node 18+ "
                     "(https://nodejs.org) or run with --docker")
        argv, env = resolved
        ensure_browser(env)
        cmd = argv + [script.as_posix()]
    print("+ " + " ".join(cmd), file=sys.stderr)
    if subprocess.run(cmd, cwd=cwd, env=env).returncode != 0:
        sys.exit(f"error: {script} failed; see the output above")


def to_gif(webm: Path, gif: Path, fps: int, width: int) -> None:
    graph = (f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];"
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
    digest = hashlib.sha256(transcript.read_bytes()).hexdigest() \
        if transcript.is_file() else "none"

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

    result = optimize(gif, cwd, int(args.target_mb * MB), docker=False)
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
    parser.add_argument("--fps", type=int, default=12,
                        help="web video is heavy; 12 reads as smooth for UI")
    parser.add_argument("--width", type=int, default=1000)
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
