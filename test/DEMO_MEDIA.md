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
```

If an installed Microsoft Edge browser is preferred, pass `--channel msedge`
to the capture and check scripts. This avoids installing Playwright Chromium.
`render_demos.py --only copy,contour` regenerates selected scenes. A full run
also creates `overview.gif` from Width, Copy, and Contour.

The exporter captures six screenshots per step, then assembles the frames
with short pauses around each operation. Intermediate PNGs stay under ignored
`artifacts/demo-frames/`. Only the reviewed GIFs are tracked in `docs/media/`.
`tools/build_guide.py` generates the browser guide from the canonical Markdown
document; regenerate it when the Markdown changes.

## Recording an actual Virtuoso session

Use the dedicated test library and environment described in [README.md](README.md).
Prepare fresh synthetic geometry with the testbench scripts. Set a neutral
test-cell name and frame the canvas so usernames, hostnames, paths, clocks,
production designs, and CIW transcripts are excluded from every frame.

For each tool, record a short sequence:

| Tool | Sequence |
| --- | --- |
| Picking | Hover → select one edge → select a parallel edge → inspect the value |
| Path / Wire | Start command → J → enter width → confirm → place a segment |
| Rectangle | First corner → J → `12,6` → preview → confirm |
| Measurement | K → first point → J → length → confirm |
| Stretch | Partial edge selection → J → final size → confirm |
| Move | Reference point → J relative entry → repeat with Shift+J absolute entry |
| Copy | Select source → N → count → J → pitch → preview all targets → confirm |
| Contour | Idle rectangle → Shift+J → offset → pivot → inside/outside → confirm |
| Cleanup | Prepare disposable Steiner objects → toolbar action → inspect CIW count |

Keep original captures under `artifacts/recordings/`. Check every frame before
promoting an edited recording to `docs/media/`. Label real recordings with the
tested Virtuoso release and distinguish them from the illustrative animations.
Do not use private historical screenshots as publication assets.

Browser checks validate the illustrations and controls. Native behavior still
requires the live and manual checks in [README.md](README.md).
