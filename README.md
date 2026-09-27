# Numeric Layout Assist for Virtuoso

Load `numeric_assist.il` in the Virtuoso CIW using your installation path.
Keep any sibling runtime assets beside the script. The script installs
its bindings when loaded; `vbnUninstall()` restores prior bindings.
See [test instructions](test/README.md) for isolated live checks.

## Use

Start a native **Path**, **Wire**, **Stretch**, or **Move** command first.

| Active command | Key | Confirmed number means |
| --- | --- | --- |
| Path | J | Width of the active path |
| Wire | J | Length of the last wire segment |
| Stretch | J | Final length along the stretch direction |
| Stretch | Shift+J | Stretch displacement magnitude |
| Move | Shift+J | Move displacement magnitude |

After the hotkey, type `0`–`9`, `.`, or Backspace. The current input appears next
to the cursor. The result contour appears while a valid number is pending.
Click a shape edge instead to use its length. A second parallel
edge changes the number to the distance between the edges. A perpendicular
second edge or any third edge begins a new single-edge measurement. Ruler edges
are available too.

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
For Wire, place at least one native wire point first. If two or more points are
already entered, confirmation replaces the last point and changes the last
segment. With one point entered, it adds a segment of the requested length.
Point the cursor toward the intended segment direction.
Confirmation commits that wire through the entered endpoint; the native Wire
command stays active, ready for another wire.

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
