"""Generate transparent toolbar icons from drawing primitives using Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / "nlayout" / "icons"
SCALE = 4


def canvas():
    image = Image.new("RGBA", (32 * SCALE, 32 * SCALE))
    return image, ImageDraw.Draw(image)


def coords(values):
    return tuple(round(value * SCALE) for value in values)


def line(draw, points, color, width=2):
    draw.line([coords(point) for point in points], fill=color,
              width=round(width * SCALE), joint="curve")


def polygon(draw, points, color):
    draw.polygon([coords(point) for point in points], fill=color)


def save(image, name):
    image.resize((32, 32), Image.Resampling.LANCZOS).save(ROOT / name)


def main():
    image, draw = canvas()
    navy, cyan, gold = "#12354A", "#16BDE8", "#FFD166"
    draw.rounded_rectangle(coords((3, 16, 29, 28)), radius=2 * SCALE,
                           fill=gold, outline=navy, width=2 * SCALE)
    for x in range(7, 28, 4):
        line(draw, [(x, 17), (x, 23 if x % 8 == 7 else 21)], navy, 1.4)
    line(draw, [(4, 4), (4, 13)], navy, 1.5)
    line(draw, [(28, 4), (28, 13)], navy, 1.5)
    line(draw, [(7, 8), (25, 8)], cyan)
    polygon(draw, [(4, 8), (10, 4), (10, 12)], cyan)
    polygon(draw, [(28, 8), (22, 4), (22, 12)], cyan)
    save(image, "numeric_assist.png")

    image, draw = canvas()
    purple, pink, navy = "#7943B8", "#D651B8", "#12354A"
    line(draw, [(5, 5), (13, 13), (5, 25)], purple)
    line(draw, [(13, 13), (24, 6)], purple)
    for x, y in [(5, 5), (5, 25), (24, 6)]:
        draw.rounded_rectangle(coords((x - 3, y - 3, x + 3, y + 3)),
                               radius=SCALE, fill="#E9DCF8",
                               outline=purple, width=round(1.5 * SCALE))
    draw.ellipse(coords((10, 10, 16, 16)), fill=pink)
    line(draw, [(28, 12), (19, 22)], navy, 3)
    polygon(draw, [(17, 18), (24, 24), (20, 30), (10, 23)], "#E2A22C")
    polygon(draw, [(15, 22), (22, 27), (20, 30), (10, 23)], "#FFD166")
    line(draw, [(13, 23), (19, 28)], "#B8741A", 1)
    line(draw, [(16, 23), (21, 27)], "#B8741A", 1)
    save(image, "remove_steiners.png")


if __name__ == "__main__":
    main()
