#!/usr/bin/env python3
"""Write a deterministic, safe vhs tape for 1-3 demo commands.

Usage:
  tape.py --commands "tool --help; tool run sample.txt" [--theme NAME]
          [--path-add DIR] [--out demo/evergif.tape] [--gif demo/evergif.gif]
          [--pause SECONDS] [--stdout]

Every visible command is checked against a safety policy (no destructive,
networked, privileged or secret-revealing commands). Unsafe commands are
rejected with exit code 2.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_THEME = "Catppuccin Mocha"
DEFAULT_NAME = "evergif"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
MAX_COMMANDS = 3


def program(*names: str) -> str:
    """Match NAMES only where a program name can appear (start of a pipeline
    segment, or after xargs/time/nohup), so flags like `--id` or `--top` pass."""
    return (r"(?:^|[|;&(]\s*|\b(?:xargs|time|nohup|nice|command)\s+)"
            rf"(?:\S*/)?(?:{'|'.join(names)})(?=\s|$)")


# (pattern, reason). Matched case-insensitively against each visible command.
UNSAFE = [
    (program("rm", "rmdir", "shred", "truncate", "dd", r"mkfs\S*", "mv", "cp", "ln",
             "chmod", "chown", "kill", "pkill", "killall", "shutdown", "reboot",
             "touch", "mkdir", "tee"),
     "destructive or file-writing command"),
    (program("sudo", "su", "doas"), "privilege escalation"),
    (r">(?!&)|>>", "writes files via redirection"),
    (program("curl", "wget", "ssh", "scp", "sftp", "rsync", "nc", "ncat", "telnet",
             "ftp", "ping", "dig", "nslookup", "open", "xdg-open"),
     "network access"),
    (r"\b(https?|ftp)://|\bgit@", "network URL"),
    (program("git") + r"\s+(push|pull|fetch|clone|reset|clean|checkout|switch|restore|"
     r"rebase|commit|tag|stash|remote|config|credential)\b",
     "git command that changes, fetches, or reveals state"),
    (program("npm", "npx", "pnpm", "yarn", "bun", "pip", "pip3", "pipx", "uv", "poetry",
             "cargo", "go", "gem", "brew", "apt", "apt-get", "yum", "dnf", "pacman",
             "apk", "choco", "scoop", "winget")
     + r"\s+(install|i|add|remove|uninstall|publish|get|update|upgrade|login|exec|"
       r"x|dlx|tool|sync|lock)\b",
     "package install/publish (network)"),
    (program("docker", "podman", "kubectl", "helm", "terraform", "aws", "gcloud", "az",
             "gh", "heroku", "vercel", "flyctl", "firebase", "ansible"),
     "cloud/infra CLI (auth or network)"),
    (program("env", "printenv", "export", "declare", "typeset", "set", "history",
             "whoami", "id", "hostname", "uname", "ifconfig", "ip"),
     "reveals environment, user, or machine info"),
    (r"\$|`", "shell expansion ($VAR, $(...), backticks) can leak secrets"),
    (r"(^|\s|=|/)~|\.env\b|\.ssh\b|\.aws\b|\.gnupg|\.netrc|\.npmrc|\.pypirc|\.kube\b|"
     r"/etc/|/Users/|/home/|/root\b|/var/",
     "reads private or home-directory paths"),
    (r"token|secret|passw|api[_-]?key|credential|private[_-]?key|bearer|auth",
     "mentions credentials or auth"),
    (program("eval", "exec", "source", r"\.")
     + r"|\|\s*(ba|z|da|k|fi)?sh\b|\b(ba|z|da|k|fi)?sh\s+-\w*c|-exec\b"
       r"|\bpython3?\s+-c\b|\bnode\s+-e\b",
     "executes arbitrary code"),
    (program("read", "sleep", "watch", "top", "htop", "less", "more", "man", "vi", "vim",
             "nvim", "nano", "emacs", "tail\\s+-f"),
     "interactive or time-dependent (non-deterministic)"),
    (program("date", "uptime", "uuidgen", "shuf", "ps", "df", "du", "ls\\s+-\\S*l\\S*"),
     "non-deterministic output"),
]


def split_commands(text: str) -> list[str]:
    """Split on ';' and newlines, but not inside quotes: a command may legally
    contain a quoted semicolon (`tool --commands "a; b"`)."""
    parts, current, quote = [], [], ""
    for char in text:
        if quote:
            quote = "" if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char in ";\n":
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return [part.strip() for part in parts if part.strip()]


def check(command: str) -> str | None:
    """Return the reason a command is unsafe, or None if it is allowed."""
    for pattern, reason in UNSAFE:
        if re.search(pattern, command, re.IGNORECASE):
            return reason
    return None


def quote(text: str) -> str:
    """Quote a string for a vhs Type command (vhs strings have no escapes)."""
    for mark in ('"', "'", "`"):
        if mark not in text:
            return f"{mark}{text}{mark}"
    raise ValueError(f"cannot quote for vhs (uses \", ' and `): {text}")


def build(commands: list[str], theme: str, gif: str, path_add: list[str],
          pause: float, height: int) -> str:
    prelude = "PS1='> ' PROMPT_COMMAND='' HISTFILE=/dev/null"
    if path_add:
        dirs = ":".join(f"$PWD/{d.strip('/')}" for d in path_add)
        prelude = f'PATH="{dirs}:$PATH" {prelude}'
    lines = [
        "# Generated by evergif (https://github.com/ShreyasDasari/evergif).",
        "# Re-run evergif to regenerate; CI renders this file as-is.",
        f"Output {gif}",
        "",
        'Set Shell "bash"',
        "Set FontSize 18",
        "Set Width 1100",
        f"Set Height {height}",
        "Set Padding 24",
        f"Set Theme {quote(theme)}",
        "Set TypingSpeed 45ms",
        "Set Framerate 24",
        "Set CursorBlink false",
        'Env BASH_SILENCE_DEPRECATION_WARNING "1"',
        "",
        "Hide",
        f"Type {quote(f'export {prelude} && clear')}",
        "Enter",
        "Wait@10s",
        "Show",
    ]
    for index, command in enumerate(commands):
        if index:
            lines += ["", "Hide", 'Type "clear"', "Enter", "Wait@10s", "Show"]
        lines += [
            "",
            f"Type {quote(command)}",
            "Sleep 400ms",
            "Enter",
            "Wait@15s",
            f"Sleep {pause:g}s",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--commands", required=True,
                        help='1-3 commands separated by ";"')
    parser.add_argument("--theme", default=DEFAULT_THEME)
    parser.add_argument("--path-add", action="append", default=[],
                        metavar="DIR", help="project dir to prepend to PATH (repeatable)")
    parser.add_argument("--name", default=DEFAULT_NAME,
                        help="demo name; a README may hold several demos")
    parser.add_argument("--out", default=None, help="default: demo/<name>.tape")
    parser.add_argument("--gif", default=None, help="default: demo/<name>.gif")
    parser.add_argument("--height", type=int, default=500,
                        help="window height in px; about 22px per output row")
    parser.add_argument("--pause", type=float, default=3.0,
                        help="seconds to hold each command's output")
    parser.add_argument("--stdout", action="store_true",
                        help="print the tape instead of writing it")
    args = parser.parse_args()

    if not NAME_RE.match(args.name):
        print(f"error: --name must be lowercase letters, numbers and hyphens: "
              f"{args.name!r}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else Path("demo") / f"{args.name}.tape"
    gif = args.gif or (Path("demo") / f"{args.name}.gif").as_posix()

    commands = split_commands(args.commands)
    if not 1 <= len(commands) <= MAX_COMMANDS:
        print(f"error: need 1-{MAX_COMMANDS} commands, got {len(commands)}",
              file=sys.stderr)
        return 2
    for path in args.path_add:
        if check(path) or path.startswith("/") or ".." in path:
            print(f"error: --path-add must be a relative project dir: {path}",
                  file=sys.stderr)
            return 2
    rejected = [(c, check(c)) for c in commands if check(c)]
    for command, reason in rejected:
        print(f"refused: {command!r}: {reason}", file=sys.stderr)
    if rejected:
        print("pick a read-only, offline command (--help, --version, --dry-run, "
              "or sample data in the repo)", file=sys.stderr)
        return 2

    try:
        tape = build(commands, args.theme, gif, args.path_add, args.pause,
                     args.height)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.stdout:
        sys.stdout.write(tape)
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tape, encoding="utf-8")
    print(f"wrote {out} ({len(commands)} command{'s' * (len(commands) > 1)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
