#!/usr/bin/env bash
# todo - a read-only todo list reader used as an evergif test fixture.
set -euo pipefail

FILE="${TODO_FILE:-tasks.txt}"

usage() {
  cat <<'EOF'
todo - read a plain-text todo list

Usage:
  todo.sh list [--done|--open]   show tasks (all, done, or open)
  todo.sh stats                  count tasks by state
  todo.sh --help                 show this help

Tasks live in tasks.txt, one per line: "[x] done" or "[ ] still open".
EOF
}

list_tasks() {
  local filter="${1:-all}" n=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$filter:$line" in
      done:'[ ]'*|open:'[x]'*) continue ;;
    esac
    n=$((n + 1))
    printf '  %2d. %s\n' "$n" "$line"
  done < "$FILE"
  printf '\n%d task(s) shown from %s\n' "$n" "$FILE"
}

case "${1:---help}" in
  list)
    case "${2:-}" in
      --done) list_tasks done ;;
      --open) list_tasks open ;;
      *) list_tasks all ;;
    esac
    ;;
  stats)
    done_count=$(grep -c '^\[x\]' "$FILE" || true)
    open_count=$(grep -c '^\[ \]' "$FILE" || true)
    printf 'done: %s\nopen: %s\ntotal: %s\n' \
      "$done_count" "$open_count" "$((done_count + open_count))"
    ;;
  -h|--help) usage ;;
  *)
    printf 'todo: unknown command %s\n\n' "$1" >&2
    usage >&2
    exit 1
    ;;
esac
