#!/usr/bin/env python3
"""Insert or update the evergif GIF embed in a README.

Usage: embed.py --alt "What the GIF shows" [--name NAME] [--readme README.md]
                [--gif PATH] [--dry-run]

The default demo lives between <!-- evergif:start --> and <!-- evergif:end -->.
Any other demo uses named markers, e.g. <!-- evergif:start:install -->, so one
README can hold several demos. If the markers exist, only the text between them
is replaced; otherwise the block is added after the last existing evergif block,
or after the title. Running it twice never duplicates a block.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_NAME = "evergif"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
# The default demo keeps v0.1's bare markers; extra demos are named.
ANY_END = re.compile(r"<!-- evergif:end(?::[a-z0-9-]+)? -->")


def markers(name: str) -> tuple[str, str]:
    suffix = "" if name == DEFAULT_NAME else f":{name}"
    return (f"<!-- evergif:start{suffix} -->", f"<!-- evergif:end{suffix} -->")


GENERIC_ALT = {"demo", "gif", "demo gif", "screenshot", "animation", "image", "evergif"}


def weak_alt(alt: str) -> bool:
    """True when alt text says nothing a screen reader user could use."""
    cleaned = " ".join(alt.split())
    return len(cleaned) < 15 or cleaned.lower().rstrip(".") in GENERIC_ALT


def block(alt: str, src: str, name: str) -> str:
    start, end = markers(name)
    alt = " ".join(alt.split()).replace("[", "(").replace("]", ")")
    return f"{start}\n![{alt}]({src})\n{end}"


def insertion_index(lines: list[str]) -> int:
    """Line index after the H1 title and the paragraph (tagline/badges) under it."""
    title = next((i for i, line in enumerate(lines)
                  if line.startswith("# ") or line.startswith("<h1")), None)
    if title is None:
        return 0
    i = title + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and not lines[i].startswith(("#", "```", "|")):
        while i < len(lines) and lines[i].strip():
            i += 1
    return i


def fenced_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges inside ``` fences. A README that documents the markers
    (this one does) must not have that prose mistaken for a real embed."""
    fences = [m.start() for m in re.finditer(r"^[ \t]*```", text, re.MULTILINE)]
    return [(fences[i], fences[i + 1]) for i in range(0, len(fences) - 1, 2)]


def marker_positions(text: str, marker: str) -> list[re.Match]:
    spans = fenced_spans(text)
    return [m for m in re.finditer(re.escape(marker), text)
            if not any(lo <= m.start() < hi for lo, hi in spans)]


def last_block_line(text: str) -> int | None:
    """Line after the last evergif block of any name, so demos stay together."""
    spans = fenced_spans(text)
    ends = [m for m in ANY_END.finditer(text)
            if not any(lo <= m.start() < hi for lo, hi in spans)]
    if not ends:
        return None
    return text[:ends[-1].end()].count("\n") + 1


def update(text: str, new_block: str, name: str) -> tuple[str, str]:
    start_marker, end_marker = markers(name)
    starts = marker_positions(text, start_marker)
    ends = marker_positions(text, end_marker)
    if len(starts) != len(ends) or len(starts) > 1:
        raise ValueError(f"found {len(starts)} start and {len(ends)} end markers "
                         f"for demo {name!r} outside code blocks; expected exactly "
                         "one pair (fix the README by hand)")
    newline = "\r\n" if "\r\n" in text else "\n"
    if starts:
        if ends[0].start() < starts[0].start():
            raise ValueError("end marker appears before the start marker")
        return (text[:starts[0].start()] + new_block.replace("\n", newline)
                + text[ends[0].end():]), "updated"
    lines = text.splitlines()
    index = last_block_line(text)
    if index is None:
        index = insertion_index(lines)
    before = [""] if index and lines[index - 1].strip() else []
    after = [""] if index < len(lines) and lines[index].strip() else []
    lines[index:index] = before + new_block.split("\n") + after
    result = newline.join(lines)
    if text.endswith(("\n", "\r\n")) or not text:
        result += newline
    return result, "inserted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--alt", required=True, help="real alt text describing the GIF")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--name", default=DEFAULT_NAME,
                        help="demo name; a README may hold several demos")
    parser.add_argument("--gif", default=None, help="default: demo/<name>.gif")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the block and the action, change nothing")
    args = parser.parse_args()

    if weak_alt(args.alt):
        print("error: --alt must describe what the GIF shows (at least 15 characters)",
              file=sys.stderr)
        return 2
    if not NAME_RE.match(args.name):
        print(f"error: --name must be lowercase letters, numbers and hyphens: "
              f"{args.name!r}", file=sys.stderr)
        return 2
    readme = Path(args.readme)
    gif = Path(args.gif) if args.gif else Path("demo") / f"{args.name}.gif"
    src = Path(os.path.relpath(gif, readme.parent)).as_posix()
    new_block = block(args.alt, src, args.name)
    if readme.is_file():
        with open(readme, encoding="utf-8", newline="") as fh:
            text = fh.read()
    else:
        text = f"# {Path.cwd().name}\n"
    try:
        updated, action = update(text, new_block, args.name)
    except ValueError as exc:
        print(f"error: {readme}: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(new_block)
        print(f"(dry run: would have {action} this block in {readme})")
        return 0
    if updated == text:
        print(f"{readme}: embed '{args.name}' already up to date")
        return 0
    with open(readme, "w", encoding="utf-8", newline="") as fh:
        fh.write(updated)
    print(f"{readme}: {action} evergif embed '{args.name}' ({src})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
