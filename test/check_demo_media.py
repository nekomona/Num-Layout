"""Verify freshly rendered GIF timing and the single-active-panel README grid."""

from bisect import bisect_right
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    schedule = json.loads((ROOT / "artifacts/demo-frames/overview/schedule.json").read_text(encoding="utf-8"))
    assert schedule["panels"] == ["pick", "width", "measure", "copy"]
    entries = schedule["frames"]
    active_order = []
    ends, total = [], 0
    for entry in entries:
        total += entry["duration"]
        ends.append(total)
        if entry["active"] and (not active_order or active_order[-1] != entry["active"]):
            active_order.append(entry["active"])
    assert active_order == schedule["panels"]
    assert [entry["duration"] for entry in entries if entry["active"] is None] == [1000] * 4
    assert entries[-1]["active"] is None  # Includes the gap across the GIF loop seam.
    width, height = schedule["size"]
    boxes = [(x, y, x + width, y + height) for x, y in schedule["positions"]]

    with Image.open(ROOT / "docs/media/overview.gif") as gif:
        assert gif.info["loop"] == 0
        gif.seek(gif.n_frames - 1)
        completed = gif.convert("RGB")
        final_hashes = [sha256(completed.crop(box).tobytes()).digest() for box in boxes]
        elapsed = 0
        for index in range(gif.n_frames):
            gif.seek(index)
            entry = entries[bisect_right(ends, elapsed)]
            frame = gif.convert("RGB")
            for panel, box, expected in zip(schedule["panels"], boxes, final_hashes):
                if panel != entry["active"]:
                    assert sha256(frame.crop(box).tobytes()).digest() == expected, (index, panel)
            elapsed += gif.info["duration"]
        assert elapsed == total, (elapsed, total)

    for name in ("pick", "width", "rectangle", "measure", "stretch", "move", "copy", "contour", "cleanup"):
        with Image.open(ROOT / f"docs/media/{name}.gif") as gif:
            assert gif.info["loop"] == 0
            gif.seek(gif.n_frames - 1)
            assert gif.info["duration"] >= 3000, name
    print("Passed: infinite GIF loops, 3 s standalone holds, 2x2 grid order, 1 s gaps,")
    print("and every inactive panel stays pixel-identical throughout the decoded overview GIF.")


if __name__ == "__main__":
    main()
