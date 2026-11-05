"""Capture the synthetic browser scenes and assemble documentation GIFs."""

import argparse
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OVERVIEW = ("pick", "width", "measure", "copy")
LOOP_WAIT = 3000
OVERVIEW_GAP = 1000


def overview_schedule(all_paths, all_durations):
    """A single changing panel, followed by a one-second all-still interval."""
    for active in OVERVIEW:
        for path, duration in zip(all_paths[active][:-1], all_durations[active][:-1]):
            yield active, path, duration
        yield None, all_paths[active][-1], OVERVIEW_GAP


def render_overview(all_paths, all_durations, scratch, destination):
    directory = scratch / "overview"
    directory.mkdir(exist_ok=True)
    panel_width, gutter = 600, 12
    with Image.open(all_paths[OVERVIEW[0]][0]) as first:
        panel_height = round(first.height * panel_width / first.width)
    size = (panel_width, panel_height)
    positions = [(gutter + (i % 2) * (panel_width + gutter),
                  gutter + (i // 2) * (panel_height + gutter)) for i in range(4)]
    canvas = Image.new("RGB", (panel_width * 2 + gutter * 3, panel_height * 2 + gutter * 3), "#101a23")
    # Inactive panels hold their completed result throughout the entire cycle.
    for name, position in zip(OVERVIEW, positions):
        with Image.open(all_paths[name][-1]) as frame:
            canvas.paste(frame.convert("RGB").resize(size, Image.Resampling.LANCZOS), position)
    paths, durations, manifest = [], [], []
    for index, (active, source, duration) in enumerate(overview_schedule(all_paths, all_durations)):
        frame = canvas.copy()
        if active:
            x, y = positions[OVERVIEW.index(active)]
            with Image.open(source) as panel:
                frame.paste(panel.convert("RGB").resize(size, Image.Resampling.LANCZOS), (x, y))
            ImageDraw.Draw(frame).rectangle((x - 3, y - 3, x + panel_width + 2, y + panel_height + 2), outline="#e989f1", width=2)
        path = directory / f"{index:04d}.png"
        frame.save(path)
        paths.append(path)
        durations.append(duration)
        manifest.append({"frame": path.name, "active": active, "duration": duration})
    (directory / "schedule.json").write_text(json.dumps({"panels": OVERVIEW, "size": size,
        "positions": positions, "frames": manifest}, indent=2) + "\n", encoding="utf-8")
    save_gif(paths, durations, destination)
    print(f"Rendered 2x2 overview: {len(paths)} frames; one active panel, 1 s gaps", flush=True)


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
                duration = timeline[step]["duration"]
                for frame, time in enumerate(range(0, duration, 100)):
                    page.evaluate("([id, step, fraction]) => NumericDemo.show(id, step, {}, fraction)",
                                  [name, step, time / duration])
                    path = directory / f"{step:02d}-{frame:02d}.png"
                    page.locator("#capture").screenshot(path=path)
                    paths.append(path)
                    durations.append(min(100, duration - time))
            page.evaluate("([id, step]) => NumericDemo.show(id, step)", [name, len(scene["steps"]) - 1])
            path = directory / "final.png"
            page.locator("#capture").screenshot(path=path)
            paths.append(path)
            durations.append(LOOP_WAIT)
            save_gif(paths, durations, output / f"{name}.gif")
            all_paths[name], all_durations[name] = paths, durations
            print(f"Rendered {name}: {len(paths)} frames", flush=True)
        browser.close()
    if all(name in all_paths for name in OVERVIEW):
        render_overview(all_paths, all_durations, scratch, output / "overview.gif")


if __name__ == "__main__":
    main()
