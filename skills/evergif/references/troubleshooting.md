# Troubleshooting

## doctor.py says `mode: none`

Neither vhs nor Docker is usable. `doctor.py` prints install commands for the
detected OS. Show them to the user and stop; don't install system packages on
their behalf.

macOS is one line: `brew install vhs gifsicle` (vhs brings ttyd and ffmpeg).

## The render fails

| Symptom | Cause | Fix |
|---|---|---|
| `Error: unknown theme` | theme name typo | `vhs themes` lists valid names |
| Hangs, then a `Wait` timeout | the command never returned to the prompt (interactive, or waiting on input) | pick a non-interactive command, or write a TUI tape by hand (see the cookbook) |
| `command not found` in the GIF | the tool isn't on PATH inside the tape's shell | `--path-add bin`, or record the explicit invocation (`python3 cli.py`) |
| Blank or black GIF | ttyd could not start | check `ttyd --version`; on Linux the Docker fallback avoids it |
| Fonts look wrong | the font isn't installed | stick to the default (JetBrains Mono ships in the Docker image and in vhs-action) |

## vhs exits 0 but writes no GIF

vhs renders frames with a headless browser, then shells out to ffmpeg. Either
half can fail while vhs still exits 0:

- **The browser will not start** (`could not start browser: browser exited
  unexpectedly`). vhs needs its sandbox disabled in containers and on some
  macOS setups. `render.py` always sets `VHS_NO_SANDBOX=true`, which fixes it.
- **The encode fails silently.** vhs 0.12 passes options that ffmpeg 9 rejects,
  and swallows the error. `render.py` detects the missing GIF, re-runs the tape
  with vhs's `Output frames/` mode, and encodes the PNG frames itself. You will
  see `encoding frames with ffmpeg (vhs's own encoder produced nothing)` and a
  `mode` of `local+frames` in the JSON summary. The result is equivalent.

Because the encode can happen in either place, evergif's tapes do not use
`Set WindowBar` or `Set BorderRadius`: those are applied during vhs's own
ffmpeg stage, so a tape that used them would look different depending on which
encoder ran.

## Docker fallback caveats

`render.py` mounts the project at `/vhs` inside `ghcr.io/charmbracelet/vhs`.
Everything the demo runs must exist **inside the container**:

- A bash script fixture works.
- A Python or Node CLI needs that runtime in the image. If `python3` is not
  there, the recorded command fails on camera. Check with
  `docker run --rm --entrypoint python3 ghcr.io/charmbracelet/vhs --version`.
  If it is missing, install vhs locally instead.
- On Linux, files written by the container are owned by root. Fix with
  `sudo chown "$USER" demo/evergif.gif`, or install vhs locally.
- The container has no access to the host's environment variables, which is
  a safety feature, not a bug.
- **Known failure: Colima on Apple Silicon.** The image's chromium captures
  zero frames there and vhs still exits 0, with no error on either stream.
  `--shm-size`, `--ipc=host` and `--cap-add=SYS_ADMIN` make no difference.
  `render.py` fails loudly, keeps your previous GIF, and points here. Install
  vhs locally (`brew install vhs`) or use Docker Desktop instead.

## The GIF renders but looks wrong

Re-read the tape before touching the encoder. Common causes: output scrolled
off (window too short), a shell banner leaked into frame (the hidden prelude
was edited), or a prompt from the user's own `PROMPT_COMMAND` (only happens if
`Set Shell` was changed away from bash).

## The README embed

- `error: found 2 start and 1 end markers` — the README has a broken marker
  pair. Fix it by hand; `embed.py` will not guess.
- The block landed in an odd place — move it anywhere you like. `embed.py`
  updates it where it is; placement is only chosen on first insert. A new named
  demo is added after the last existing evergif block, so demos stay together.
- `error: found 1 start and 0 end markers for demo 'install'` — the named pair
  is incomplete. Named demos use `<!-- evergif:start:install -->` and
  `<!-- evergif:end:install -->`; the default demo uses the bare markers.
- Relative path — the `src` is computed relative to the README, so a README in
  `docs/` gets `../demo/evergif.gif`.

## CI

- **No PR appears after a real change.** Enable Settings → Actions → General →
  "Allow GitHub Actions to create and approve pull requests".
- **A PR appears on every run.** A recorded command prints something that
  varies between runs (a timestamp, a duration, an absolute path, an unordered
  listing). The workflow hashes command output, so anything non-deterministic
  looks like a change every time. Re-run evergif with a stable command.
- **The first run after adding the workflow opens one PR.** It creates
  `demo/evergif.lock`. Merge it; later runs stay quiet until the CLI changes.
- **`demo/<name>.lock` is not optional.** It is the record of what that demo
  shows. Commit it alongside the GIF.
- **A demo re-renders when a different demo changed.** Each demo has its own
  lock, so this means both demos really do show the changed output. Narrow one
  of them to commands that do not overlap.
- **The workflow fails at the setup step.** `--setup` must make the recorded
  commands runnable on a clean Ubuntu runner. Re-run `ci.py` with the right
  setup lines.

## Web demos

| Symptom | Cause | Fix |
|---|---|---|
| `MODULE_NOT_FOUND: playwright` | no Node, or a project whose Playwright is not installed | evergif fetches it into `~/.cache/evergif`; if Node itself is missing, install it or use `--docker` on Linux |
| `<url> did not answer within 90s` | the `serve` command never came up | run it by hand and check the port matches `--url` |
| `waitForSelector` times out | the selector is wrong, or the element renders later | read the markup for the real selector, and `wait` before you act |
| `--docker` cannot reach the app | Docker Desktop and Colima do not support `--network host` | use a Linux host, or install Node |

## Windows

Symlinked skill directories need `git clone -c core.symlinks=true` plus
Developer Mode or an elevated shell. Without them, copy the skill folder
instead, or install with `npx skills add ... --copy`.

vhs runs natively on Windows (`scoop install vhs`), but tapes generated by
evergif use `Set Shell "bash"`. On Windows, run evergif from WSL or Git Bash.
