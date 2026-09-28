# Numeric Assist for Virtuoso Layout

Numeric Assist adds a value picker to native Virtuoso layout editing. Press **J** while drawing a path or wire, creating a measurement, stretching, or moving. With one rectangle selected and no command active, **Shift+J** starts Contour. Idle J keeps Virtuoso's selection command, and Ctrl+J keeps Flip. The **Numeric J** toolbar button enables or disables the assist.

## Start a session

Load the plugin through your configured bridge:

```powershell
virtuoso-bridge load numeric_assist.il
```

The file installs the J bindings and toolbar button when loaded. To remove them and restore the previous bindings, run `virtuoso-bridge eval 'vbnUninstall()'`.

## Choose the value

After **J**, type digits, the decimal point, or Backspace. The number and the active mode appear beside the cursor. The last confirmed number is prefilled the next time J opens; typing a digit or decimal point replaces that prefill. Enter, Space, J again, or a click on empty canvas confirms the value. Escape clears the current input before closing the assist, leaving the native command active.

You can also take a value from geometry:

1. Move over an edge. The candidate edge turns **yellow**.
2. Click once to use that edge's length. The selected edge and length arrow turn **magenta**.
3. Click a parallel edge to use the spacing between the two edges. A perpendicular second edge starts a new single-edge pick; a third edge also starts over.

Edges inside instances, PCells, and arrays can be picked. Numeric Assist
transforms each picked shape into the edited cellview's coordinates before
measuring it. Contour can use an internal rectangle as its pivot.

For a wire, clicking its longitudinal centerline or terminal uses its physical width. A side click uses the side length. The plugin uses the raw pointer position for Path and Wire picking, even if native wire drawing snaps the working cursor elsewhere.

## What J changes

| Native context | Key | Result after confirmation |
| --- | --- | --- |
| Path | J | Active path width |
| Wire | J | Current wire segment width |
| Measurement (K) | J | New measurement length |
| Stretch | J | Final extent along the stretch direction |
| Stretch | Shift+J | Stretch displacement magnitude |
| Move | J or Shift+J | Move displacement magnitude |
| One rectangle selected, no active command | Shift+J | Contour offset |

### Path and Wire widths

Start the native Path or Wire command, press J, enter or pick the width, then confirm. The preview shows the new contour before confirmation. In Wire, the confirmed value updates the Create Wire form's `wireWidth` for the current and subsequent segments.

### Stretch and Move

For an absolute Stretch length, select one edge or endpoint with native Stretch before pressing J. A whole-shape selection translates the shape in Virtuoso, so it cannot specify one final extent. Shift+J in Stretch, and either J or Shift+J in Move, sets the displacement magnitude in the direction from the command's start point toward the pointer. The current native snap mode controls that direction: orthogonal, 45-degree, or any angle.

The plugin places supported rectangle extents and straight path or ruler endpoints at absolute grid coordinates after native Stretch completes. This avoids the observed half-grid error where a requested `20.000` could land at `19.995`. Diagonal results can still differ slightly because the manufacturing grid has discrete coordinates.

### Measurement

Press K to start a native measurement, place its first point, and move toward the desired direction. Press J, enter or pick a length, and confirm. Numeric Assist creates a saved ruler at that length and finishes the Measurement command. Live tests produced exact `5.0` lengths from typed and edge-picked values.

## Contour a rectangle

Select exactly one source rectangle while no command is active, then press Shift+J. Contour has three phases:

1. **Offset:** Type a positive number or pick it from one or two edges. Confirm to advance.
2. **Pivot:** Click a pivot rectangle, or select four edges that define two X and two Y boundaries. The segments may stop short of the corners. Confirm the pivot.
3. **Side:** Move the pointer inside or outside the pivot. A magenta contour previews the chosen result, and the cursor label says INSIDE or OUTSIDE. Click or press a confirmation key to move and resize the source rectangle.

Each Escape returns to the preceding phase. If the inset would collapse either pivot dimension, only OUTSIDE is available. The direction preview repaints as the pointer moves through empty canvas, including across a boundary with no object under the cursor.

## Quick reference

| Input | Effect while Numeric Assist is active |
| --- | --- |
| `0`–`9`, `.` | Enter a number; first character replaces remembered value |
| Backspace | Remove the last entered character |
| Click an edge | Pick its length or wire width |
| Click a second parallel edge | Pick the spacing between edges |
| Enter, Space, active hotkey | Confirm the current value or contour phase |
| Escape | Clear the current value or return one contour phase |
| Numeric J toolbar button | Enable or disable the assist |

The physical dot key is captured for decimal input while Numeric Assist runs. Its original Virtuoso magnifier binding returns when the assist closes. Edge picking searches shapes through the instance hierarchy and saved ruler markers in the edited cellview. The cursor label uses a temporary highlight on the current entry layer, which must be visible.
