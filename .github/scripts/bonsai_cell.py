"""Compose output/bonsai.gif into a white README sheet cell: output/bonsai-cell.gif.

The README is a grid of white panels with 1.5px ink borders. This cell is the middle third
of the contact row, so it draws no borders of its own: the neighbouring SVG cells draw its
left and right edges and the Record panel below draws the line the pot stands on. That keeps
every line in the grid a crisp vector. The tree is scaled with nearest-neighbour so the pixel
art stays sharp, centred, and its pot sits on the bottom edge.

The canvas is 2x the cell's 280x200 layout size so the tree stays sharp on high-DPI screens.
"""
import pathlib
import sys

from PIL import Image, ImageSequence

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output/bonsai.gif")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "output/bonsai-cell.gif")

SCALE = 2
W, H = 280 * SCALE, 200 * SCALE
BOX_W, BOX_H = 200 * SCALE, 132 * SCALE
PAPER = (255, 255, 255)


def cell_frame(tree, size):
    canvas = Image.new("RGB", (W, H), PAPER)
    t = tree.resize(size, Image.NEAREST)
    x = (W - size[0]) // 2
    y = H - size[1]                                        # pot stands on the Record panel's top line
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
