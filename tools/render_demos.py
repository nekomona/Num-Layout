"""Capture the synthetic browser scenes and assemble documentation GIFs."""

import argparse
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def save_gif(paths, durations, destination):
    frames = []
    for path in paths:
        with Image.open(path) as image:
            frames.append(image.convert("RGB").quantize(colors=128))
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=2)


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
            for step in range(len(scene["steps"])):
                for frame in range(6):
                    page.evaluate("([id, step, fraction]) => NumericDemo.show(id, step, {}, fraction)",
                                  [name, step, frame / 5])
                    path = directory / f"{step:02d}-{frame:02d}.png"
                    page.locator("#capture").screenshot(path=path)
                    paths.append(path)
                    durations.append(180 if frame < 5 else 550)
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
