<p align="center">
  <img src="docs/media/banner.svg" alt="Numeric Layout Assist — Precision, at your cursor." width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-6b45b9?style=flat-square" alt="MIT license"></a>
  <a href="docs/numeric_assist_guide.md"><img src="https://img.shields.io/badge/Virtuoso-IC23.1-527c79?style=flat-square" alt="Virtuoso IC23.1"></a>
  <a href="src/numeric_assist.il"><img src="https://img.shields.io/badge/built_with-SKILL-bb667f?style=flat-square" alt="Built with SKILL"></a>
</p>

<p align="center">
  <b><a href="docs/numeric_assist_guide.md">User guide</a></b> &nbsp;·&nbsp;
  <b><a href="docs/demo/index.html">Interactive lab</a></b> &nbsp;·&nbsp;
  <a href="docs/numeric_assist_guide.md#installation">Installation</a> &nbsp;·&nbsp;
  <a href="test/README.md">Testing</a>
</p>

Add precise numeric input to native **Virtuoso Layout** commands. Pick a length
or spacing from geometry, type a dimension, and preview the result at your
cursor. **J** handles numeric entry, **Shift+J** adds absolute positioning and
Contour, and **N** sets the Copy count.

## See it in motion

<p align="center">
  <a href="docs/demo/index.html"><img src="docs/media/overview.gif" alt="Four tools in a 2×2 grid: pick a dimension, set a path width, create an exact ruler, and place repeated copies. One panel plays at a time." width="100%"></a>
</p>

**Pick → Width → Measurement → Copy.** One panel plays at a time, with a
one-second pause between tools. These are illustrative animations using synthetic
geometry. [Open the interactive lab](docs/demo/index.html) to change values,
adjust playback speed, or step through every tool. The self-contained site runs locally by opening its
HTML file; [preview instructions](docs/numeric_assist_guide.md#interactive-demonstrations)
and [GitHub Pages deployment](docs/PUBLISHING.md) are documented separately.

## The tools

| Tool | What it helps you do | Watch / explore |
| --- | --- | --- |
| **Dimension picker** | Read an edge length, wire width, or parallel-edge spacing | [GIF](docs/media/pick.gif) · [Try it](docs/demo/index.html#pick) |
| **Path / Wire** | Set a width while drawing | [GIF](docs/media/width.gif) · [Try it](docs/demo/index.html#width) |
| **Rectangle** | Enter width and height together | [GIF](docs/media/rectangle.gif) · [Try it](docs/demo/index.html#rectangle) |
| **Measurement** | Give a new ruler a precise length | [GIF](docs/media/measure.gif) · [Try it](docs/demo/index.html#measure) |
| **Stretch** | Set a partial selection's final extent or move a whole selection | [GIF](docs/media/stretch.gif) · [Try it](docs/demo/index.html#stretch) |
| **Move** | Use a relative displacement or absolute position | [GIF](docs/media/move.gif) · [Try it](docs/demo/index.html#move) |
| **Copy + count** | Set the count and pitch, then preview every Step target | [GIF](docs/media/copy.gif) · [Try it](docs/demo/index.html#copy) |
| **Contour** | Resize a rectangle inside or outside a chosen pivot | [GIF](docs/media/contour.gif) · [Try it](docs/demo/index.html#contour) |
| **Steiner cleanup** | Remove invisible Steiner objects from the edited layout | [GIF](docs/media/cleanup.gif) · [Try it](docs/demo/index.html#cleanup) |

The ruler toolbar button toggles Numeric Assist. Full command behavior,
installation, grid handling, and key restoration are in the
**[user guide](docs/numeric_assist_guide.md)**.
