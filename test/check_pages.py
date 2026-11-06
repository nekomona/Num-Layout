"""Validate the public Pages artifact, optionally under a repository URL prefix."""

import argparse
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from threading import Thread
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "artifacts" / "pages"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        for key in ("href", "src"):
            if key in attributes:
                self.targets.append(attributes[key])


def check_artifact():
    expected = {"index.html", "app.js", "style.css", "guide.html", "guide.zh-CN.html",
                "overview.html", "overview.zh-CN.html", "contributing.html",
                "contributing.zh-CN.html",
                "publishing.html", "testing.html", "recordings.html", "license.html", ".nojekyll"}
    expected.update("media/" + path.name for path in (ROOT / "docs/media").iterdir()
                    if path.suffix in (".gif", ".svg", ".png", ".webp"))
    actual = {path.relative_to(SITE).as_posix() for path in SITE.rglob("*") if path.is_file()}
    assert actual == expected, (actual - expected, expected - actual)
    assert all(not path.is_symlink() for path in SITE.rglob("*"))
    pages = {}
    for path in SITE.glob("*.html"):
        parsed = Links()
        parsed.feed(path.read_text(encoding="utf-8"))
        pages[path] = parsed
    scenes = set(re.findall(r'id:\s*"([^"]+)"', (SITE / "app.js").read_text(encoding="utf-8")))
    for path, parsed in pages.items():
        for value in parsed.targets:
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            assert not url.path.startswith("/"), (path.name, value, "root-relative URL")
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(SITE), (path.name, value, "outside artifact")
            assert target.is_file(), (path.name, value, "missing target")
            if url.fragment and target in pages:
                valid_ids = pages[target].ids | (scenes if target.name == "index.html" else set())
                assert unquote(url.fragment) in valid_ids, (path.name, value, "missing anchor")
    print(f"Pages artifact passed: {len(actual)} public files; all internal links and anchors resolve.")


def check_browser(channel):
    from playwright.sync_api import sync_playwright
    prefix = "/preview-project/"

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if not self.path.startswith(prefix):
                self.send_error(404)
                return
            self.path = "/" + self.path[len(prefix):]
            super().do_GET()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(SITE)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}{prefix}"
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(channel=channel, headless=True)
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(base + "?lang=en#copy")
            assert response.status == 200
            page.wait_for_function("window.NumericDemo && NumericDemo.state.tool === 'copy'")
            page.get_by_role("button", name="Next step").click()
            assert page.evaluate("NumericDemo.state.step") == 1
            page.get_by_role("link", name="User guide").click()
            assert page.url == base + "guide.html"
            assert page.locator("#installation").count() == 1
            page.locator('.topbar a[href="guide.zh-CN.html"]').click()
            assert page.url == base + "guide.zh-CN.html"
            assert page.locator("h1").inner_text() == "Numeric Layout Assist — 用户教程"
            assert page.locator("#安装").count() == 1
            page.locator('.topbar a[href="guide.html"]').click()
            assert page.url == base + "guide.html"
            for document in ("overview.html", "overview.zh-CN.html", "contributing.html",
                             "contributing.zh-CN.html",
                             "testing.html", "publishing.html", "recordings.html", "license.html"):
                assert page.goto(base + document).status == 200
                assert page.locator("main").inner_text()
            assert page.request.get(base + "media/overview.gif").status == 200
            assert not errors, errors
            browser.close()
        print("Pages browser check passed beneath a repository URL prefix.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--channel")
    args = parser.parse_args()
    check_artifact()
    if args.browser:
        check_browser(args.channel)


if __name__ == "__main__":
    main()
