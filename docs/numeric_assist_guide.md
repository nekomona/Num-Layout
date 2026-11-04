# Numeric Assist quick guide

Load `numeric_assist.il` with its sibling runtime assets as described in the
[installation instructions](../README.md#installation).

1. Start a native Rectangle, Path, Wire, Measurement, Stretch, Move, or Copy command.
2. Press **J** to enter a value or pick a geometry edge. Pick a second parallel
   edge to measure spacing. The candidate is yellow and the selection is magenta.
3. Confirm with Enter, Space, the active hotkey, or empty canvas. Contour uses
   Enter or Space to advance its offset and pivot phases.
4. Escape clears input before closing the assist. The native command remains
   active unless confirming a completed operation ends it.

| Context | J | Shift+J |
| --- | --- | --- |
| Path / Wire | Width | — |
| Rectangle | Width/height, including `X,Y` | — |
| Measurement | Length or endpoint delta | — |
| Partial Stretch | Final extent of selected edge/endpoint | Relative displacement |
| Whole-object / multiple-object Stretch | Relative displacement | Relative displacement |
| Move / Copy | Relative displacement or `X,Y` delta | Absolute reference-point position |
| One idle selected rectangle | Native binding | Contour |

During Copy, **N** sets a positive integer Step copy count without placing copies.
J preserves that count and previews each Step target. Scalar relative distances
follow the native snap mode; explicit X/Y input still snaps to the manufacturing
grid. Omitted X or Y components retain the context-specific behavior described
in the [full input reference](../README.md#xy-input-and-absolute-position).

Contour resizes a selected rectangle in three phases: choose a positive offset,
choose a pivot rectangle or four bounding edges, then choose inside or outside.
In its pivot phase, J picks edges and Shift+J gives rectangles priority.
Enter or Space advances phases; Escape returns to the preceding phase.

The ruler toolbar icon toggles the assist. The routing-node and broom icon
removes invisible Steiners without saving the cellview. `vbnUninstall()`
restores the previous key bindings.

See the [full usage reference](../README.md#use) for input memory, wire-width
picking, hierarchy transforms, repeated Copy, and grid rounding. Reproducible
checks and environment setup are in [test/](../test/README.md).
