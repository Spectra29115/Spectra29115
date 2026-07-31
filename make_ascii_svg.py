"""
make_ascii_svg.py

Converts source-prepped.png (written by prep_photo.py) into a self-typing
monochrome ASCII-art SVG.

The image is downsampled to a character grid (~100 wide x 53 tall), and each
pixel's brightness picks a glyph from a density ramp -- sparse characters
for bright areas, dense ones for dark:

    RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
    # leading space clears the background to nothing

Two choices keep it clean instead of noisy:
  - Monochrome: one light-gray fill. Per-character rainbow coloring is what
    makes most ASCII portraits look like static.
  - High contrast: a busy background washes out to the space glyph, so only
    the subject prints.

For the animation, each row is wrapped in a horizontal clip that wipes
left-to-right (a small block "cursor" rides the wipe edge), staggered top
to bottom. The portrait prints once and freezes -- no looping.

Usage:
    python make_ascii_svg.py [source-prepped.png]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

GRID_W = 100
GRID_H = 53
CHAR_W = 6.2
CHAR_H = 11
FILL_COLOR = "#c9d1d9"


def image_to_ascii_rows(path: Path):
    img = Image.open(path).convert("L")
    img = img.resize((GRID_W, GRID_H))
    pixels = np.array(img)

    rows = []
    ramp_len = len(RAMP)
    for y in range(GRID_H):
        row_chars = []
        for x in range(GRID_W):
            brightness = pixels[y, x] / 255.0  # 1.0 = white/bright
            idx = int((1 - brightness) * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render(rows):
    width = GRID_W * CHAR_W
    height = GRID_H * CHAR_H

    row_groups = []
    stagger = 0.03  # seconds between row starts, top to bottom
    wipe_duration = 0.9

    for y, row in enumerate(rows):
        text = escape_xml(row)
        delay = y * stagger
        clip_id = f"wipe{y}"
        row_groups.append(f'''
    <clipPath id="{clip_id}">
      <rect x="0" y="{y * CHAR_H}" width="0" height="{CHAR_H + 2}">
        <animate attributeName="width" from="0" to="{width}"
                 begin="{delay:.3f}s" dur="{wipe_duration}s" fill="freeze" />
      </rect>
    </clipPath>''')
        row_groups.append(
            f'<text x="0" y="{y * CHAR_H + CHAR_H - 2}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="{CHAR_H}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{text}</text>'
        )

    svg = f'''<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    {''.join(g for g in row_groups if g.strip().startswith('<clipPath'))}
  </defs>
  {''.join(g for g in row_groups if g.strip().startswith('<text'))}
</svg>'''
    return svg


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "source-prepped.png"
    if not src.exists():
        print(f"Not found: {src}\nRun prep_photo.py first, or pass a path explicitly.")
        sys.exit(1)

    out_path = Path(__file__).resolve().parent.parent / "profile-ascii.svg"
    rows = image_to_ascii_rows(src)
    svg = render(rows)
    out_path.write_text(svg)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
