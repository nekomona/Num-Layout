# Numeric Layout Assist for Virtuoso

Load `numeric_assist.il` in the Virtuoso CIW using your installation path.
Keep any sibling runtime assets beside the script. The script installs
its bindings when loaded; `vbnUninstall()` restores prior bindings.
See [test instructions](test/README.md) for isolated live checks.

## Use

Start a native **Path**, **Wire**, **Stretch**, or **Move** command, or select one
rectangle to contour it.

| Active command | Key | Confirmed number means |
| --- | --- | --- |
| Path | J | Width of the active path |
| Wire | J | Width of the current wire segment |
| Stretch | J | Final length along the stretch direction |
| Stretch | Shift+J | Stretch displacement magnitude |
| Move | J | Move displacement magnitude |
| Move | Shift+J | Move displacement magnitude |

After the hotkey, type `0`–`9`, `.`, or Backspace. The current input appears next
to the cursor. The result contour appears while a valid number is pending.
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

The last confirmed J number is prefilled the next time J opens. Confirm it to
reuse it, or type a digit to replace it. Escape clears the prefilled number
before closing the assist. Wire and Path picking use the mouse position before
native snapping; clicking anywhere along a wire's longitudinal centerline,
including its terminals, picks its width.

The edge under the cursor is yellow. Selected edges and a length arrow are
magenta. Press **Enter**, **Space**, the same hotkey again, or click empty canvas
to confirm. Escape while
edges are selected returns to number entry. Escape with digits clears them;
Escape with an empty entry closes Numeric Assist and leaves the native command
active. A click used to pick an edge or confirm a number is consumed by Numeric
Assist and does not add a point to the native command.

For absolute Stretch length, select one **edge or endpoint** with native
Stretch before pressing J. Selecting the entire shape translates it in
Virtuoso, so Numeric Assist refuses an absolute length in that state. A ruler
or straight path uses the distance between its endpoints. Other shapes use
their X or Y bounding extent, according to the stretch direction. Shift+J
uses the direction from the native command's reference point to the cursor.
For Wire, J updates the native Create Wire form's `wireWidth` field. The
current segment contour uses that width before confirmation. The native Wire
command remains active after confirmation, so subsequent points use the new
width.

## Contour a rectangle

Select one rectangle outside Move or Stretch, then press J. Enter a positive
offset, or measure an edge or the spacing between parallel edges. Press Enter,
Space, or J to advance. Click inside a pivot rectangle, or select four edges
that form one rectangle's bounding box, and confirm the pivot. Move the cursor
inside or outside the pivot to preview the result, then click or confirm again
to resize and move the initially selected rectangle. The offset applies to
all four sides. If an inset would collapse either dimension, only outside is
available. Each Escape returns one phase; from the number phase, Escape
clears the number before exiting.

Move J and Shift+J, and Stretch Shift+J, follow the native command's current
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
selection searches top-level shapes and saved ruler markers in the edited
cellview; it does not transform edges inside placed instances. Absolute Stretch
length requires exactly one native selection with a subset of its points
selected. The cursor label uses a temporary highlight set on the current entry
layer, so that layer needs to be visible.
