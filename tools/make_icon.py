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
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # soft cream app tile
    d.rounded_rectangle([6, 6, SIZE - 6, SIZE - 6], radius=46,
                        fill=CREAM, outline=INK, width=4)

    # orange Claude buddy body
    d.rounded_rectangle([40, 54, 216, 232], radius=46,
                        fill=ORANGE, outline=INK, width=6)

    # eyes (cream with an ink pupil that looks slightly down = friendly)
    for ex in (100, 156):
        d.ellipse([ex - 22, 98, ex + 22, 142], fill=CREAM, outline=INK, width=3)
        d.ellipse([ex - 9, 116, ex + 9, 134], fill=INK)

    # smile (bottom arc of an ellipse)
    d.arc([86, 120, 170, 198], start=20, end=160, fill=INK, width=8)

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
