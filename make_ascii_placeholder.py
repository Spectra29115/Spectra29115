"""
make_ascii_placeholder.py

Stand-in for the portrait column until you run the real photo pipeline
(prep_photo.py -> make_ascii_svg.py). Renders a name wordmark with
pyfiglet instead of a photo, then applies the exact same monochrome,
row-by-row wipe animation as the real ASCII portrait, so swapping the two
files later is a drop-in replacement with no README changes needed.

Usage:
    python make_ascii_placeholder.py
"""

from pathlib import Path

import pyfiglet

NAME = "SPECTRA"
TAGLINE = "mechanical eng -> ai / swe"
FONT = "big"

CHAR_W = 6.2
CHAR_H = 11
FILL_COLOR = "#c9d1d9"

OUT_PATH = Path(__file__).resolve().parent.parent / "profile-ascii.svg"


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rows():
    art = pyfiglet.Figlet(font=FONT).renderText(NAME)
    lines = [ln for ln in art.split("\n")]
    while lines and lines[-1].strip() == "":
        lines.pop()
    max_len = max(len(ln) for ln in lines) if lines else 0

    lines.append("")
    lines.append(TAGLINE.center(max_len))
    return lines, max_len


def render(rows, grid_w):
    width = grid_w * CHAR_W
    height = len(rows) * CHAR_H

    defs = []
    texts = []
    stagger = 0.05
    wipe_duration = 0.8

    for y, row in enumerate(rows):
        text = escape_xml(row.ljust(grid_w))
        delay = y * stagger
        clip_id = f"pwipe{y}"
        defs.append(f'''
    <clipPath id="{clip_id}">
      <rect x="0" y="{y * CHAR_H}" width="0" height="{CHAR_H + 2}">
        <animate attributeName="width" from="0" to="{width}"
                 begin="{delay:.3f}s" dur="{wipe_duration}s" fill="freeze" />
      </rect>
    </clipPath>''')
        texts.append(
            f'<text x="0" y="{y * CHAR_H + CHAR_H - 2}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="{CHAR_H}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{text}</text>'
        )

    return f'''<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    {''.join(defs)}
  </defs>
  {''.join(texts)}
</svg>'''


def main():
    rows, grid_w = build_rows()
    svg = render(rows, grid_w)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH} (placeholder -- swap for a real photo later)")


if __name__ == "__main__":
    main()
