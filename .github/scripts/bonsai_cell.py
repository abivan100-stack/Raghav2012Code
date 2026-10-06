"""Compose output/bonsai.gif into the README sheet's colophon cell: output/bonsai-cell.gif.

The README is a grid of white panels with 1.5px ink borders. The bonsai sits in the
bottom-right cell on an ink display plate, mounted on a white mat so the sheet stays one
white rectangle in GitHub's dark mode too. This cell is the sheet's corner, so it draws the
sheet's right and bottom edges itself; the colophon note's border and the Toolchain panel
draw its left and top edges.

The canvas is 2x the cell's 280x170 layout size so the pixel-art tree stays sharp on
high-DPI screens. Edges are laid out so that, drawn at half size, they rasterise like the
SVG borders: one full ink pixel on the edge and a half-tone pixel inside it.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageSequence

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output/bonsai.gif")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "output/bonsai-cell.gif")

SCALE = 2
W, H = 280 * SCALE, 170 * SCALE
MAT = 16 * SCALE                # white margin between the cell edges and the plate
BOX_W, BOX_H = 220 * SCALE, 112 * SCALE   # plate interior less 12px padding
PAPER, INK = (255, 255, 255), (17, 17, 17)
PLATE = INK


def cell_frame(tree, size):
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    # sheet edges: 1.5 layout px = 3 canvas px, flush with the outer edge like the SVG borders
    d.rectangle([W - 3, 0, W - 1, H - 1], fill=INK)
    d.rectangle([0, H - 3, W - 1, H - 1], fill=INK)
    # the display plate on its mat
    d.rectangle([MAT, MAT, W - 3 - MAT - 1, H - 3 - MAT - 1], fill=PLATE)
    t = tree.resize(size, Image.NEAREST)
    pw, ph = W - 3 - 2 * MAT, H - 3 - 2 * MAT
    x = MAT + (pw - size[0]) // 2
    y = MAT + (ph - size[1]) // 2
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
