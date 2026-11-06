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
    project_name = "定数绘版" if is_zh else "Num-Layout"
    brand_name = (
        '定数绘版 <span class="brand-light">Num-Layout</span>'
        if is_zh else "Num-Layout"
    )
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
<title>__PROJECT_NAME__ · __TITLE__</title><link rel="stylesheet" href="style.css">
<style>.guide{max-width:1020px;margin:45px auto;padding:0 28px 60px;line-height:1.85}.guide h1{font-size:38px;line-height:1.25;margin-bottom:24px}.guide h2{font-size:28px;line-height:1.3;margin-top:52px;margin-bottom:18px}.guide h3{font-size:20px;line-height:1.4;margin-top:38px}.guide p,.guide li{font-size:16px}.guide pre{overflow:auto;background:#17232e;color:#dce8f0;padding:22px;border-radius:8px;font-size:13px}.guide code{font-family:Consolas,monospace}.guide table{display:block;overflow:auto;border-collapse:collapse;width:100%;font-size:14px}.guide th,.guide td{text-align:left;border-bottom:1px solid #d9d9d0;padding:12px;min-width:120px}.guide th{background:#ebe7f1}.guide a{color:#6b45b9}.guide img{max-width:100%;height:auto}.guide h2,.guide h3{scroll-margin-top:25px}.language-switch a{padding:6px 9px;border-radius:4px;font-size:12px;line-height:1}.language-switch a[aria-current="page"]{background:#eee8f7}</style>
</head><body><header class="topbar"><a class="brand" href="__HOME_HREF__"><span class="brand-mark" aria-hidden="true">J</span> __BRAND_NAME__</a><nav>__LANGUAGE_LINK__<a class="github-link" href="https://github.com/nekomona/Num-Layout" aria-label="Num-Layout on GitHub"><svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg><span>GitHub ↗</span></a><a href="__LAB_HREF__">__LAB_LABEL__ ↗</a><a href="__LICENSE__">__LICENSE_LABEL__ ↗</a></nav></header><main class="guide">'''
    page += body + '</main></body></html>\n'
    values = {
        "__TITLE__": escape(title),
        "__PROJECT_NAME__": escape(project_name),
        "__BRAND_NAME__": brand_name,
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
            home_href=(
                "../site/index.zh-CN.html"
                if lang.startswith("zh")
                else "../site/index.html"
            ),
        )
        destination = ROOT / "docs" / "demo" / output_name
        destination.write_text(page, encoding="utf-8")
        print(f"Built docs/demo/{output_name} from docs/{source_name}")


if __name__ == "__main__":
    main()
