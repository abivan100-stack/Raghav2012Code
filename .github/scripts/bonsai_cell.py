"""Compose output/bonsai.gif into the README sheet's colophon cell: output/bonsai-cell.gif.

The README is a grid of white panels with 1.5px ink borders. The bonsai stands in the
bottom-right cell straight on the sheet's white, so it reads as part of the page. The ground
is the sheet's white rather than transparent: a transparent cell would show GitHub's dark
page through the sheet in dark mode. This cell is the sheet's corner, so it draws the
sheet's right and bottom edges itself; the colophon note's border and the Toolchain panel
draw its left and top edges.

The tree is scaled by a whole number with nearest-neighbour so every art pixel stays square,
centred across the cell, and its pot stands on the colophon note's last baseline.

The canvas is 2x the cell's 280x170 layout size so the tree stays sharp on high-DPI screens.
Edges are laid out so that, drawn at half size, they rasterise like the SVG borders.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageSequence

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output/bonsai.gif")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "output/bonsai-cell.gif")

SCALE = 2
W, H = 280 * SCALE, 170 * SCALE
EDGE = 3                        # 1.5 layout px, flush with the outer edge like the SVG borders
BASELINE = 142 * SCALE          # the colophon note's last baseline; the pot stands on it
BOX_W, BOX_H = 220 * SCALE, 118 * SCALE
PAPER, INK = (255, 255, 255), (17, 17, 17)


def cell_frame(tree, size):
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    d.rectangle([W - EDGE, 0, W - 1, H - 1], fill=INK)    # sheet's right edge
    d.rectangle([0, H - EDGE, W - 1, H - 1], fill=INK)    # sheet's bottom edge
    t = tree.resize(size, Image.NEAREST)
    x = (W - EDGE - size[0]) // 2
    y = max(0, BASELINE - size[1])
    canvas.paste(t, (x, y), t)
    return canvas


def main():
    src = Image.open(SRC)
    frames, durations = [], []
    for fr in ImageSequence.Iterator(src):
        frames.append(fr.convert("RGBA"))
        durations.append(fr.info.get("duration", src.info.get("duration", 100)))
    w, h = frames[0].size
    k = min(BOX_W / w, BOX_H / h)
    if k >= 1:
        k = int(k)              # whole-number scale keeps every art pixel square
    size = (max(1, round(w * k)), max(1, round(h * k)))

    composed = [cell_frame(f, size) for f in frames]
    # one palette built from every frame, so colours cannot shift or flicker between frames
    sheet = Image.new("RGB", (W, H * len(composed)), PAPER)
    for i, c in enumerate(composed):
        sheet.paste(c, (0, i * H))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = [c.quantize(palette=palette, dither=Image.Dither.NONE) for c in composed]
    out[0].save(OUT, save_all=True, append_images=out[1:], duration=durations,
                loop=src.info.get("loop", 0), disposal=1, optimize=False)
    print(f"{OUT}: {len(out)} frames, tree {w}x{h} -> {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
