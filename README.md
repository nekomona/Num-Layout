# Numeric Layout Assist for Virtuoso

Load `numeric_assist.il` in the Virtuoso CIW using your installation path.
Keep any sibling runtime assets beside the script. The script installs
its bindings when loaded; `vbnUninstall()` restores prior bindings.
See [test instructions](test/README.md) for isolated live checks.

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
When no reference point is recorded, Numeric Assist uses the selected objects'
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

Outside Copy, N retains its previous native binding. Turning Numeric Assist
off also restores N's native behavior. Uninstalling restores the prior N
enterfunction binding; the normal N binding is not replaced.

### J number entry

After the hotkey, type `0`–`9`, `.`, `,`, `-`, or Backspace as appropriate for the mode. The current input and mode
appear next to the cursor. The result contour appears while a valid number is
pending. Numeric Assist captures Virtuoso's physical dot binding during input
and restores its original magnifier binding when the assist closes.
Click a shape edge instead to use its length. A second parallel
edge changes the number to the distance between the edges. A perpendicular
second edge or any third edge begins a new single-edge measurement. Ruler edges
are available too.

For a wire path segment, clicking its centerline or terminal uses the wire's
physical width. Clicking a side uses that side's length; clicking a second
parallel side uses the spacing between the sides. The yellow hover line and
magenta selection arrow show the exact feature being measured. Numeric Assist
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
Escape with an empty entry closes Numeric Assist and leaves the native command
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
Copy form's snap mode. If Copy has no entered reference point, Numeric Assist
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
Numeric Assist reads it when drawing the preview and applying the number.

The assist snaps target coordinates to the technology manufacturing grid. It
sets rectangle extents, selected path points, and straight path/ruler endpoints
from absolute target coordinates after native Stretch completes, avoiding
half-grid rounding in the native relative delta. Shape types without editable
points use native Stretch's result.
A requested diagonal length may be approximated by the nearest grid
coordinates.

## Version and scope

The native form fields and callbacks were checked against a running Virtuoso
IC23.1 instance. Recheck them on another release before loading there. Edge
selection searches shapes through the instance hierarchy and saved ruler
markers in the edited cellview. Absolute Stretch
length requires exactly one native selection with a subset of its points
selected. Cursor labels use plugin-owned window highlight packets.
