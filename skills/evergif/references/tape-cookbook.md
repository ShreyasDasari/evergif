# Tape cookbook

What `tape.py` generates, how to adjust it, and which commands make a good
demo. Read this when the default tape needs changing or when you are unsure
which commands to record.

## What a generated tape looks like

```
Output demo/evergif.gif

Set Shell "bash"            # a predictable shell, not the user's zsh setup
Set FontSize 18             # readable in a GitHub README at 800px wide
Set Width 1200 / Height 500  # height is sized to the tallest output
Set Theme "Catppuccin Mocha"
Set TypingSpeed 45ms
Set Framerate 24
Set CursorBlink false       # a blinking cursor costs frames and bytes

Hide                        # setup nobody should see
Type "export PS1='> ' PROMPT_COMMAND='' HISTFILE=/dev/null && clear"
Enter
Wait@10s
Show

Type "tool --help"          # one visible command
Sleep 400ms                 # a beat before Enter reads as intentional
Enter
Wait@15s                    # wait for the prompt, not a guessed duration
Sleep 3s                    # hold the output long enough to read
```

The hidden prelude is what makes renders reproducible: a fixed prompt, no
history file, no `PROMPT_COMMAND` (which many shell themes use for timestamps
or git status), and a cleared screen.

`Wait` blocks until the prompt returns, so a slow machine produces the same
frames as a fast one; only the render takes longer. The `@15s` timeout makes a
hung command fail the render instead of silently recording nothing.

## Choosing commands

| Project type | Good opener | Good payoff |
|---|---|---|
| argparse/click/typer | `tool --help` | `tool <verb> --flag sample.txt` |
| Node CLI | `npx --no-install tool --help` or `node cli.js --help` | a run against a fixture in the repo |
| Go / Rust | `tool --help` (build first) | `tool run testdata/example.json` |
| Shell script | `./tool.sh --help` | `./tool.sh list fixture.txt` |
| TUI | skip `--help` | one screen of the TUI, then `q` to quit |

Rules of thumb:

- **Two or three commands beat one.** Show what it is, then show it working.
- **Output under about 20 lines.** Each row is about 21px, and the window
  height is set from the tallest output. Longer output scrolls off screen.
- **Use fixtures already in the repo** (`testdata/`, `examples/`, `fixtures/`).
  Don't create sample files just for the demo unless the user asks.
- **Never record what you cannot re-run.** The CI workflow re-renders this tape
  on a clean Ubuntu runner: if a command needs a database, a token, or a file
  that isn't committed, it will fail there.

## Adjusting the defaults

| Want | Change |
|---|---|
| A different palette | `--theme "Dracula"` (any name from `vhs themes`) |
| More reading time | `--pause 4.5` |
| A tool that isn't on PATH | `--path-add bin` (prepends `$PWD/bin`) |
| A window that fits the output | `--height` = `rows x 21 + 90` for the tallest output |
| A different output path | `--out`, `--gif` |

Hand-edits to `demo/evergif.tape` survive until evergif is re-run with
`--commands`, which rewrites the file. Tell the user that.

## TUI demos

`tape.py` refuses interactive programs by default (they are non-deterministic).
For a TUI, write the tape by hand from the generated one:

```
Type "mytui"
Enter
Sleep 2s
Down@500ms 3        # keystrokes with a delay between repeats
Enter
Sleep 2s
Type "q"            # always quit, or the render hangs until the timeout
```

Use `Sleep`, not `Wait`, inside a TUI: the shell prompt never comes back until
it exits.

## Commands that are always refused

`tape.py` rejects these, and no flag overrides it: deletes and writes
(`rm`, `mv`, `>`), privilege escalation (`sudo`), network access (`curl`,
`git push`, package installs), cloud CLIs (`docker`, `aws`, `gh`), environment
and identity (`env`, `printenv`, `whoami`), shell expansion (`$VAR`, backticks),
private paths (`~`, `.env`, `.ssh`, `/etc/`), credential words, and
non-deterministic commands (`date`, `ps`, `ls -l`).

If a refusal blocks the only interesting command, that is a signal the demo
would be unsafe or unreproducible. Pick a different command, or ask the user.
