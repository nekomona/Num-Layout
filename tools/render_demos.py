"""Capture the synthetic browser scenes and assemble documentation GIFs."""

import argparse
from pathlib import Path
import re

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def save_gif(paths, durations, destination):
    # One palette avoids color flicker and permits compact frame deltas.
    samples = Image.new("RGB", (64 * 10, 64 * ((len(paths) + 9) // 10)))
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            samples.paste(image.convert("RGB").resize((64, 64), Image.Resampling.NEAREST), ((index % 10) * 64, (index // 10) * 64))
    # Preserve the exact highlight/text colors even when thin strokes are rare
    # in the sampled images; averaged thumbnails would wash those colors out.
    source = (ROOT / "docs/demo/app.js").read_text(encoding="utf-8") + (ROOT / "docs/demo/style.css").read_text(encoding="utf-8")
    colors = sorted(set(re.findall(r"#[0-9a-fA-F]{6}\b", source)))
    assert len(colors) < 128
    count = 256 - len(colors)
    palette = samples.quantize(colors=count)
    entries = palette.getpalette()
    for index, color in enumerate(colors, count):
        entries[index * 3:index * 3 + 3] = bytes.fromhex(color[1:])
    palette.putpalette(entries)
    frames = []
    for path in paths:
        with Image.open(path) as image:
            frames.append(image.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE))
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Use an installed browser channel, e.g. msedge")
    parser.add_argument("--only", help="Comma-separated scene IDs; defaults to every scene")
    args = parser.parse_args()
    output = ROOT / "docs" / "media"
    scratch = ROOT / "artifacts" / "demo-frames"
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    all_paths, all_durations = {}, {}
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel=args.channel, headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 650}, device_scale_factor=1)
        page.goto((ROOT / "docs/demo/index.html").as_uri() + "?export=1")
        page.wait_for_function("window.NumericDemo")
        scenes = page.evaluate("NumericDemo.tools")
        selected = args.only.split(",") if args.only else [scene["id"] for scene in scenes]
        unknown = set(selected) - {scene["id"] for scene in scenes}
        if unknown:
            raise ValueError(f"Unknown scenes: {sorted(unknown)}")
        for scene in scenes:
            name = scene["id"]
            if name not in selected:
                continue
            directory = scratch / name
            directory.mkdir(exist_ok=True)
            paths, durations = [], []
            page.evaluate("id => NumericDemo.show(id, 0, {}, 0)", name)
            timeline = page.evaluate("NumericDemo.timeline")
            for step in range(len(scene["steps"])):
                frame_count = (timeline[step]["duration"] + 99) // 100
                for frame in range(frame_count + 1):
                    page.evaluate("([id, step, fraction]) => NumericDemo.show(id, step, {}, fraction)",
                                  [name, step, frame / frame_count])
                    path = directory / f"{step:02d}-{frame:02d}.png"
                    page.locator("#capture").screenshot(path=path)
                    paths.append(path)
                    durations.append(100)
            durations[-1] = 1500
            save_gif(paths, durations, output / f"{name}.gif")
            all_paths[name], all_durations[name] = paths, durations
            print(f"Rendered {name}: {len(paths)} frames", flush=True)
        browser.close()
    overview = ["width", "copy", "contour"]
    if all(name in all_paths for name in overview):
        save_gif([path for name in overview for path in all_paths[name]],
                 [duration for name in overview for duration in all_durations[name]],
                 output / "overview.gif")


if __name__ == "__main__":
    main()
