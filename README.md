# Numeric Layout Assist for Virtuoso

Load `numeric_assist.il` in the Virtuoso CIW using your installation path.
Keep any sibling runtime assets beside the script. The script installs
its bindings when loaded; `vbnUninstall()` restores prior bindings.
See [test instructions](test/README.md) for isolated live checks.

## Use

Start a native **Path**, **Wire**, **Measurement (K)**, **Stretch**, **Move**, or **Copy**
command, or select one rectangle to contour it.

| Active command | Key | Confirmed number means |
| --- | --- | --- |
| Path | J | Width of the active path |
| Wire | J | Width of the current wire segment |
| Measurement (K) | J | Length of a new two-point ruler |
| Stretch | J | Final length along the stretch direction |
| Stretch | Shift+J | Stretch displacement magnitude |
| Move | J | Move displacement magnitude |
| Move | Shift+J | Move displacement magnitude |
| Copy | J or Shift+J | Copy displacement magnitude |
| One selected rectangle, no command | Shift+J | Start Contour |

After the hotkey, type `0`–`9`, `.`, or Backspace. The current input and mode
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
Stretch before pressing J. Selecting the entire shape translates it in
Virtuoso, so Numeric Assist refuses an absolute length in that state. A ruler
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

For **Copy**, select objects and start native Copy. Press J or Shift+J, then
enter or pick the displacement magnitude. The cursor direction follows the
Copy form's snap mode. If Copy has no entered reference point, Numeric Assist
uses the center of the selected objects' combined bounding box as the direction
origin. Confirmation uses the native Copy form's X/Y fields and Apply action,
including its current Single, Step, or Array settings.

## Contour a rectangle

Select one rectangle with no active command, then press Shift+J. Enter a positive
offset, or measure an edge or the spacing between parallel edges. Press Enter
or Space to advance. Phase two starts in **edge** mode: click four edges that
define two distinct X and two distinct Y boundaries. Press **Shift+J** for
**rectangle** mode; a rectangle takes priority over its edge at the pointer.
Press **J** to return to edge-only picking. Switching modes preserves the
current edge or pivot selection. A new rectangle pick replaces the edge set.
The edge segments may stop short of the corners. Only Enter or Space advances
to phase three after a valid pivot is selected. Move the cursor
inside or outside the pivot to preview the result, then click or confirm again
to resize and move the initially selected rectangle. The offset applies to
all four sides. If an inset would collapse either dimension, only outside is
available. Each Escape returns one phase; from the number phase, Escape
clears the number before exiting.

Move and Copy J or Shift+J, and Stretch Shift+J, follow the native command's current
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
selected. The cursor label uses a temporary highlight set on the current entry
layer, so that layer needs to be visible.
