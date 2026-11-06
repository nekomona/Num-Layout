"""Create an isolated three-level layout for NLayout hierarchy checks.

The script refuses to replace any existing cells and never edits user layouts.
Run it with a virtual environment and configured bridge profile.
"""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.layout import (
    layout_create_param_inst,
    layout_create_rect,
    layout_create_simple_mosaic,
)


LEAF = "VB_NUMERIC_HIER_LEAF"
MIDDLE = "VB_NUMERIC_HIER_MID"
TOP = "VB_NUMERIC_HIER_TB"


def instance(cell: str, name: str, x: float, y: float, orient: str) -> str:
    return (
        f'dbCreateInstByMasterName(cv "{LIB}" "{cell}" "layout" '
        f'"{name}" list({x:g} {y:g}) "{orient}")'
    )


def main() -> None:
    client = VirtuosoClient.from_env()
    for cell in (LEAF, MIDDLE, TOP):
        found = client.execute_skill(f'ddGetObj("{LIB}" "{cell}")')
        if found.output != "nil":
            raise RuntimeError(f"Refusing to replace existing cell {LIB}/{cell}")
    pcell_available = bool(PCELL_LIB and PCELL_CELL) and client.execute_skill(
        f'ddGetObj("{PCELL_LIB}" "{PCELL_CELL}")'
    ).output != "nil"

    with client.layout.create(LIB, LEAF) as lay:
        lay.add(layout_create_rect(LAYER, "drawing", 0, 0, 4, 2))
        lay.add(layout_create_rect(LAYER, "drawing", 6, 0, 8, 3))
        lay.add(f'dbCreatePathSeg(cv list("{LAYER}" "drawing") '
                'list(0 6) list(4 6) 0.6 "truncate" "truncate")')

    with client.layout.create(LIB, MIDDLE) as lay:
        lay.add(instance(LEAF, "leafR90", 20, 0, "R90"))
        lay.add(layout_create_rect(LAYER, "drawing", 0, 0, 2, 1))

    with client.layout.create(LIB, TOP) as lay:
        lay.add(instance(MIDDLE, "midMX", 30, 30, "MX"))
        lay.add(instance(LEAF, "leafR0", 0, 20, "R0"))
        lay.add(layout_create_simple_mosaic(
            LIB, LEAF, origin=(0, 35), rows=2, cols=2,
            row_pitch=10, col_pitch=10, instance_name="leafArray",
        ))
        if pcell_available:
            lay.add(layout_create_param_inst(
                PCELL_LIB, PCELL_CELL, "layout", "pcellSample",
                10, 40, "R90",
            ))
        lay.add(layout_create_rect(LAYER, "drawing", 50, 50, 52, 52))

    client.open_window(LIB, TOP, view="layout")
    print(f"Created and opened {LIB}/{TOP}/layout")


if __name__ == "__main__":
    main()
