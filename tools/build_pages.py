"""Build a repository-independent Pages artifact from public files only."""

from html import escape, unescape
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
from urllib.parse import urlsplit, urlunsplit

import markdown

from build_guide import MARKDOWN_EXTENSIONS, ROOT, document_page

OUTPUT = ROOT / "artifacts" / "pages"
DOCUMENTS = {
    "README.md": ("overview.html", "Project overview", "en"),
    "README.zh-CN.md": ("overview.zh-CN.html", "项目概览", "zh-CN"),
    "docs/numeric_assist_guide.md": ("guide.html", "User guide", "en"),
    "docs/numeric_assist_guide.zh-CN.md": ("guide.zh-CN.html", "用户教程", "zh-CN"),
    "CONTRIBUTING.md": ("contributing.html", "Contributing", "en"),
    "CONTRIBUTING.zh-CN.md": ("contributing.zh-CN.html", "参与贡献", "zh-CN"),
    "docs/PUBLISHING.md": ("publishing.html", "Pages deployment", "en"),
    "test/README.md": ("testing.html", "Testing", "en"),
    "test/DEMO_MEDIA.md": ("recordings.html", "Demo recordings", "en"),
}


def rewrite_links(content, source, mapping):
    def replace(match):
        attribute, target = match.groups()
        parsed = urlsplit(unescape(target))
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        path = posixpath.normpath(str(PurePosixPath(source).parent / parsed.path))
        if path not in mapping:
            raise ValueError(f"Unpackaged link in {source}: {target}")
        replacement = urlsplit(mapping[path])
        destination = urlunsplit(("", "", replacement.path, parsed.query, parsed.fragment or replacement.fragment))
        return f'{attribute}="{escape(destination, quote=True)}"'
    return re.sub(r'(href|src)="([^"]+)"', replace, content)


def main():
    media = sorted((ROOT / "docs/media").glob("*"))
    media = [path for path in media if path.suffix in (".gif", ".svg", ".png", ".webp")]
    mapping = {source: target for source, (target, _, _) in DOCUMENTS.items()}
    mapping.update({
        "docs/demo/index.html": "index.html",
        "docs/demo/guide.html": "guide.html",
        "docs/demo/guide.zh-CN.html": "guide.zh-CN.html",
        "docs/demo/style.css": "style.css",
        "docs/demo/app.js": "app.js",
        "LICENSE": "license.html",
        # The language badge leads to the installation instructions on the site.
        "src/numeric_assist.il": "guide.html#installation",
    })
    mapping.update({path.relative_to(ROOT).as_posix(): "media/" + path.name for path in media})

    # This fixed staging directory is always below the ignored artifact root.
    artifact_root = (ROOT / "artifacts").resolve()
    if OUTPUT.is_symlink() or OUTPUT.resolve() != artifact_root / "pages" or artifact_root != ROOT / "artifacts":
        raise RuntimeError("Unexpected Pages output path")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "media").mkdir(parents=True)
    for filename in ("app.js", "style.css"):
        shutil.copyfile(ROOT / "docs/demo" / filename, OUTPUT / filename)
    source = "docs/demo/index.html"
    (OUTPUT / "index.html").write_text(rewrite_links((ROOT / source).read_text(encoding="utf-8"), source, mapping), encoding="utf-8")
    for source, (destination, title, lang) in DOCUMENTS.items():
        body = markdown.markdown((ROOT / source).read_text(encoding="utf-8"), extensions=MARKDOWN_EXTENSIONS)
        body = rewrite_links(body, source, mapping)
        alternates = {
            "overview.html": ("overview.zh-CN.html", "简体中文"),
            "overview.zh-CN.html": ("overview.html", "English"),
            "guide.html": ("guide.zh-CN.html", "简体中文"),
            "guide.zh-CN.html": ("guide.html", "English"),
            "contributing.html": ("contributing.zh-CN.html", "简体中文"),
            "contributing.zh-CN.html": ("contributing.html", "English"),
        }
        alternate_href, alternate_label = alternates.get(destination, ("", ""))
        (OUTPUT / destination).write_text(
            document_page(
                body,
                title,
                "license.html",
                lang=lang,
                alternate_href=alternate_href,
                alternate_label=alternate_label,
                lab_label="Interactive lab" if lang == "en" else "交互演示",
                license_label="MIT license" if lang == "en" else "MIT 许可证",
            ),
            encoding="utf-8",
        )
    license_body = "<h1>MIT License</h1><pre>" + escape((ROOT / "LICENSE").read_text(encoding="utf-8")) + "</pre>"
    (OUTPUT / "license.html").write_text(document_page(license_body, "License", "license.html"), encoding="utf-8")
    for path in media:
        if path.is_symlink():
            raise RuntimeError(f"Documentation assets must be regular files: {path.name}")
        shutil.copyfile(path, OUTPUT / "media" / path.name)
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(list(OUTPUT.rglob('*')))} entries in artifacts/pages")


if __name__ == "__main__":
    main()
