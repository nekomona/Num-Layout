"""Check synthetic demo sequences, inputs, labels, and playback controls."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel")
    args = parser.parse_args()
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel=args.channel, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        url = (ROOT / "docs/demo/index.html").as_uri()
        page.goto(url)
        page.wait_for_function("window.NumericDemo")
        scenes = {s["id"]: s for s in page.evaluate("NumericDemo.tools")}

        def show(name, phase, fraction=1, values=None):
            return page.evaluate("([id,i,v,f]) => NumericDemo.show(id,i,v,f)",
                                 [name, scenes[name]["phases"].index(phase), values or {}, fraction])

        def state():
            return page.evaluate("NumericDemo.state")

        def pointer():
            p = page.locator('[data-role="pointer"]')
            return tuple(float(p.get_attribute("data-" + axis)) for axis in ("x", "y"))

        def balloon():
            return page.locator('[data-role="balloon"]').text_content()

        for name, scene in scenes.items():
            page.locator(f'[data-tool="{name}"]').click()
            page.wait_for_function("id => NumericDemo.state.tool === id", arg=name)
            assert state()["playing"] and state()["loop"] and state()["step"] == 0
            for index in range(1, len(scene["steps"])):
                page.locator("#next").click()
                assert state()["step"] == index
            assert page.locator("#next").is_disabled()
            page.locator("#reset").click()
            assert state()["step"] == 0 and state()["playing"]
            show(name, "start", 0)
            assert pointer() == (44, 2)
            assert page.locator('[data-role="balloon"]').count() == 0
            for index in range(len(scene["steps"]) - 1):
                page.evaluate("([id,i]) => NumericDemo.show(id,i)", [name, index])
                previous = pointer()
                page.evaluate("([id,i]) => NumericDemo.show(id,i,{},0)", [name, index + 1])
                assert pointer() == previous, (name, index)
            show(name, "confirm")
            assert pointer() == (44, 2)
            assert page.locator('[data-role="balloon"]').count() == 0
            assert page.locator(".typed-value").inner_text() == "Done."
            assert "Return pointer" not in page.locator("#steps").inner_text()

        expected = {"pick": ["S", "Click", "J", "Click", "Click", "Enter"],
                    "width": ["P", "Click", "J", "Enter"], "rectangle": ["R", "Click", "J", "Enter"],
                    "measure": ["K", "Click", "J", "Enter"], "stretch": ["S", "Click", "J", "Enter"],
                    "move": ["M", "Click", "J", "Enter"], "copy": ["C", "Click", "N", "Enter", "J", "Enter"]}
        for name, sequence in expected.items():
            show(name, "start", 0)
            phases = page.evaluate("NumericDemo.timeline")
            assert [e["key"] for p in phases for e in p["events"] if e["type"] != "character"] == sequence
            for p in phases:
                for i, event in enumerate(p["events"]):
                    if event["type"] == "character":
                        continue
                    next_start = p["events"][i + 1]["start"] if i + 1 < len(p["events"]) else p["duration"]
                    assert next_start - event["end"] >= 1200
                if p.get("select"):
                    assert next(e["start"] for e in p["events"] if e["type"] == "select") >= p["moveStart"] + p["moveDuration"]

        for name, phase in (("pick", "first"), ("pick", "second"), ("stretch", "start"), ("contour", "pivot")):
            show(name, phase, 0)
            a = state()["animation"]
            points = []
            for fraction in (0, .5, 1):
                show(name, phase, (a["moveStart"] + fraction * a["moveDuration"]) / a["duration"])
                assert page.locator('[data-role="hover-highlight"]').count() == (1 if fraction == 1 else 0)
                assert not state()["animation"]["selected"]
                points.append(pointer())
            assert points[0] != points[1] != points[2]
        for phase, size, label in (("activate", "4", "STRETCH LENGTH"), ("first", "12", "12 [1 edge]  |  STRETCH LENGTH"), ("second", "3", "3 [2 edges]  |  STRETCH LENGTH")):
            show("pick", phase)
            assert page.locator('[data-role="stretch-preview"]').get_attribute("data-size") == size
            assert balloon() == label
        show("pick", "second", values={"kind": "length"})
        assert balloon() == "12 [1 edge]  |  STRETCH LENGTH"
        show("measure", "start", 0)
        assert page.locator('[data-role="ruler"]').count() == 0
        show("measure", "aim")
        assert page.locator('[data-role="ruler"]').count() == 1
        show("copy", "aim")
        assert page.locator('[data-role="copy-preview"]').count() == 1
        show("width", "input", values={"value": 3})
        path = page.locator('[data-role="extended-path"] rect')
        assert path.get_attribute("x") == "120"  # Includes the original segment at x=2.
        assert path.get_attribute("width") == "435"
        assert path.get_attribute("height") == "45"
        for name, label in {"width": "2  |  PATH WIDTH", "rectangle": "12,6  |  RECT SIZE X,Y", "measure": "20  |  MEASUREMENT LENGTH", "stretch": "18  |  STRETCH LENGTH", "move": "12,6  |  MOVE DELTA X,Y", "copy": "9  |  COPY DISTANCE [3 copies]"}.items():
            show(name, "input")
            assert balloon() == label
        show("contour", "pivot", .7)
        assert balloon() == "PIVOT RECT  2  [0/4 edges]"
        assert "four bounding edges" in page.locator("#scene-description").inner_text()
        show("contour", "side")
        assert balloon() == "CONTOUR OUTSIDE  2"
        for mode in ("relative", "absolute"):
            show("move", "confirm", 0, {"mode": mode})
            a = state()["animation"]
            enter = next(e for e in a["events"] if e["key"] == "Enter")
            show("move", "confirm", (enter["start"] - 1) / a["duration"], {"mode": mode})
            assert page.locator('[data-role="move-source"]').count() == 1
            show("move", "confirm", (enter["start"] + 1) / a["duration"], {"mode": mode})
            assert page.locator('[data-role="move-source"]').count() == 0
            assert page.locator('[data-role="move-target"]').count() == 1

        decimal = {"value": "2.345678"}
        show("width", "input", 0, decimal)
        assert state()["values"]["value"] == 2.3457
        assert page.locator("#field-value").input_value() == "2.3457"
        a = state()["animation"]
        typed, previous = "", None
        for event in a["events"]:
            show("width", "input", (event["start"] + 60) / a["duration"], decimal)
            assert page.locator(".keycap.pressed").inner_text() == event["key"]
            if event["type"] == "character":
                typed += event["character"]
                if previous is not None:
                    assert event["start"] - previous == 260
                previous = event["start"]
            assert page.locator(".typed-value").get_attribute("data-typed") == typed
            assert balloon() == (typed + "  |  " if typed else "") + "PATH WIDTH"
            show("width", "input", (event["end"] + 20) / a["duration"], decimal)
            assert page.locator(".keycap.pressed").count() == 0
        show("move", "input", values={"value": "-1.23456,6.78909"})
        assert state()["values"]["value"] == [-1.2346, 6.7891]
        page.locator("#field-value").fill("12,6")
        page.locator("#field-value").press("Enter")
        assert state()["playing"] and state()["step"] == 0 and state()["values"]["value"] == [12, 6]
        page.locator("#field-mode").select_option("absolute")
        assert state()["values"]["mode"] == "absolute" and state()["step"] == 0
        show("move", "input", values={"value": "12,6", "mode": "absolute"})
        assert "(12, 6)" in page.locator("#scene-result").inner_text()
        assert balloon() == "12,6  |  MOVE ABSOLUTE X,Y"
        show("move", "input", 0, {"mode": "absolute"})
        a = state()["animation"]
        show("move", "input", (a["events"][0]["start"] + 20) / a["duration"], {"mode": "absolute"})
        assert balloon() == "MOVE ABSOLUTE X"
        page.locator("#field-value").fill("12,")
        page.locator("#field-value").press("Enter")
        assert page.locator("#error").inner_text() and not state()["playing"]
        show("copy", "input")
        for value in ("2.5", "2.00001"):
            page.locator("#field-count").fill(value)
            page.locator("#field-count").press("Enter")
            assert "whole number" in page.locator("#error").inner_text()
        show("width", "input")
        page.locator("#field-value").fill("3.123456")
        page.locator("#field-value").press("Tab")
        assert state()["values"]["value"] == 3.1235 and state()["step"] == 0 and state()["playing"]
        show("width", "input")
        page.locator("#field-value").fill("2.5")
        page.wait_for_timeout(1600)
        page.locator("#field-value").fill("2.75")
        page.wait_for_timeout(1600)
        assert state()["values"]["value"] == 2
        page.wait_for_function("NumericDemo.state.values.value === 2.75")
        assert state()["playing"] and state()["step"] == 0
        assert page.locator("#field-value").evaluate("el => el === document.activeElement")

        show("width", "start", 0)
        page.evaluate("NumericDemo.advance(400)")
        page.locator("#speed").select_option("2")
        assert state()["position"] == 400
        page.evaluate("NumericDemo.advance(200)")
        assert state()["position"] == 800
        page.locator("#play").click()
        page.wait_for_function("NumericDemo.state.position > 850")
        page.locator("#play").click()
        paused = state()["position"]
        page.wait_for_timeout(100)
        assert not state()["playing"] and state()["position"] == paused
        page.locator("#play").click()
        page.wait_for_function("p => NumericDemo.state.position > p", arg=paused)
        page.locator("#play").click()
        show("width", "confirm")
        page.evaluate("NumericDemo.advance(2999)")
        assert state()["holding"] and state()["holdElapsed"] == 2999
        assert page.locator(".typed-value").inner_text() == "Done."
        page.evaluate("NumericDemo.advance(1)")
        assert state()["position"] == 0 and not state()["holding"]
        show("width", "confirm")
        page.locator("#loop").click()
        page.evaluate("NumericDemo.advance(4000)")
        assert not state()["playing"] and not state()["holding"] and not state()["loop"]
        page.locator('[data-tool="copy"]').click()
        page.wait_for_function("NumericDemo.state.tool === 'copy'")
        assert state()["step"] == 0 and state()["playing"] and state()["loop"] and state()["speed"] == 2
        page.locator("#speed").select_option("1")
        # An unfinished input debounce cannot restart a subsequently selected tool.
        page.locator("#field-value").fill("8")
        page.locator('[data-tool="width"]').click()
        page.wait_for_function("NumericDemo.state.tool === 'width'")
        page.locator("#play").click()
        paused = state()["position"]
        page.wait_for_timeout(3100)
        assert state()["tool"] == "width" and state()["position"] == paused and not state()["playing"]

        screenshots = ROOT / "artifacts/demo-checks"
        screenshots.mkdir(parents=True, exist_ok=True)
        show("copy", "input")
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
    print("Passed: nine scenes, command order, hover/cursor continuity, native balloon text,")
    print("typing/pause timing, rounding/validation, all auto-apply paths, debounce cancellation,")
    print("speed, pause/resume, looping, tool switches, deep links and responsive layouts.")


if __name__ == "__main__":
    main()
