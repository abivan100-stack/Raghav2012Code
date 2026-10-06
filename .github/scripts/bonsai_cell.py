"""Compose output/bonsai.gif into the README's Projects band: output/bonsai-cell.gif.

The README is a grid of white panels with 1.5px ink borders. The bonsai stands at the right
end of the Projects header band, its pot on the line above the project list, like a plant at
the end of a shelf. The cell is the right third of that band:

- the band's left part (assets/sheet/projects.svg) has no right edge, so the band reads as one;
- the line the tree stands on is the Vault row's top edge, drawn just below this image;
- the line above is the Record panel's bottom edge;
- so this image draws only the sheet's right edge.

The ground is the sheet's white rather than transparent, so GitHub's dark page never shows
through the sheet. The tree is scaled by a whole number with nearest-neighbour so every art
pixel stays square. The canvas is 2x the cell's 280x124 layout size so the tree stays sharp
on high-DPI screens, and the edge is laid out to rasterise like the SVG borders at half size.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageSequence

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output/bonsai.gif")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "output/bonsai-cell.gif")

SCALE = 2
W, H = 280 * SCALE, 124 * SCALE
EDGE = 3                        # 1.5 layout px, flush with the outer edge like the SVG borders
BOX_W, BOX_H = 240 * SCALE, 112 * SCALE
PAPER, INK = (255, 255, 255), (17, 17, 17)


def cell_frame(tree, size):
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    d.rectangle([W - EDGE, 0, W - 1, H - 1], fill=INK)    # sheet's right edge
    t = tree.resize(size, Image.NEAREST)
    x = (W - EDGE - size[0]) // 2
    y = H - size[1]                                       # pot stands on the line below the band
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
