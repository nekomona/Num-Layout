# Num-Layout — user guide

[Project overview](../README.md) · [Interactive demonstrations](demo/index.html) · [Tests](../test/README.md)

Num-Layout adds numeric entry and geometry picking to native Virtuoso
Layout commands. It targets Virtuoso IC23.1; native form fields and callbacks
may differ on other releases.

This guide follows your browser language when first opened. Use **EN / 中文** to
switch explicitly; the choice is remembered across the home page, guide, and lab.

**Contents:** [Install](#installation) · [Toolbar and previews](#toolbar-and-previews) ·
[Command reference](#use) · [X/Y input](#xy-input-and-absolute-position) ·
[Copy count](#copy-count-n) · [Picking and confirmation](#j-number-entry) ·
[Contour](#contour-a-rectangle) · [Interactive demos](#interactive-demonstrations) ·
[Repository layout](#repository-layout)

## Installation

The deployable runtime files are in `src/`. Keep their relative paths intact:

```text
src/
  numeric_assist.il
  numeric_assist.drf
  wire_refresh.py
  icons/
    numeric_assist.png
    remove_steiners.png
```

To load directly from a checkout, use its absolute path in the Virtuoso CIW:

```skill
load("/path/to/numeric-assist/src/numeric_assist.il")
```

The script installs its bindings and toolbar when loaded. To load it at startup,
add that line to your own `.cdsinit`. Run `vbnUninstall()` in CIW to restore the
previous bindings and remove the toolbar.

For remote deployment, install `virtuoso-bridge` in a virtual environment and
configure its SSH and GUI roles. From this repository, run:

```sh
python deploy.py
# Optional: choose an absolute directory on the remote host.
python deploy.py --remote-dir /path/to/numeric-assist
```

The deployment helper uploads the contents of `src/` into the installation
directory, checks their hashes, backs up the installed `.il`, and loads the
plugin through the bridge. For example, `--remote-dir /opt/numeric-assist`
installs `/opt/numeric-assist/numeric_assist.il`, with the helper, display
resources, and `icons/` beside it. The Wire refresh
helper requires Python 3, libX11, and the XTest extension on the GUI host. It
inherits DISPLAY and XAUTHORITY from Virtuoso.

## Toolbar and previews

The ruler icon enables or disables Num-Layout. Its pressed state means
that the assist is enabled. The routing-node and broom icon deletes invisible
Steiners from the edited layout, including during edit-in-place. It reports
the removed count and leaves saving to the user. The toolbar is registered
with the layout session's **Window > Toolbars** manager.

Candidate contours appear in yellow; selected contours and measurement arrows
appear in magenta. Picking respects displayed layers and hierarchy levels.
The plugin loads its own highlight packets from `numeric_assist.drf`.

After Wire width confirmation, `wire_refresh.py` nudges the pointer by 32 pixels
in X and 16 pixels in Y, then returns it after 40 ms. It checks the target,
focus, held buttons, and pointer movement before returning. It skips the return
if user input intervenes. CIW diagnostics are available as:

```skill
list(vbnWireRefreshBusy vbnWireRefreshStatus)
```

A successful pointer return does not establish that the native rubberband
repainted; verify that behavior interactively using the test instructions.

## Use

Start a native **Rectangle**, **Path**, **Wire**, **Measurement (K)**, **Stretch**, **Move**, or **Copy**
command, or select one rectangle to contour it.

| Active command | Key | Confirmed number means |
| --- | --- | --- |
| Path | J | Width of the active path |
| Wire | J | Width of the current wire segment |
| Rectangle | J | Rectangle width/height; enter `X,Y` |
| Measurement (K) | J | Length of a new two-point ruler |
| Stretch | J | Final length for one selected edge/endpoint; displacement for a whole object or multiple objects |
| Stretch | Shift+J | Stretch displacement magnitude |
| Move | J | Move displacement magnitude |
| Move | Shift+J | Absolute reference-point position |
| Copy | J | Per-copy displacement; keeps the copy count |
| Copy | Shift+J | Absolute position of the first copy's reference point |
| Copy | N | Positive integer copy count; does not place copies |
| One selected rectangle, no command | Shift+J | Start Contour |

### X/Y input and absolute position

In Move, Copy, Stretch, Measurement, and Rectangle, a comma switches input to
`X,Y`. Each component accepts decimals and a leading minus. Backspace edits the
text normally. A second comma or a second dot in the same component is ignored.

| Context | `10,20` | `10,` | `,20` |
| --- | --- | --- | --- |
| J Move/Copy or relative Stretch | Delta X=10, Y=20 | Delta X=10, Y=0 | Delta X=0, Y=20 |
| J partial Stretch size | Width=10, height=20 | Width=10; height unchanged | Height=20; width unchanged |
| J Rectangle | Width=10, height=20 | Width=10; height unchanged | Height=20; width unchanged |
| J Measurement | End point at start + (10,20) | Horizontal delta 10 | Vertical delta 20 |
| Shift+J Move/Copy | Target position (10,20) | Target X=10; Y unchanged | Target Y=20; X unchanged |

For **Shift+J Move/Copy**, the target is the native command's reference point.
When no reference point is recorded, Num-Layout uses the selected objects'
combined bounding-box center. Coordinates use the displayed window's frame,
including during edit-in-place. A **single number** changes only X or Y,
selected by mouse direction from the reference point; the hint identifies the
axis. Negative absolute coordinates are supported.

Explicit X/Y components determine the edit without an angular snap constraint;
the manufacturing grid still applies. Scalar relative distances retain the
current orthogonal/45-degree/any-angle behavior. Switching J and Shift+J during
Move/Copy keeps pending input, picked edges, and the copy count. In repeated
Copy, the first target uses the commanded position, and later targets repeat
the same displacement; every Step target is previewed.

For **Rectangle drawing**, J before the first corner sets the native Specify
Size fields for subsequent placement. After the first corner, J previews and
completes the rectangle in the mouse's quadrant. An omitted dimension retains
the existing native field or the current provisional rectangle extent. A
single value selects an axis by mouse direction after the first corner; before
the first corner it sets width.

For **rectangle resizing**, use native partial Stretch to select an edge/corner,
then J with a final width/height. The opposite side stays fixed. Whole-object
or multiple-object Stretch retains relative displacement behavior; Shift+J
Stretch also stays relative.

Comma keeps the preceding number as X, including a prefilled or picked value.
Clear it with Escape first when starting with an empty X. Picking after a comma
fills Y without discarding X. Empty `,` cannot confirm. Size dimensions must be
positive. N remains integer-only; Path/Wire widths and Contour offsets stay
scalar. The last successful X/Y input is remembered for Cartesian modes;
scalar modes keep their scalar memory.

### Copy count (N)

During native Copy, press **N**, type a positive integer using `0`–`9` and
Backspace, then confirm with **Enter**, **Space**, **N** again, or a canvas click.
The cursor label shows `COPY COUNT`. Decimal input is ignored; zero cannot be
confirmed. N does not pick geometry or change the remembered J distance.
Pressing **J** or **Shift+J** while N is open first applies the pending count,
then opens relative or absolute entry without placing copies. Invalid or empty count
input keeps N open for correction.

Confirmation sets native **Copies → Type: Step → Number**, closes numeric
entry, and leaves Copy waiting for placement. It does not invoke Copy's Apply
action or add a point. Place the copies using native Copy afterward.

Entering N resets the native copy count to **1**. A confirmed N count is
preserved when J opens, so N can set the number of copies and J can set their
displacement. J previews every Step copy target for each selected object, at
successive multiples of the entered distance. Its hint includes the count,
for example `12 | COPY DISTANCE [3 copies]`. Confirming J places all the copies.

Canceling either assist, entering N again, or leaving J resets the count to
**1**. On J confirmation, that reset happens after placement. Escape first
clears N's digits; another Escape closes numeric entry while keeping native
Copy active.

Outside Copy, N retains its previous native binding. Turning Num-Layout
off also restores N's native behavior. Uninstalling restores the prior N
enterfunction binding; the normal N binding is not replaced.

### J number entry

After the hotkey, type `0`–`9`, `.`, `,`, `-`, or Backspace as appropriate for the mode. The current input and mode
appear next to the cursor. The result contour appears while a valid number is
pending. Num-Layout captures Virtuoso's physical dot binding during input
and restores its original magnifier binding when the assist closes.
Click a shape edge instead to use its length. A second parallel
edge changes the number to the distance between the edges. A perpendicular
second edge or any third edge begins a new single-edge measurement. Ruler edges
are available too.

For a wire path segment, clicking its centerline or terminal uses the wire's
physical width. Clicking a side uses that side's length; clicking a second
parallel side uses the spacing between the sides. The yellow hover line and
magenta selection arrow show the exact feature being measured. Num-Layout
uses the raw mouse position for wire picking so native Wire snapping does not
turn a side click into a centerline click.

Edge picking follows instance hierarchy into leaf shapes, including PCell
geometry and array elements. Edges are measured in the edited cellview's
coordinates after each instance transform. Contour can also use a rectangle
inside an instance as its pivot; the selected source rectangle remains in the
edited cellview.

The last confirmed J number is prefilled the next time J opens. Confirm it to
reuse it, or type a digit to replace it. Escape clears the prefilled number
before closing the assist. Wire and Path picking use the mouse position before
native snapping; clicking anywhere along a wire's longitudinal centerline,
including its terminals, picks its width.

The edge under the cursor is yellow. Selected edges and a length arrow are
magenta. Outside Contour, press **Enter**, **Space**, the same hotkey again, or
click empty canvas to confirm. Escape while
edges are selected returns to number entry. Escape with digits clears them;
Escape with an empty entry closes Num-Layout and leaves the native command
active. A click used to pick an edge or confirm a number is consumed by Numeric
Assist and does not add a point to the native command.

For absolute Stretch length, select one **edge or endpoint** with native
Stretch before pressing J. With a whole object or multiple objects selected,
J uses displacement magnitude, with the same number entry, preview, and snap
direction as Move. A ruler
or straight path uses the distance between its endpoints. Other shapes use
their X or Y bounding extent, according to the stretch direction. Shift+J
uses the direction from the native command's reference point to the cursor.
For Wire, J updates the native Create Wire form's `wireWidth` field. The
current segment contour uses that width before confirmation. The native Wire
command remains active after confirmation, so subsequent points use the new
width.

For **Measurement (K)**, place its first point, move the cursor toward the
desired direction, and press J. Enter or pick a number and confirm to create a
saved ruler at that length. A line previews the result before confirmation.
The active Measurement command then ends. Its endpoint is snapped to the
manufacturing grid, so diagonal lengths can have a small grid approximation.
When editing descended group contents or an instance in place, the saved ruler
uses the active edited cell's coordinates, keeping it at the requested position.

For **Copy**, select objects and start native Copy. Press J for relative input
or Shift+J for absolute position. A scalar relative distance follows the
Copy form's snap mode. If Copy has no entered reference point, Num-Layout
uses the center of the selected objects' combined bounding box as the direction
origin. Confirmation uses the native Copy form's X/Y fields in Pitch mode and
its Apply action, including the current Single, Step, or Array settings.

## Contour a rectangle

Select one rectangle with no active command, then press Shift+J. Enter a positive
offset, or measure an edge or the spacing between parallel edges. Press Enter
or Space to advance. Phase two starts in **edge** mode: click four edges that
define two distinct X and two distinct Y boundaries. Press **Shift+J** for
**rectangle** mode; a rectangle takes priority over its edge at the pointer.
Press **J** to return to edge-only picking. Switching modes preserves the
current edge or pivot selection. A new rectangle pick replaces the edge set.
The source rectangle's original boundary is also a valid pivot. Rectangle
picks tolerate a small distance from the displayed boundary, and confirmation
rebuilds a four-edge pivot from the selected edges. The edge segments may stop
short of the corners. Only Enter or Space advances
to phase three after a valid pivot is selected. Move the cursor
inside or outside the pivot to preview the result, then click or confirm again
to resize and move the initially selected rectangle. The offset applies to
all four sides. If an inset would collapse either dimension, only outside is
available. Each Escape returns one phase; from the number phase, Escape
clears the number before exiting.

Move and Copy J or Shift+J, and both Stretch displacement modes, follow the native command's current
segment snap mode when choosing displacement direction: orthogonal, diagonal
(45-degree increments), or any angle. Horizontal and vertical modes are also
respected when offered by the form. Change the snap mode in the native form;
Num-Layout reads it when drawing the preview and applying the number.

The assist snaps target coordinates to the technology manufacturing grid. It
sets rectangle extents, selected path points, and straight path/ruler endpoints
from absolute target coordinates after native Stretch completes, avoiding
half-grid rounding in the native relative delta. Shape types without editable
points use native Stretch's result.
A requested diagonal length may be approximated by the nearest grid
coordinates.

## Interactive demonstrations

Open [the demo website](demo/index.html) in a browser. It is a self-contained
static site: `index.html`, `style.css`, and `app.js`. You can open the HTML file
directly, or serve the repository locally:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8000/docs/demo/`. Choose a tool, change its value,
and use **Play / Pause**, **Next step**, or the step buttons. Tool selections are
bookmarkable, for example `index.html#copy` or `index.html#contour`.

Choosing a tool starts its animation from the beginning with **Loop** enabled.
Use **Speed** (0.25×–3×) to adjust playback without losing your place, or toggle
**Loop** off to play once. Each loop waits three seconds after completion;
this wait stays three seconds at every playback speed. The pointer starts in
empty space and returns there as the last action of the final step. The action
bar then reads **Done.**

**Try a value** replays automatically after a dropdown choice, Enter, leaving an
input, or three seconds without typing. Valid decimal inputs are normalized
before replay; invalid inputs show an error and keep the last valid values.
**Apply & replay** also starts over with the current values.

The animations move the pointer onto a target before revealing its hover
highlight. Keycaps depress at each input event and numbers appear one character
at a time, 260 ms apart at 1× speed. Clicks and command keys leave at least
1.2 seconds to inspect the result before the next action. Cursor balloons use
the plugin's actual label text; explanations appear in the panel's bottom bar.
Decimal values entered in the demo are rounded to four decimal
places; copy counts remain integers. These presentation rules apply to the
illustrations and do not change the native plugin's numeric precision.

For a hosted site, use the repository-independent
[GitHub and GitLab Pages deployment workflows](PUBLISHING.md).

The scenes are interactive illustrations made with synthetic geometry. They
explain input, preview, and confirmation; they do not execute SKILL or reproduce
the Cadence UI. Coordinates use an idealized grid. Native snapping, hierarchy,
form callbacks, and pointer-refresh behavior must be checked in Virtuoso.

| Demonstration | Try this | Animation |
| --- | --- | --- |
| [Pick a dimension](demo/index.html#pick) | Switch from an edge length to parallel-edge spacing | [Watch](media/pick.gif) |
| [Path / Wire](demo/index.html#width) | Change width, then confirm | [Watch](media/width.gif) |
| [Rectangle](demo/index.html#rectangle) | Enter width and height as `X,Y` | [Watch](media/rectangle.gif) |
| [Measurement](demo/index.html#measure) | Set a ruler's length | [Watch](media/measure.gif) |
| [Stretch](demo/index.html#stretch) | Set a partial selection's final X extent | [Watch](media/stretch.gif) |
| [Move](demo/index.html#move) | Compare relative delta with absolute position | [Watch](media/move.gif) |
| [Copy](demo/index.html#copy) | Set N, then use J for Step displacement | [Watch](media/copy.gif) |
| [Contour](demo/index.html#contour) | Switch inside/outside around a pivot | [Watch](media/contour.gif) |
| [Steiner cleanup](demo/index.html#cleanup) | Remove synthetic Steiner markers while retaining shapes | [Watch](media/cleanup.gif) |

See [demo recording instructions](../test/DEMO_MEDIA.md) to regenerate the
animations or capture a real, isolated Virtuoso session.

## Repository layout

`src/` contains the SKILL program and all deployed runtime assets. `deploy.py`
at the root installs them. `tools/generate_icons.py` regenerates the icons in
`src/icons/` and requires Pillow. `docs/` contains public usage documentation.
`docs/demo/` contains the interactive illustrations, and `docs/media/` contains
reviewed documentation assets. `test/` contains test scripts and manual checks. Local agent instructions
belong in `.local/agent/`; screenshots,
verification reports, and other test output belong in `artifacts/`. Both local
folders are ignored by Git.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development, testing, and pre-PR checks.
