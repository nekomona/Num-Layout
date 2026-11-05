"""Check documentation demo interactions in a local, isolated browser."""

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed browser channel, e.g. msedge")
    args = parser.parse_args()
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel=args.channel, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        url = (ROOT / "docs/demo/index.html").as_uri()
        page.goto(url)
        page.wait_for_function("window.NumericDemo")
        for scene in page.evaluate("NumericDemo.tools"):
            page.locator(f'[data-tool="{scene["id"]}"]').click()
            page.wait_for_function("id => NumericDemo.state.tool === id", arg=scene["id"])
            for index in range(1, len(scene["steps"])):
                page.get_by_role("button", name="Next step").click()
                assert page.evaluate("NumericDemo.state.step") == index
            assert page.get_by_role("button", name="Next step").is_disabled()
            assert page.locator("#scene-result").inner_text()
            page.get_by_role("button", name="Reset").click()
            assert page.evaluate("NumericDemo.state.step") == 0

        for scene, index in (("pick", 0), ("pick", 2), ("stretch", 0), ("contour", 1)):
            pointers = []
            for fraction in (0, 0.5, 0.6):
                page.evaluate("([id, step, fraction]) => NumericDemo.show(id, step, {}, fraction)",
                              [scene, index, fraction])
                assert page.locator('[data-role="hover-highlight"]').count() == (1 if fraction >= 0.55 else 0)
                pointer = page.locator('[data-role="pointer"]')
                pointers.append((pointer.get_attribute("data-x"), pointer.get_attribute("data-y")))
            assert pointers[0] != pointers[1] != pointers[2]

        decimal = {"value": "2.345678"}
        page.evaluate("data => NumericDemo.show('width', 1, data, 0)", decimal)
        assert page.evaluate("NumericDemo.state.values.value") == 2.3457
        assert page.locator("#field-value").input_value() == "2.3457"
        phase = page.evaluate("NumericDemo.timeline[1]")
        assert phase["input"] == "2.3457"
        typed = ""
        for event in phase["events"]:
            page.evaluate("([data, fraction]) => NumericDemo.show('width', 1, data, fraction)",
                          [decimal, (event["start"] + 60) / phase["duration"]])
            assert page.locator("#input-strip").get_attribute("data-pressed") == event["key"]
            assert page.locator(".keycap.pressed").inner_text() == event["key"]
            if event["type"] == "character":
                typed += event["character"]
            assert page.locator(".typed-value").get_attribute("data-typed") == typed
            page.evaluate("([data, fraction]) => NumericDemo.show('width', 1, data, fraction)",
                          [decimal, (event["end"] + 20) / phase["duration"]])
            assert page.locator(".keycap.pressed").count() == 0
        page.evaluate("NumericDemo.show('move', 1, {value:'-1.23456,6.78909'}, 1)")
        assert page.evaluate("NumericDemo.state.values.value") == [-1.2346, 6.7891]
        assert page.locator("#field-value").input_value() == "-1.2346,6.7891"

        page.locator('[data-tool="move"]').click()
        page.wait_for_function("NumericDemo.state.tool === 'move'")
        page.locator("#field-value").fill("12,6")
        page.get_by_role("button", name="Update preview").click()
        assert "(22, 15)" in page.locator("#scene-result").inner_text()
        page.locator("#field-mode").select_option("absolute")
        assert "(12, 6)" in page.locator("#scene-result").inner_text()
        page.locator("#field-value").fill("12,")
        page.get_by_role("button", name="Update preview").click()
        assert page.locator("#error").inner_text()
        assert "(12, 6)" in page.locator("#scene-result").inner_text()

        page.locator('[data-tool="copy"]').click()
        page.wait_for_function("NumericDemo.state.tool === 'copy'")
        page.locator("#field-count").fill("4")
        page.get_by_role("button", name="Update preview").click()
        assert "4 preview targets" in page.locator("#scene-result").inner_text()
        page.locator("#field-count").fill("2.5")
        page.get_by_role("button", name="Update preview").click()
        assert "whole number" in page.locator("#error").inner_text()

        page.locator('[data-tool="contour"]').click()
        page.wait_for_function("NumericDemo.state.tool === 'contour'")
        page.locator("#field-side").select_option("inside")
        assert "inside offset" in page.locator("#scene-result").inner_text()
        page.get_by_role("button", name="Play", exact=False).click()
        page.wait_for_function("NumericDemo.state.playing")
        page.get_by_role("button", name="Pause", exact=False).click()
        assert not page.evaluate("NumericDemo.state.playing")

        screenshots = ROOT / "artifacts" / "demo-checks"
        screenshots.mkdir(parents=True, exist_ok=True)
        page.evaluate("NumericDemo.show('copy', 2)")
        page.screenshot(path=screenshots / "desktop.png", full_page=True)
        for width in (390, 768, 1440):
            page.set_viewport_size({"width": width, "height": 950})
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), width
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=screenshots / "mobile.png", full_page=True)
        page.goto(url + "#rectangle")
        page.wait_for_function("NumericDemo.state.tool === 'rectangle'")
        page.goto((ROOT / "docs/demo/guide.html").as_uri())
        assert page.locator("h1").inner_text() == "Numeric Layout Assist — user guide"
        assert page.locator("#installation").count() == 1
        assert not errors, errors
        browser.close()
    print("Passed: nine tools, step/reset controls, input validation, relative/absolute Move,")
    print("Copy count, Contour direction, play/pause, deep links, guide and three viewport sizes.")
    print("Animation checks: pointer arrival before highlights, key-down/key-up timing,")
    print("character-by-character entry, and four-decimal rounding for scalar and signed X/Y values.")


if __name__ == "__main__":
    main()
