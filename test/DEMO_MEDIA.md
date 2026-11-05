# Documentation demos and recordings

The website in `docs/demo/` and the GIFs in `docs/media/` are synthetic,
illustrative demonstrations. They are not recordings of Virtuoso. Their
geometry, captions, and states come from `docs/demo/app.js`.

## Preview and regenerate

The interactive site works by opening `docs/demo/index.html` directly. To
preview over HTTP, run `python -m http.server 8000 --bind 127.0.0.1` from the
repository root and open `http://127.0.0.1:8000/docs/demo/`.

For capture and browser checks, use a virtual environment:

```sh
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -r test/demo-requirements.txt
# On Linux/macOS, use .venv/bin/python instead.
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe tools/build_guide.py
.venv/Scripts/python.exe tools/render_demos.py
.venv/Scripts/python.exe test/check_demo.py
.venv/Scripts/python.exe test/check_demo_media.py
```

If an installed Microsoft Edge browser is preferred, pass `--channel msedge`
to the capture and check scripts. This avoids installing Playwright Chromium.
`render_demos.py --only copy,contour` regenerates selected scenes. A full run
also creates `overview.gif` as a synchronized 2×2 grid of Dimension picker,
Path width, Measurement, and Copy (01, 02, 04, 07). Regenerating those four
scenes together also rebuilds the grid.

The exporter samples the same event timeline as the interactive player at ten
frames per second, then assembles the frames with a three-second pause after
each complete demonstration. The README uses one composited GIF: exactly one
panel animates while the others hold their completed results, with a one-second
all-still gap between panels, including the last-to-first transition. Its
schedule is saved under `artifacts/demo-frames/overview/schedule.json` for checks.
Run `test/check_demo_media.py` after a full render to verify loop delays and that
every inactive panel stays pixel-identical throughout the decoded README GIF.

Pointer arrival precedes hover highlights; key presses and digit-by-digit
input are captured at their scheduled times. Digits are 260 ms apart. Command
keys and clicks leave at least 1.2 seconds for the result to be read, at 1× speed.
Every scene begins with its native command and ends by moving the pointer back
to empty space within the final step; the action bar then reads **Done.**
Cursor balloons use `vbnModeText`, `vbnDisplayText`, and `vbnPositionHint` labels
from the plugin. Explanatory text belongs in the bottom bar.

Intermediate PNGs stay under ignored
`artifacts/demo-frames/`. Only the reviewed GIFs are tracked in `docs/media/`.
`tools/build_guide.py` generates the browser guide from the canonical Markdown
document; regenerate it when the Markdown changes.

The demo rounds decimal inputs to four places before playback. Browser checks
verify this rounding, native command order, balloon labels, hover timing,
individual input characters, key-down and key-up states, playback speed,
three-second loops, and auto-replay after confirmed inputs. This rounding is
specific to the illustrative website.

See [GitHub Pages deployment](../docs/PUBLISHING.md) for building and publishing
the reviewed site and animations.

## Recording an actual Virtuoso session

Use the dedicated test library and environment described in [README.md](README.md).
Prepare fresh synthetic geometry with the testbench scripts. Set a neutral
test-cell name and frame the canvas so usernames, hostnames, paths, clocks,
production designs, and CIW transcripts are excluded from every frame.

For each tool, record a short sequence:

| Tool | Sequence |
| --- | --- |
| Picking | S → click lower edge of separate rectangle → J → pick length or spacing → inspect stretch preview → confirm |
| Path / Wire | P → click wire → pull segment → J → enter width → confirm |
| Rectangle | R → first corner → pull preview → J → `12,6` → confirm |
| Measurement | K → first point → pull right → J → length → confirm |
| Stretch | S → partial edge selection → J → final size → confirm |
| Move | M → click object → J relative entry → repeat with Shift+J absolute entry |
| Copy | C → click source → pull preview → N → count → J → pitch → confirm |
| Contour | Idle rectangle → Shift+J → offset → pivot → inside/outside → confirm |
| Cleanup | Prepare disposable Steiner objects → toolbar action → inspect CIW count |

Keep original captures under `artifacts/recordings/`. Check every frame before
promoting an edited recording to `docs/media/`. Label real recordings with the
tested Virtuoso release and distinguish them from the illustrative animations.
Do not use private historical screenshots as publication assets.

Browser checks validate the illustrations and controls. Native behavior still
requires the live and manual checks in [README.md](README.md).
