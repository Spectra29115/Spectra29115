"""Generate a GitHub-compatible static ASCII portrait SVG."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
GRID_W = 100
GRID_H = 53
CHAR_W = 6.2
CHAR_H = 11
FILL_COLOR = "#c9d1d9"


def image_to_ascii_rows(path: Path):
    img = Image.open(path).convert("L").resize((GRID_W, GRID_H))
    pixels = np.array(img)
    rows = []
    for y in range(GRID_H):
        row = []
        for x in range(GRID_W):
            brightness = pixels[y, x] / 255.0
            row.append(RAMP[int((1 - brightness) * (len(RAMP) - 1))])
        rows.append("".join(row))
    return rows


def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(rows):
    width = GRID_W * CHAR_W
    height = GRID_H * CHAR_H
    texts = []
    for y, row in enumerate(rows):
        texts.append(
            f'<text x="0" y="{y * CHAR_H + CHAR_H - 2}" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="{CHAR_H}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{escape_xml(row)}</text>'
        )
    return f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" xmlns="http://www.w3.org/2000/svg">{"".join(texts)}</svg>'


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "source-prepped.png"
    if not src.exists():
        print(f"Not found: {src}")
        sys.exit(1)
    out = Path(__file__).resolve().parent.parent / "profile-ascii.svg"
    out.write_text(render(image_to_ascii_rows(src)), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
