# Testing Numeric Assist

Run commands from the repository root using a virtual environment. Offline
tests use Python's standard library. Live checks additionally require the
installed `virtuoso-bridge` package, working bridge configuration, a running
Virtuoso session, and Numeric Assist loaded from `src/numeric_assist.il` with
its sibling runtime assets, or from an installation created by `deploy.py`.

## Offline tests

```sh
python -m unittest discover -s test -t . -p "test_*.py" -v
```

These tests exercise Wire refresh target checks, pointer restoration, canvas
boundaries, and input interruption using a fake X11 connection. They send no
live input and do not require Virtuoso or an X server.

For the documentation website, animation capture, and browser checks, see
[DEMO_MEDIA.md](DEMO_MEDIA.md). These checks use synthetic geometry and run
separately from the native plugin tests.
The Pages artifact and deployment checks are described in
[Pages deployment](../docs/PUBLISHING.md).

## Live environment

Create a dedicated writable test library in Virtuoso and attach your own
technology. Choose a valid visible drawing layer. Do not use a design library.
Set the following in the shell that launches the test scripts:

```powershell
$env:VBN_TEST_LIB = "NUMERIC_ASSIST_TESTS"
$env:VBN_TEST_LAYER = "M1"
```

The names above are generic defaults; select names appropriate for your
installation. Optional hierarchy PCell coverage requires both
`VBN_TEST_PCELL_LIB` and `VBN_TEST_PCELL_CELL`. No foundry library is assumed.
The bridge reads its own environment/profile configuration independently.
Keep credentials and host configuration outside the tracked tree.

Verify connectivity with `virtuoso-bridge status`, then load the plugin using
`python deploy.py`, which deploys the contents of `src/`. Keep the session idle
before starting a live check. Run
one script at a time: scripts open layout windows, run native commands, and
change selection or form state. Cell-creation checks refuse existing names;
verification scripts use fresh cell names. Reuse or delete only test cells.

## Test scripts

| Command | Coverage |
| --- | --- |
| `python test/create_testbench.py` | Rectangles, paths, labels, and a saved ruler |
| `python test/create_hierarchy_testbench.py` | Rotated/mirrored hierarchy, arrays, optional PCell |
| `python test/verify_feedback.py` | Contour picks, visibility, hierarchy, Path state |
| `python test/verify_copy_count.py` | Integer N input, count resets, Step Copy previews and placement |
| `python test/verify_group_edit.py` | Group Copy and ruler coordinates during edit-in-place |
| `python test/verify_xy.py` | Cartesian edits, absolute Move/Copy, Rectangle sizing |
| `python test/verify_wire_refresh.py` | Wire width and command-state preservation with motion disabled |
| `python test/verify_wire_clock.py` | Helper IPC and X-server clocks without pointer motion |
| `python test/verify_wire_xtest.py` | XTest capability and IPC completion without pointer motion |

`verify_copy_count.py` also accepts `--lib` and `--layer` overrides. Reports go
to `artifacts/reports/`, which is created automatically and ignored by Git.
Put screenshots in `artifacts/screenshots/`. Reports and screenshots may
contain local cell names or display content; keep them local.

For an explicit test window, `python test/run_x11_probe.py WINDOW_ID ACTION...`
uploads and runs `test/x11_probe.py` on the configured SSH host. This probe
sends real keyboard and mouse events. Inspect its supported actions before
using it, and target only the dedicated test layout window.

## Manual checks

Use synthetic geometry in the dedicated test library. Record local outcomes
and screenshots under `artifacts/`; this checklist does not assert a prior pass.

- Toggle the ruler toolbar button and verify bindings are restored when off.
  Switch layout tabs and check that the toolbar remains available.
- Enter Path and Wire widths using digits and edge picks. Confirm with Enter,
  Space, the hotkey, and empty canvas. Check both the preview and committed width.
- Check yellow hover contours, magenta selected edges, bidirectional arrows,
  parallel-edge spacing, wire centerline/terminal width, and input memory.
- Hide layers and collapse hierarchy. Hidden geometry must not be picked.
  Repeat picks through rotated/mirrored instances, arrays, and optional PCells.
- Check partial Stretch final extent and whole-object/multiple-object
  displacement. Repeat in each native snap mode and near grid boundaries.
- Check relative Move/Copy and absolute Shift+J positions with positive,
  negative, complete, and omitted X/Y components. Include edit-in-place.
- In Copy, use N for several Step copies, transfer to J and Shift+J, and check
  every preview target against placement. Check cancellation and count resets.
- Check Rectangle sizing before and after the first corner, and saved ruler
  length and coordinates inside a rotated child.
- Exercise all Contour phases, edge/rectangle pivot switching, inside/outside
  previews, invalid inset rejection, and Escape transitions.
- Confirm Wire width repeatedly and watch the native rubberband repaint.
  A helper status alone cannot establish visible repaint. Check that later
  pointer input, held buttons, and leaving the target interrupt restoration.
- Create disposable Steiner objects in the test cell. The cleanup button
  should remove them without changing shapes or saving the cellview.
- Uninstall and verify prior J, Shift+J, N, and decimal-key behavior returns.
