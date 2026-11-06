"""Build the browser-readable guide from its canonical Markdown source."""

from html import escape
from pathlib import Path
import re

import markdown
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parents[1]


def unicode_slug(value, separator):
    value = re.sub(r"[^\w\u3400-\u9fff\- ]", "", value.strip().lower())
    return re.sub(r"[-\s]+", separator, value).strip(separator)


MARKDOWN_EXTENSIONS = ["tables", "fenced_code", TocExtension(slugify=unicode_slug)]


def document_page(
    body,
    title="User guide",
    license_href="../../LICENSE",
    lang="en",
    alternate_href="guide.html",
    current_href="guide.html",
    lab_label="Interactive lab",
    license_label="MIT license",
    home_href="../site/index.html",
    lab_href="index.html",
    language_script="../site/language.js",
):
    is_zh = lang.startswith("zh")
    english_href = alternate_href if is_zh else current_href
    chinese_href = current_href if is_zh else alternate_href
    language_link = (
        '<span class="language-switch" aria-label="Language">'
        f'<a href="{escape(english_href, quote=True)}" data-language-choice="en" '
        f'aria-current="{"page" if not is_zh else "false"}">EN</a>'
        f'<a href="{escape(chinese_href, quote=True)}" data-language-choice="zh" '
        f'aria-current="{"page" if is_zh else "false"}">中文</a></span>'
        if alternate_href else ""
    )
    page = '''<!doctype html>
<html lang="__LANG__"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="language-current" content="__LANGUAGE_CURRENT__">__ALTERNATE_META__
<title>Numeric Layout Assist · __TITLE__</title><link rel="stylesheet" href="style.css">
<style>.guide{max-width:1020px;margin:45px auto;padding:0 28px 60px;line-height:1.8}.guide h1{font-size:40px;line-height:1.2;margin-bottom:24px}.guide h2{margin-top:48px;margin-bottom:18px}.guide h3{margin-top:35px}.guide p,.guide li{font-size:15px}.guide pre{overflow:auto;background:#17232e;color:#dce8f0;padding:22px;border-radius:8px;font-size:13px}.guide code{font-family:Consolas,monospace}.guide table{display:block;overflow:auto;border-collapse:collapse;width:100%;font-size:13px}.guide th,.guide td{text-align:left;border-bottom:1px solid #d9d9d0;padding:12px;min-width:120px}.guide th{background:#ebe7f1}.guide a{color:#6b45b9}.guide img{max-width:100%;height:auto}.guide h2,.guide h3{scroll-margin-top:25px}.language-switch a{padding:6px 9px;border-radius:4px;font-size:11px;line-height:1}.language-switch a[aria-current="page"]{background:#eee8f7}</style>
</head><body><header class="topbar"><a class="brand" href="__HOME_HREF__"><span class="brand-mark">N<span>↗</span></span> NUMERIC LAYOUT ASSIST</a><nav>__LANGUAGE_LINK__<a href="__LAB_HREF__">__LAB_LABEL__ ↗</a><a href="__LICENSE__">__LICENSE_LABEL__ ↗</a></nav></header><main class="guide">'''
    page += body + '</main></body></html>\n'
    values = {
        "__TITLE__": escape(title),
        "__LICENSE__": escape(license_href, quote=True),
        "__LANG__": escape(lang, quote=True),
        "__LANGUAGE_CURRENT__": "zh" if lang.startswith("zh") else "en",
        "__ALTERNATE_META__": (f'<meta name="language-alternate" content="{escape(alternate_href, quote=True)}">'
                              if alternate_href else ""),
        "__LANGUAGE_LINK__": language_link,
        "__LAB_LABEL__": escape(lab_label),
        "__LICENSE_LABEL__": escape(license_label),
        "__HOME_HREF__": escape(home_href, quote=True),
        "__LAB_HREF__": escape(lab_href, quote=True),
    }
    for marker, value in values.items():
        page = page.replace(marker, value)
    return page.replace("</head>", f'<script src="{escape(language_script, quote=True)}"></script>\n</head>')


def main():
    guides = (
        ("numeric_assist_guide.md", "guide.html", "User guide", "en", "guide.zh-CN.html", "Interactive lab", "MIT license"),
        ("numeric_assist_guide.zh-CN.md", "guide.zh-CN.html", "使用指南", "zh-CN", "guide.html", "交互演示", "MIT 许可证"),
    )
    for source_name, output_name, title, lang, alternate, lab_label, license_label in guides:
        source = (ROOT / "docs" / source_name).read_text(encoding="utf-8")
        body = markdown.markdown(source, extensions=MARKDOWN_EXTENSIONS)
        # Markdown links are relative to docs/; the HTML mirror lives in docs/demo/.
        def link(match):
            target = match.group(1)
            if target.startswith(("#", "https://", "http://")):
                return match.group(0)
            if target in ("../README.md", "../README.zh-CN.md"):
                return 'href="index.html"'
            return 'href="../' + target + '"'
        body = re.sub(r'href="([^"]+)"', link, body)
        page = document_page(
            body,
            title=title,
            lang=lang,
            alternate_href=alternate,
            current_href=output_name,
            lab_label=lab_label,
            license_label=license_label,
        )
        destination = ROOT / "docs" / "demo" / output_name
        destination.write_text(page, encoding="utf-8")
        print(f"Built docs/demo/{output_name} from docs/{source_name}")


if __name__ == "__main__":
    main()
