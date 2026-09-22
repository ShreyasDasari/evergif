---
name: evergif
description: Generate a reproducible terminal demo GIF for a CLI or TUI project's README and keep it fresh in CI. Inspects the project, writes a deterministic vhs tape (demo/evergif.tape), renders and optimizes demo/evergif.gif, and embeds it in README.md between evergif markers. Use when the user says "run evergif", "/evergif", "add a demo gif to my README", "record a terminal demo", "make a GIF of my CLI", "update the README gif", or wants their README demo to stop going stale.
license: MIT
compatibility: Requires Python 3.10+ and either vhs (with ttyd and ffmpeg) or Docker. CLI/TUI projects only.
metadata:
  version: "0.1.0"
  homepage: https://github.com/ShreyasDasari/evergif
---

# evergif

Your README demo that never goes stale. This skill turns a CLI/TUI project
into `demo/evergif.tape` → `demo/evergif.gif` → a README embed, and
optionally a CI workflow that re-renders it.

Everything below is plain shell. `SKILL_DIR` means the directory containing
this file; run every command from the **target project's root**.

## Options

All optional. Parse them from the user's request, in any wording.

| Option | Meaning | Default |
|---|---|---|
| `--commands "a; b"` | Exact commands to record (1–3, `;`-separated) | You pick them in step 2 |
| `--name NAME` | Which demo to write; a README can hold several | `evergif` |
| `--theme NAME` | Any theme from `vhs themes` | `Catppuccin Mocha` |
| `--ci` | Also add the GitHub workflows (freshness + cloud rendering) | off |

**Several demos in one README.** Each demo is a name: `demo/<name>.tape`,
`demo/<name>.gif`, and its own marker pair. Use one when the user asks for a
demo of a particular feature ("add a gif showing the install flow" →
`--name install`), and keep the default `evergif` for the main demo. Pass
`--name` to steps 3 and 5. Never overwrite an existing demo with unrelated
content: list `demo/*.tape` first and pick a new name if none fits.

## Workflow

### 1. Check the toolchain

```bash
python3 "$SKILL_DIR/scripts/doctor.py"
```

It prints JSON with `mode`: `local` (vhs installed), `docker` (falls back to
`ghcr.io/charmbracelet/vhs`), or `none`. On `none`, stop and show the user the
install commands it printed. Do not install system packages yourself.

### 2. Pick the commands

Skip this step if the user passed `--commands`.

```bash
python3 "$SKILL_DIR/scripts/inspect_project.py" .
```

It reports the README pitch, declared entry points, how to invoke each one,
their `--help` output, and a `deterministic` flag. Choose the **1–3 most
compelling** commands, ideally one that shows what the tool is followed by one
or two that show it doing its core job. Every command must be:

- **Safe**: read-only. No deletes, installs, writes outside the project, `git push`, or `sudo`.
- **Offline**: no network, no auth, no API keys.
- **Secret-free**: never print env vars, dotfiles, tokens, or paths under `~`.
- **Deterministic**: the same output every run, with no timestamps, random values, or spinners that depend on timing. Prefer `--help`, `--version`, `--dry-run`, or runs against sample data already in the repo.
- **Short**: output fits in about 20 lines. Pipe through `head -n 20` only if unavoidable.

If nothing qualifies, say so and ask the user which commands to record. Don't
invent sample data outside `demo/`. See
[references/tape-cookbook.md](references/tape-cookbook.md) for good patterns
per project type.

### 3. Write the tape

```bash
python3 "$SKILL_DIR/scripts/tape.py" --commands "cmd one; cmd two" \
  --height PIXELS [--name NAME] [--theme "NAME"] [--path-add DIR]
```

This writes `demo/<name>.tape`. Set `--height` from the **tallest** output you
are recording: `rows x 21 + 90`, where `rows` counts the command line plus its
output lines (step 2 reports them). A 10-line help output is about 300; the
default 500 leaves dead space under short output, which looks broken in a
README.

Use `--path-add DIR` when the tool is only runnable from a project folder (for
example `--path-add bin`). The script rejects unsafe commands. If it refuses
one, pick a different command; never work around the check.

### 4. Render and optimize

```bash
python3 "$SKILL_DIR/scripts/render.py" [--name NAME]   # or --all for every demo
```

It renders with local vhs or Docker (per step 1), then optimizes to under 2 MB
when possible and fails if the GIF is over 5 MB. If rendering fails or the
GIF looks wrong (errors on screen, cut-off output), fix the tape and re-run.
See [references/optimization.md](references/optimization.md) and
[references/troubleshooting.md](references/troubleshooting.md).

### 5. Embed in the README

```bash
python3 "$SKILL_DIR/scripts/embed.py" --alt "ALT TEXT" [--name NAME]
```

Write real alt text that describes what the GIF shows, e.g. `Terminal demo:
greet --help lists the hello and bye subcommands, then greet hello --name Ada
prints a greeting`. It inserts or replaces the block between `<!-- evergif:start -->` and
`<!-- evergif:end -->` (or `:NAME` markers for a named demo). Re-running
updates that block in place and never duplicates it.

### 6. CI freshness (only with `--ci`)

```bash
python3 "$SKILL_DIR/scripts/ci.py" --setup "SETUP COMMAND"
```

`--setup` is whatever makes the recorded commands runnable on a clean Ubuntu
runner (e.g. `pip install -e .`, `npm ci`, `go build ./...`). Repeat the flag
for several steps, or omit it if nothing is needed.

This writes two workflows: `evergif.yml` keeps the GIFs fresh, and
`evergif-render.yml` renders them in CI so contributors without vhs can edit a
tape, open a PR, and get the GIF rendered and pushed back for them
(`--no-cloud` skips the second one).

The workflow covers every demo in `demo/`. It re-runs each demo's recorded
commands, hashes the output against `demo/<name>.lock`, and re-renders and
opens one PR for only the demos whose output changed.

Tell the user to enable **Settings → Actions → General → Allow GitHub Actions
to create and approve pull requests**, and that the first run creates the lock
files, so it opens one PR.

### 7. Report

Tell the user the chosen commands, the GIF path and size, and the README
change. Suggest committing `demo/<name>.tape`, `demo/<name>.gif`, and
`README.md` (plus the workflow and `demo/<name>.lock`, if added). Don't commit
unless asked.
