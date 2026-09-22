# Web demos

Recording a web app with Playwright. Read this when a project is a web app, or
when a web recording needs adjusting.

## The two files

`web_tape.py` writes a pair, both committed:

| File | What it is |
|---|---|
| `demo/<name>.web.json` | the URL, viewport, serve command and steps |
| `demo/<name>.web.mjs` | a fixed runner that reads the JSON |

The split is what lets CI record a demo with plain shell, without evergif's
scripts being present in the project. Edit the JSON to tweak a demo; the runner
never needs changing.

The runner pulls Playwright in through `createRequire`, not a bare `import`,
because ESM specifier resolution ignores `NODE_PATH` and globally installed
packages. That one detail is why the same script works whether Playwright is in
the project, installed globally, or baked into a container image.

## Choosing steps

| Step | Use it for |
|---|---|
| `goto /path` | the first step of every demo |
| `wait SELECTOR` | proving the page is ready before recording continues |
| `fill SELECTOR TEXT` | typing into an input |
| `click SELECTOR` | buttons, links, toggles |
| `press KEY` | `Enter`, `Escape`, `Tab` |
| `scroll PIXELS` | revealing content below the fold |
| `pause MS` | holding still so a viewer can read |

Rules that keep a recording honest:

- **Read the markup for selectors.** Guessed selectors fail in CI, where there
  is no one to notice a missing button. Prefer ids and stable class names over
  `div > div:nth-child(2)`.
- **`wait` before you act.** A `click` on an element that has not rendered is
  the most common failure. Follow every `goto` with a `wait`.
- **Show one flow.** Open the page, do the thing, see the result. A demo that
  wanders through four features reads as a recording of someone lost.
- **Seed data in the app, not the demo.** The fixture should already contain a
  couple of rows so the first frame is not an empty state.

## Dev servers

`--serve` is started before recording and stopped after, and the runner polls
the URL until it answers rather than guessing a delay. A stock Vite app works
as is: `--serve "npm run dev" --url http://localhost:5173`.

`goto` waits for `load`, not `networkidle`. Playwright discourages
`networkidle`, and a dev server's HMR socket or any polling request can keep
the network busy indefinitely. Wait on a selector instead, which is what the
step vocabulary is for.

## No Node on the machine

`render_web.py --docker` records with the official Playwright image instead.
The image ships the browsers but not the npm package, so evergif installs the
matching package inside the container into a writable prefix and points
NODE_PATH at it; the browsers in `/ms-playwright` are used as they are.

It needs a **Linux host**: the container reaches your dev server through
`--network host`, which Docker Desktop and Colima do not provide. On macOS,
install Node instead -- evergif fetches Playwright into `~/.cache/evergif`
without touching your project.

Verified on every change to the web scripts by the `web docker` workflow,
which also fails if the recording comes out blank or frozen.

## Determinism

The runner sets `reducedMotion: 'reduce'` and a fixed viewport and colour
scheme, so transitions and responsive breakpoints cannot vary between runs.

What still varies, and will make CI re-render forever:

- clocks and relative timestamps ("2 minutes ago")
- random ids, seeded data generated at startup
- anything fetched from a network service
- animations that never settle (spinners, carousels, looping video)

Freshness is measured on the page's **visible text**, not on pixels: the runner
writes `demo/<name>.transcript.txt` after each step and CI hashes it. A CSS
tweak will not trigger a re-render; a changed label will.

## Sizing and weight

Web video is far heavier than terminal output. The conversion runs at 12 fps
and scales to 1000px wide, which keeps a ten-second demo comfortably under
1 MB. If a GIF comes out too big, cut steps or lower `--fps` before touching
quality; a 30-second web demo is too long regardless of its file size.

A viewport of `1000x620` suits a README. Taller than about 700px and the GIF
gets letterboxed by GitHub's content width.

## Safety

- **localhost only** unless the user explicitly asks for another URL and passes
  `--allow-external`. Recording a live site can capture real customer data.
- **Never record a login.** Steps mentioning passwords, tokens, API keys or
  other credentials are refused outright, and no flag overrides it.
- The `--serve` command goes through the same safety check as recorded shell
  commands, so a demo cannot deploy or delete anything on the way up.
