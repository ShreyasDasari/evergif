#!/usr/bin/env python3
"""Insert or update the evergif GIF embed in a README.

Usage: embed.py --alt "What the GIF shows" [--readme README.md]
                [--gif demo/evergif.gif] [--dry-run]

The embed lives between <!-- evergif:start --> and <!-- evergif:end -->.
If the markers exist, only the text between them is replaced. Otherwise the
block is inserted after the README's title and first paragraph (or at the top
if there is no title). Running it twice never duplicates the block.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

START = "<!-- evergif:start -->"
END = "<!-- evergif:end -->"
GENERIC_ALT = {"demo", "gif", "demo gif", "screenshot", "animation", "image", "evergif"}


def block(alt: str, src: str) -> str:
    alt = " ".join(alt.split()).replace("[", "(").replace("]", ")")
    return f"{START}\n![{alt}]({src})\n{END}"


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


def update(text: str, new_block: str) -> tuple[str, str]:
    starts = marker_positions(text, START)
    ends = marker_positions(text, END)
    if len(starts) != len(ends) or len(starts) > 1:
        raise ValueError(f"found {len(starts)} start and {len(ends)} end markers "
                         "outside code blocks; expected exactly one pair "
                         "(fix the README by hand)")
    newline = "\r\n" if "\r\n" in text else "\n"
    if starts:
        if ends[0].start() < starts[0].start():
            raise ValueError("end marker appears before the start marker")
        return (text[:starts[0].start()] + new_block.replace("\n", newline)
                + text[ends[0].end():]), "updated"
    lines = text.splitlines()
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
    parser.add_argument("--gif", default="demo/evergif.gif")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the block and the action, change nothing")
    args = parser.parse_args()

    if len(args.alt.strip()) < 15 or args.alt.strip().lower() in GENERIC_ALT:
        print("error: --alt must describe what the GIF shows (at least 15 characters)",
              file=sys.stderr)
        return 2
    readme, gif = Path(args.readme), Path(args.gif)
    src = Path(os.path.relpath(gif, readme.parent)).as_posix()
    new_block = block(args.alt, src)
    if readme.is_file():
        with open(readme, encoding="utf-8", newline="") as fh:
            text = fh.read()
    else:
        text = f"# {Path.cwd().name}\n"
    try:
        updated, action = update(text, new_block)
    except ValueError as exc:
        print(f"error: {readme}: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(new_block)
        print(f"(dry run: would have {action} this block in {readme})")
        return 0
    if updated == text:
        print(f"{readme}: embed already up to date")
        return 0
    with open(readme, "w", encoding="utf-8", newline="") as fh:
        fh.write(updated)
    print(f"{readme}: {action} evergif embed ({src})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
