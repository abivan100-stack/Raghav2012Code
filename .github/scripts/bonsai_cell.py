"""Compose output/bonsai.gif into the README's bonsai side-build card: output/bonsai-cell.gif.

The README is a grid of white panels with 1.5px ink borders. Under the side builds sits a
card for this tree: "Side build · GitHub Actions / bonsai / Grown from my commits, regrown
every day." (assets/sheet/bonsai-card.svg), and this image is the tree half of that card.
It draws no lines of its own: the side-build cards above draw its top edge, the saas-lab
demo cell beside it draws its right edge, the Toolchain panel draws its bottom edge, and it
joins the card text on its left with no divider, so the text and the tree read as one card.

The ground is the sheet's white rather than transparent, so GitHub's dark page never shows
through the sheet. The tree is scaled by a whole number with nearest-neighbour so every art
pixel stays square, centred across the cell, and its pot stands on the card description's
last baseline. The canvas is 2x the cell's 168x150 layout size so the tree stays sharp on
high-DPI screens.
"""
import pathlib
import sys

from PIL import Image, ImageSequence

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output/bonsai.gif")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "output/bonsai-cell.gif")

SCALE = 2
W, H = 168 * SCALE, 150 * SCALE
BASELINE = 127 * SCALE          # the card description's last baseline; the pot stands on it
BOX_W, BOX_H = 144 * SCALE, 117 * SCALE
PAPER = (255, 255, 255)


def cell_frame(tree, size):
    canvas = Image.new("RGB", (W, H), PAPER)
    t = tree.resize(size, Image.NEAREST)
    x = (W - size[0]) // 2
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
