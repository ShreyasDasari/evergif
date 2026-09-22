#!/usr/bin/env python3
"""Render demo/evergif.tape with vhs (local or Docker) and optimize the GIF.

Usage: render.py [--name NAME | --tape PATH | --all] [--mode auto|local|docker]
                 [--target-mb 2] [--max-mb 5] [--skip-render]

Optimization tries progressively stronger settings until the GIF is under
--target-mb, using gifsicle if present, else ffmpeg (local, or the ffmpeg
inside the vhs Docker image). Exits 1 if the result is still over --max-mb.
Prints a JSON summary on success.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from doctor import VHS_IMAGE, detect

MB = 1024 * 1024
GIFSICLE_LEVELS = [  # (lossy, colors, scale)
    (0, 256, 1.0), (60, 256, 1.0), (100, 128, 1.0), (140, 64, 1.0),
    (160, 64, 0.8), (200, 48, 0.66),
]
FFMPEG_LEVELS = [  # (fps, colors, scale)
    (24, 256, 1.0), (15, 128, 1.0), (12, 64, 1.0), (10, 64, 0.8), (8, 48, 0.66),
]
PASSTHROUGH_ENV = ("PATH", "HOME", "TMPDIR", "TERM", "LANG", "LC_ALL", "SHELL",
                   "USER", "LOGNAME", "VIRTUAL_ENV", "SYSTEMROOT", "XDG_CACHE_HOME")


def scrubbed_env() -> dict:
    """Only what vhs needs; secrets in the caller's env never reach the tape."""
    return {k: os.environ[k] for k in PASSTHROUGH_ENV if k in os.environ}


def docker_cmd(cwd: Path, *args: str, entrypoint: str | None = None,
               env: dict | None = None) -> list[str]:
    cmd = ["docker", "run", "--rm", "-v", f"{cwd}:/vhs", "-w", "/vhs"]
    for key, value in (env or {}).items():
        cmd += ["-e", f"{key}={value}"]
    if entrypoint:
        cmd += ["--entrypoint", entrypoint]
    return cmd + [VHS_IMAGE, *args]


def output_path(tape: Path) -> Path:
    match = re.search(r"^Output\s+(\S+\.gif)\s*$", tape.read_text(encoding="utf-8"),
                      re.MULTILINE)
    if not match:
        sys.exit(f"error: {tape} has no 'Output <file>.gif' line")
    return Path(match.group(1))


def framerate(tape: Path) -> int:
    match = re.search(r"^Set\s+Framerate\s+(\d+)", tape.read_text(encoding="utf-8"),
                      re.MULTILINE)
    return int(match.group(1)) if match else 24


def run_vhs(tape: Path, mode: str, cwd: Path) -> int:
    """Run vhs on a tape. VHS_NO_SANDBOX is required wherever the browser vhs
    drives cannot use its sandbox (containers as root, and some macOS setups)."""
    rel = tape.resolve().relative_to(cwd).as_posix()
    if mode == "local":
        env = scrubbed_env() | {"VHS_NO_SANDBOX": "true"}
        cmd = ["vhs", rel]
    else:
        env = None
        cmd = docker_cmd(cwd, rel, env={"VHS_NO_SANDBOX": "true"})
    print("+ " + " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, cwd=cwd, env=env).returncode


def encode_frames(frames: Path, gif: Path, cwd: Path, fps: int, docker: bool) -> bool:
    """Encode vhs's PNG frames into a GIF ourselves.

    vhs renders frames with a headless browser and then shells out to ffmpeg.
    When that second step fails (notably vhs 0.12 against ffmpeg 9, where vhs
    exits 0 having written nothing), the frames are still perfectly good.
    """
    text = frames / "frame-text-%05d.png"
    cursor = frames / "frame-cursor-%05d.png"
    if not list(frames.glob("frame-text-*.png")):
        return False
    graph = ("[0][1]overlay=shortest=1,split[a][b];"
             "[a]palettegen=max_colors=256:stats_mode=diff[p];"
             "[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle")

    def args(t: str, c: str, out: str) -> list[str]:
        return ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", t,
                "-framerate", str(fps), "-i", c, "-filter_complex", graph,
                "-loop", "0", out]

    if shutil.which("ffmpeg"):
        cmd = args(str(text), str(cursor), str(gif))
    elif docker:
        rel = lambda p: p.relative_to(cwd).as_posix() if p.is_absolute() else p.as_posix()
        cmd = docker_cmd(cwd, *args(rel(text), rel(cursor), rel(gif))[1:],
                         entrypoint="ffmpeg")
    else:
        return False
    print("+ encoding frames with ffmpeg (vhs's own encoder produced nothing)",
          file=sys.stderr)
    return subprocess.run(cmd, cwd=cwd).returncode == 0 and gif.is_file()


def render(tape: Path, mode: str, cwd: Path, gif: Path, docker: bool) -> str:
    """Render the tape, falling back until a GIF exists. Returns the method used."""
    if run_vhs(tape, mode, cwd) == 0 and gif.is_file():
        return mode

    frames = gif.parent / ".evergif-frames"
    patched = gif.parent / ".evergif-frames.tape"
    try:
        shutil.rmtree(frames, ignore_errors=True)
        body = tape.read_text(encoding="utf-8")
        rel_frames = frames.relative_to(cwd).as_posix() if frames.is_absolute() \
            else frames.as_posix()
        patched.write_text(
            re.sub(r"^Output\s+\S+\.gif\s*$", f"Output {rel_frames}/", body,
                   count=1, flags=re.MULTILINE), encoding="utf-8")
        if run_vhs(patched, mode, cwd) == 0 or frames.is_dir():
            if encode_frames(frames, gif, cwd, framerate(tape), docker):
                return f"{mode}+frames"
    finally:
        shutil.rmtree(frames, ignore_errors=True)
        patched.unlink(missing_ok=True)

    if mode == "local" and docker:
        print("local rendering produced no GIF; retrying with Docker",
              file=sys.stderr)
        return render(tape, "docker", cwd, gif, docker=False)
    sys.exit("error: vhs produced no GIF; see the skill's "
             "references/troubleshooting.md")


def gifsicle_pass(src: Path, dst: Path, lossy: int, colors: int, scale: float) -> list[str]:
    cmd = ["gifsicle", "-O3", "--no-comments", "--no-names", "--no-extensions"]
    if lossy:
        cmd.append(f"--lossy={lossy}")
    if colors < 256:
        cmd += ["--colors", str(colors)]
    if scale < 1.0:
        cmd += ["--scale", str(scale)]
    return cmd + [str(src), "-o", str(dst)]


def ffmpeg_pass(src: str, dst: str, fps: int, colors: int, scale: float) -> list[str]:
    scaling = f",scale=iw*{scale}:-1:flags=lanczos" if scale < 1.0 else ""
    graph = (f"fps={fps}{scaling},split[a][b];"
             f"[a]palettegen=max_colors={colors}:stats_mode=diff[p];"
             "[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle")
    return ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", graph, "-loop", "0", dst]


def optimize(gif: Path, cwd: Path, target: int, docker: bool) -> dict:
    original = gif.stat().st_size
    if shutil.which("gifsicle"):
        tool, levels = "gifsicle", GIFSICLE_LEVELS
    elif shutil.which("ffmpeg") or docker:
        tool, levels = "ffmpeg", FFMPEG_LEVELS
    else:
        return {"optimizer": None, "original_bytes": original, "bytes": original}

    best, best_size, used = None, original, None
    with tempfile.TemporaryDirectory(dir=cwd, prefix=".evergif-") as tmp:
        tmp_path = Path(tmp)
        for index, (a, b, scale) in enumerate(levels):
            candidate = tmp_path / f"try{index}.gif"
            if tool == "gifsicle":
                cmd = gifsicle_pass(gif, candidate, a, b, scale)
            elif shutil.which("ffmpeg"):
                cmd = ffmpeg_pass(str(gif), str(candidate), a, b, scale)
            else:  # ffmpeg from the vhs image; paths relative to the mount
                rel = lambda p: p.resolve().relative_to(cwd).as_posix()
                cmd = docker_cmd(cwd, *ffmpeg_pass(rel(gif), rel(candidate), a, b, scale)[1:],
                                 entrypoint="ffmpeg")
            if subprocess.run(cmd, cwd=cwd).returncode != 0 or not candidate.is_file():
                continue
            size = candidate.stat().st_size
            if size < best_size:
                best, best_size, used = candidate, size, (a, b, scale)
            if best_size <= target:
                break
        if best is not None:
            shutil.copyfile(best, gif)
    keys = ("lossy", "colors", "scale") if tool == "gifsicle" else ("fps", "colors", "scale")
    return {"optimizer": tool, "original_bytes": original, "bytes": gif.stat().st_size,
            "settings": dict(zip(keys, used)) if used else "kept original"}


def render_one(tape: Path, args: argparse.Namespace, report: dict, mode: str,
               cwd: Path) -> dict:
    gif = output_path(tape)
    method = mode
    if not args.skip_render:
        gif.parent.mkdir(parents=True, exist_ok=True)
        # Move any existing GIF aside: a stale file must not look like a fresh
        # render, but a failed render must not destroy what the repo already has.
        backup = gif.with_suffix(".gif.previous") if gif.is_file() else None
        if backup:
            gif.replace(backup)
        try:
            method = render(tape, mode, cwd, gif, report["docker"])
        except SystemExit:
            if backup:
                backup.replace(gif)
                print(f"kept the previous {gif}", file=sys.stderr)
            raise
        finally:
            if backup and backup.is_file() and gif.is_file():
                backup.unlink()
    if not gif.is_file():
        sys.exit(f"error: vhs did not produce {gif}")


    result = optimize(gif, cwd, int(args.target_mb * MB), report["docker"])
    result.update({"demo": tape.stem, "tape": tape.as_posix(),
                   "gif": gif.as_posix(), "mode": method,
                   "mb": round(result["bytes"] / MB, 2),
                   "under_target": result["bytes"] <= args.target_mb * MB,
                   "over_limit": result["bytes"] > args.max_mb * MB})
    return result


def demo_tapes(root: Path) -> list[Path]:
    """Every committed demo tape, skipping evergif's own temporary files."""
    return sorted(p for p in (root / "demo").glob("*.tape")
                  if not p.name.startswith("."))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tape", default=None, help="default: demo/<name>.tape")
    parser.add_argument("--name", default=None, help="demo name to render")
    parser.add_argument("--all", action="store_true",
                        help="render every tape in demo/")
    parser.add_argument("--mode", choices=("auto", "local", "docker"), default="auto")
    parser.add_argument("--target-mb", type=float, default=2.0)
    parser.add_argument("--max-mb", type=float, default=5.0)
    parser.add_argument("--skip-render", action="store_true",
                        help="only optimize an existing GIF")
    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    if args.all:
        tapes = demo_tapes(cwd)
        if not tapes:
            sys.exit("error: no tapes in demo/ (run tape.py first)")
    else:
        name = args.name or "evergif"
        tapes = [Path(args.tape) if args.tape else Path("demo") / f"{name}.tape"]
        if not tapes[0].is_file():
            sys.exit(f"error: {tapes[0]} not found (run tape.py first)")

    report = detect()
    mode = report["mode"] if args.mode == "auto" else args.mode
    if mode == "none":
        sys.exit("error: no vhs and no Docker; run doctor.py for install commands")
    if mode == "docker" and not report["docker"]:
        sys.exit("error: --mode docker but Docker is not running")

    results = [render_one(tape, args, report, mode, cwd) for tape in tapes]
    print(json.dumps(results if args.all else results[0], indent=2))
    oversized = [r for r in results if r["over_limit"]]
    for result in oversized:
        print(f"error: {result['gif']} is {result['mb']} MB (limit {args.max_mb} MB); "
              "shorten the tape (fewer commands, shorter --pause, smaller output)",
              file=sys.stderr)
    return 1 if oversized else 0


if __name__ == "__main__":
    sys.exit(main())
