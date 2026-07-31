"""
make_info_card.py

Hand-authored SVG that looks like the output of `neofetch`: a title bar,
then colored key/value rows. This is where the *story* numbers can't tell
lives -- the contribution heatmap already covers raw GitHub stats, so keep
this card to role, stack, and highlights instead of duplicating counts.

Each line fades + slides in on a short stagger so the panel looks like it's
printing next to the ASCII portrait. Set STATIC=1 to emit a frozen frame
(useful for a local Quick Look / non-animated preview).

Usage:
    python make_info_card.py
    STATIC=1 python make_info_card.py
"""

import os
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"

TITLE = "spectra@github"

# Edit these five lines to keep the card current.
ENTRIES = [
    ("Now", "Mechanical Eng (Yr 2) -> Software / AI Eng"),
    ("Prev", "CAD + FEA portfolio: EV pack, F1 wishbone, robotic arm"),
    ("Stack", "Python, TypeScript, Next.js, Node.js, SQLite, Ollama"),
    ("Building", "Agent-O7 (agentic OS) + RecruitIQ (ATS platform)"),
    ("Goal", "MS in Germany -- TU Munich / RWTH Aachen / KIT"),
]

KEY_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLEBAR_COLOR = "#161b22"

WIDTH = 490
ROW_H = 26
TOP_PAD = 46
LEFT_PAD = 18


def main():
    static = os.environ.get("STATIC") == "1"
    height = TOP_PAD + len(ENTRIES) * ROW_H + 18

    rows = []
    for i, (key, value) in enumerate(ENTRIES):
        y = TOP_PAD + i * ROW_H
        delay = i * 0.18
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        cls = "" if static else ' class="line"'
        rows.append(
            f'<text{cls} x="{LEFT_PAD}" y="{y}"{style} font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="13"><tspan fill="{KEY_COLOR}">{key}</tspan>'
            f'<tspan fill="{VALUE_COLOR}">  {value}</tspan></text>'
        )

    keyframes = "" if static else '''
    .line { opacity: 0; transform: translateX(-8px); animation: typeIn 0.4s ease-out forwards; }
    @keyframes typeIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
    '''

    svg = f'''<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg">
  <style>
    {keyframes}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" ry="8"
        fill="{BG_COLOR}" stroke="{BORDER_COLOR}" />
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="28" rx="8" ry="8" fill="{TITLEBAR_COLOR}" />
  <rect x="0.5" y="20.5" width="{WIDTH - 1}" height="8" fill="{TITLEBAR_COLOR}" />
  <circle cx="16" cy="14" r="5" fill="#ff5f56" />
  <circle cx="32" cy="14" r="5" fill="#ffbd2e" />
  <circle cx="48" cy="14" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="18" text-anchor="middle" fill="#8b949e"
        font-family="Consolas, 'Courier New', monospace" font-size="12">{TITLE}</text>
  {''.join(rows)}
</svg>'''
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
