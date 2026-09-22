#!/usr/bin/env python3
"""Write a Playwright script that records a web app demo.

Usage:
  web_tape.py --steps "goto /; click #new; fill #title Hello; wait .saved"
              [--name NAME] [--url http://localhost:3000] [--serve "npm run dev"]
              [--size 1280x720] [--pause 900] [--allow-external] [--stdout]

This is the web equivalent of a vhs tape: a committed, reviewable script that
renders the same demo every time. Steps are checked against a safety policy
(localhost only, no credentials, no destructive serve command).

Steps, separated by ";":
  goto PATH            navigate to URL + PATH
  click SELECTOR       click an element
  fill SELECTOR TEXT   type TEXT into an element
  press KEY            press a key (Enter, Escape, ...)
  wait SELECTOR        wait until an element appears
  scroll PIXELS        scroll down (negative scrolls up)
  pause MS             hold still, to let the viewer read
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from tape import check as command_check, split_commands

DEFAULT_NAME = "evergif-web"
DEFAULT_URL = "http://localhost:3000"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
SIZE_RE = re.compile(r"^(\d{3,4})x(\d{3,4})$")
LOCAL_HOSTS = ("localhost", "127.0.0.1", "[::1]", "0.0.0.0")
ACTIONS = {"goto": 1, "click": 1, "fill": 2, "press": 1, "wait": 1,
           "scroll": 1, "pause": 1}
SECRET_RE = re.compile(r"password|passwd|secret|token|api[_-]?key|credential|"
                       r"otp|2fa|ssn|credit[_-]?card", re.IGNORECASE)
RUNNER = """
const transcript = [];

function visible(text) {
  return text.split('\\n').map((line) => line.trim()).filter(Boolean)
    .slice(0, 40).join('\\n');
}

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: config.viewport,
  recordVideo: { dir: config.videoDir, size: config.viewport },
  deviceScaleFactor: 1,
  reducedMotion: 'reduce',
  colorScheme: config.colorScheme,
});
const page = await context.newPage();

try {
  for (const step of config.steps) {
    switch (step.action) {
      case 'goto':
        await page.goto(config.url + step.args[0], { waitUntil: 'networkidle' });
        break;
      case 'click':
        await page.click(step.args[0]);
        break;
      case 'fill':
        await page.fill(step.args[0], step.args.slice(1).join(' '));
        break;
      case 'press':
        await page.keyboard.press(step.args[0]);
        break;
      case 'wait':
        await page.waitForSelector(step.args[0]);
        break;
      case 'scroll':
        await page.mouse.wheel(0, Number(step.args[0]));
        break;
      case 'pause':
        await page.waitForTimeout(Number(step.args[0]));
        break;
      default:
        throw new Error(`unknown step: ${step.action}`);
    }
    await page.waitForTimeout(config.pauseMs);
    transcript.push(`> ${step.raw}`);
    transcript.push(visible(await page.innerText('body')));
  }
} finally {
  const video = page.video();
  await context.close();
  await browser.close();
  if (video) {
    await mkdir(dirname(config.videoPath), { recursive: true });
    await rename(await video.path(), config.videoPath);
  }
  await writeFile(config.transcriptPath, transcript.join('\\n') + '\\n');
}

console.log(`evergif: recorded ${config.steps.length} steps to ${config.videoPath}`);
"""


def parse_steps(text: str) -> list[dict]:
    steps = []
    for raw in split_commands(text):
        parts = raw.split()
        action = parts[0].lower()
        if action not in ACTIONS:
            raise ValueError(f"unknown step {action!r} in {raw!r}; "
                             f"use one of {', '.join(sorted(ACTIONS))}")
        args = parts[1:]
        if len(args) < ACTIONS[action]:
            raise ValueError(f"step {raw!r} needs {ACTIONS[action]} argument(s)")
        if action in ("scroll", "pause") and not re.fullmatch(r"-?\d+", args[0]):
            raise ValueError(f"step {raw!r} needs a number, got {args[0]!r}")
        steps.append({"action": action, "args": args, "raw": raw})
    return steps


def check_steps(steps: list[dict]) -> str | None:
    """Return why these steps are unsafe to record, or None."""
    for step in steps:
        joined = " ".join(step["args"])
        if SECRET_RE.search(joined):
            return (f"step {step['raw']!r} mentions credentials; never record a "
                    "login, a password field, or a real token")
        if step["action"] == "goto" and not step["args"][0].startswith("/"):
            return f"goto takes a path starting with '/', got {step['args'][0]!r}"
        if step["action"] == "fill" and len(step["args"]) < 2:
            return f"step {step['raw']!r} needs a selector and text"
    return None


def check_url(url: str, allow_external: bool) -> str | None:
    match = re.match(r"^https?://([^/:]+|\[[^\]]+\])(:\d+)?(/.*)?$", url)
    if not match:
        return f"--url must be a full http(s) URL, got {url!r}"
    host = match.group(1)
    if host not in LOCAL_HOSTS and not allow_external:
        return (f"--url points at {host}, not localhost. Recording a live site "
                "can capture real user data; pass --allow-external only if the "
                "user explicitly asked for that exact URL")
    return None


def build(name: str, url: str, steps: list[dict], size: tuple[int, int],
          pause: int, scheme: str, serve: str | None) -> str:
    config = {
        "url": url.rstrip("/"),
        "steps": steps,
        "viewport": {"width": size[0], "height": size[1]},
        "pauseMs": pause,
        "colorScheme": scheme,
        "videoDir": f"demo/.{name}-video",
        "videoPath": f"demo/{name}.webm",
        "transcriptPath": f"demo/{name}.transcript.txt",
        "serve": serve,
    }
    return (
        "// Generated by evergif (https://github.com/ShreyasDasari/evergif).\n"
        "// Re-run evergif to regenerate; CI renders this file as-is.\n"
        "import { chromium } from 'playwright';\n"
        "import { mkdir, rename, writeFile } from 'node:fs/promises';\n"
        "import { dirname } from 'node:path';\n\n"
        f"const config = {json.dumps(config, indent=2)};\n"
        + RUNNER
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--steps", required=True, help='steps separated by ";"')
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--url", default=DEFAULT_URL, help="where the app is served")
    parser.add_argument("--serve", default=None,
                        help='command that starts the app, e.g. "npm run dev"')
    parser.add_argument("--size", default="1280x720", help="viewport, WIDTHxHEIGHT")
    parser.add_argument("--pause", type=int, default=900,
                        help="ms to hold after each step")
    parser.add_argument("--scheme", choices=("light", "dark"), default="light")
    parser.add_argument("--allow-external",
                        action="store_true", help="permit a non-localhost URL")
    parser.add_argument("--out", default=None, help="default: demo/<name>.web.mjs")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    if not NAME_RE.match(args.name):
        print(f"error: --name must be lowercase letters, numbers and hyphens: "
              f"{args.name!r}", file=sys.stderr)
        return 2
    size = SIZE_RE.match(args.size)
    if not size:
        print(f"error: --size must look like 1280x720, got {args.size!r}",
              file=sys.stderr)
        return 2
    problem = check_url(args.url, args.allow_external)
    if problem:
        print(f"refused: {problem}", file=sys.stderr)
        return 2
    if args.serve:
        reason = command_check(args.serve)
        if reason:
            print(f"refused: --serve {args.serve!r}: {reason}", file=sys.stderr)
            return 2
    try:
        steps = parse_steps(args.steps)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not steps:
        print("error: no steps given", file=sys.stderr)
        return 2
    reason = check_steps(steps)
    if reason:
        print(f"refused: {reason}", file=sys.stderr)
        return 2

    script = build(args.name, args.url, steps,
                   (int(size.group(1)), int(size.group(2))),
                   args.pause, args.scheme, args.serve)
    if args.stdout:
        sys.stdout.write(script)
        return 0
    out = Path(args.out) if args.out else Path("demo") / f"{args.name}.web.mjs"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script, encoding="utf-8")
    print(f"wrote {out} ({len(steps)} steps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
