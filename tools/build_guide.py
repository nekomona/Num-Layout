"""Build the browser-readable guide from its canonical Markdown source."""

from html import escape
from pathlib import Path
import re

import markdown

ROOT = Path(__file__).resolve().parents[1]


def document_page(body, title="User guide", license_href="../../LICENSE"):
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Numeric Layout Assist · __TITLE__</title><link rel="stylesheet" href="style.css">
<style>.guide{max-width:1020px;margin:45px auto;padding:0 28px 60px;line-height:1.8}.guide h1{font-size:40px;line-height:1.2;margin-bottom:24px}.guide h2{margin-top:48px;margin-bottom:18px}.guide h3{margin-top:35px}.guide p,.guide li{font-size:15px}.guide pre{overflow:auto;background:#17232e;color:#dce8f0;padding:22px;border-radius:8px;font-size:13px}.guide code{font-family:Consolas,monospace}.guide table{display:block;overflow:auto;border-collapse:collapse;width:100%;font-size:13px}.guide th,.guide td{text-align:left;border-bottom:1px solid #d9d9d0;padding:12px;min-width:120px}.guide th{background:#ebe7f1}.guide a{color:#6b45b9}.guide img{max-width:100%;height:auto}.guide h2,.guide h3{scroll-margin-top:25px}</style>
</head><body><header class="topbar"><a class="brand" href="index.html"><span class="brand-mark">N<span>↗</span></span> NUMERIC LAYOUT ASSIST</a><nav><a href="index.html">Interactive lab ↗</a><a href="__LICENSE__">MIT license ↗</a></nav></header><main class="guide">'''
    page += body + '</main></body></html>\n'
    return page.replace('__TITLE__', escape(title)).replace('__LICENSE__', escape(license_href, quote=True))


def main():
    source = (ROOT / "docs/numeric_assist_guide.md").read_text(encoding="utf-8")
    body = markdown.markdown(source, extensions=["tables", "fenced_code", "toc"])
    # Markdown links are relative to docs/; the HTML mirror lives in docs/demo/.
    def link(match):
        target = match.group(1)
        if target.startswith(("#", "https://", "http://")):
            return match.group(0)
        if target == "../README.md":
            return 'href="index.html"'
        return 'href="../' + target + '"'
    body = re.sub(r'href="([^"]+)"', link, body)
    page = document_page(body)
    (ROOT / "docs/demo/guide.html").write_text(page, encoding="utf-8")
    print("Built docs/demo/guide.html from docs/numeric_assist_guide.md")


if __name__ == "__main__":
    main()
