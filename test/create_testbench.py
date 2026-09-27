"""Create the isolated live-layout testbench for numeric_assist.il.

Run with the project's virtual environment. The cell name is intentionally
fixed and creation refuses to overwrite any existing cell.
"""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.layout import (
    layout_create_label,
    layout_create_path,
    layout_create_rect,
)

CELL = "VB_NUMERIC_LAYOUT_TB"


def main() -> None:
    client = VirtuosoClient.from_env()
    found = client.execute_skill(f'ddGetObj("{LIB}" "{CELL}")')
    if found.output != "nil":
        raise RuntimeError(f"Refusing to replace existing cell {LIB}/{CELL}")
    with client.layout.create(LIB, CELL) as lay:
        lay.add(layout_create_rect(LAYER, "drawing", 0, 0, 8, 3))
        lay.add(layout_create_rect(LAYER, "drawing", 12, 0, 20, 5))
        lay.add(layout_create_path(LAYER, "drawing", [(0, 10), (8, 10), (8, 15)], 1))
        lay.add(layout_create_path(LAYER, "drawing", [(12, 10), (22, 10)], 2))
        lay.add(layout_create_label(LAYER, "drawing", 0, -3, "STRETCH X/Y", "lowerLeft", "R0", "stick", 0.8))
        lay.add(layout_create_label(LAYER, "drawing", 0, 17, "PATH WIDTH", "lowerLeft", "R0", "stick", 0.8))
    client.open_window(LIB, CELL, view="layout")
    ruler = client.execute_skill(
        'let((cv) cv=geGetEditCellView(hiGetCurrentWindow()) '
        'leCreateMeasurement(cv list(0:20 10:20) t "Ruler") dbSave(cv))'
    )
    if not ruler.ok:
        raise RuntimeError(f"Could not add test ruler: {ruler.errors}")
    print(f"Created and opened {LIB}/{CELL}/layout")


if __name__ == "__main__":
    main()
