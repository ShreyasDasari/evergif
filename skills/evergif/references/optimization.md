# Optimization

`render.py` renders the tape, then shrinks the GIF until it fits. Read this
when a GIF comes out too big or looks wrong after optimization.

## Budget

| Threshold | Meaning |
|---|---|
| 2 MB | Target. `render.py` stops optimizing once it is under this. |
| 5 MB | Hard limit. Over this, `render.py` exits 1 and you must shorten the demo. |

GitHub serves READMEs to people on phones; a 10 MB GIF is a broken README even
though it renders.

## The ladder

Each pass runs on the original render, not on the previous pass, so quality
degrades once rather than cumulatively. The first pass that lands under the
target wins; otherwise the smallest result is kept.

**With gifsicle** (preferred):

| Pass | Settings |
|---|---|
| 1 | `-O3` only (lossless) |
| 2 | `--lossy=60` |
| 3 | `--lossy=100 --colors 128` |
| 4 | `--lossy=140 --colors 64` |
| 5 | `--lossy=160 --colors 64 --scale 0.8` |
| 6 | `--lossy=200 --colors 48 --scale 0.66` |

`--no-comments --no-names --no-extensions` strips metadata, which also makes
renders byte-comparable.

**Without gifsicle** (ffmpeg, local or from the vhs Docker image): the same
idea with a generated palette, dropping framerate first (24 → 15 → 12 → 10 → 8),
then colors, then scale. `stats_mode=diff` builds the palette from what changes
between frames, which suits terminal output; `diff_mode=rectangle` only redraws
changed regions.

ffmpeg output is typically 20–40% larger than gifsicle's for terminal GIFs.
Installing gifsicle is worth it: `brew install gifsicle`, `apt install gifsicle`.

## When it is still too big

Fix the recording, not the encoder. In order of effect:

1. **Fewer commands.** Three short commands beat two long ones; one long
   scrolling command is the usual culprit.
2. **Shorter pauses.** `--pause 2` instead of the default 3 saves a second of
   frames per command.
3. **Less output.** Pick a command whose output is under 20 lines.
4. **Lower the framerate.** `Set Framerate 15` in the tape. Terminal output has
   few moving pixels; 15 fps still reads as smooth.
5. **Smaller window.** `Set Width 1000` / `Set Height 560`.

Typing speed is not a good lever: faster typing looks unnatural and saves
little, because the typed characters change only a few pixels per frame.

## Checking the result

```bash
ls -lh demo/evergif.gif
gifsicle --info demo/evergif.gif | head -3   # frame count, size, loop
```

Look at the GIF before committing it: optimization can turn readable text into
mush at `--colors 48`, and a passing size check will not tell you that.
