#!/usr/bin/env python3
"""greet - a tiny argparse CLI used as an evergif test fixture."""
from __future__ import annotations

import argparse
import sys

GREETINGS = {"en": "Hello", "fr": "Bonjour", "ja": "Konnichiwa"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="greet", description="Greet someone, politely or loudly.")
    sub = parser.add_subparsers(dest="command", required=True)

    hello = sub.add_parser("hello", help="greet a person")
    hello.add_argument("--name", default="world", help="who to greet")
    hello.add_argument("--lang", choices=sorted(GREETINGS), default="en",
                       help="greeting language")
    hello.add_argument("--shout", action="store_true", help="USE CAPS")

    bye = sub.add_parser("bye", help="say goodbye")
    bye.add_argument("--name", default="world")

    args = parser.parse_args(argv)
    if args.command == "hello":
        line = f"{GREETINGS[args.lang]}, {args.name}!"
        print(line.upper() if args.shout else line)
    else:
        print(f"Goodbye, {args.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
