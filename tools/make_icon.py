"""Generate the Claude-buddy desktop icon as a multi-resolution .ico.

Run from the project root:  python tools/make_icon.py
Produces tools/claude.ico (and tools/claude_preview.png for eyeballing).
"""
import os
from PIL import Image, ImageDraw

ORANGE = (217, 119, 87, 255)   # #d97757
CREAM  = (250, 249, 245, 255)  # #faf9f5
INK    = (20, 20, 19, 255)     # #141413

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 256


def draw_icon():
    import math
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, SIZE - 6, SIZE - 6], radius=46, fill=CREAM, outline=INK, width=4)
    cx = SIZE // 2
    # legs
    d.rounded_rectangle([cx - 14, 214, cx - 2, 244], radius=4, fill=ORANGE, outline=INK, width=2)
    d.rounded_rectangle([cx + 2, 214, cx + 14, 244], radius=4, fill=ORANGE, outline=INK, width=2)
    # body
    d.rounded_rectangle([cx - 60, 150, cx + 60, 226], radius=26, fill=ORANGE, outline=INK, width=4)
    # face
    for ex in (cx - 22, cx + 22):
        d.ellipse([ex - 13, 168, ex + 13, 194], fill=CREAM, outline=INK, width=2)
        d.ellipse([ex - 5, 178, ex + 5, 190], fill=INK)
    d.arc([cx - 22, 188, cx + 22, 214], start=20, end=160, fill=INK, width=4)
    # sunburst head
    hx, hy = cx, 96
    d.line([hx, hy + 30, hx, 150], fill=ORANGE, width=8)            # neck
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line([hx, hy, hx + 52 * math.cos(rad), hy + 52 * math.sin(rad)], fill=ORANGE, width=7)
    d.ellipse([hx - 30, hy - 30, hx + 30, hy + 30], fill=ORANGE, outline=INK, width=3)
    d.ellipse([hx - 12, hy - 12, hx + 12, hy + 12], fill=CREAM)
    return img


def main():
    img = draw_icon()
    ico = os.path.join(HERE, "claude.ico")
    png = os.path.join(HERE, "claude_preview.png")
    img.save(png)
    img.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                         (64, 64), (128, 128), (256, 256)])
    print("icon   :", ico)
    print("preview:", png)


if __name__ == "__main__":
    main()
