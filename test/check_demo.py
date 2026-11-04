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


if __name__ == "__main__":
    main()
