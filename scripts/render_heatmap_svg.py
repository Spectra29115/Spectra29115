"""
render_heatmap_svg.py

Reads data/contributions.json (written by fetch_contributions.py) and draws
the classic 53-week x 7-day contribution grid as an SVG. Boxes reveal in a
diagonal, line-after-line slide-down using CSS keyframes -- plays once on
load, then freezes (no looping "glow"). Adds a Less -> More legend and a
one-line stats footer.

Usage:
    python render_heatmap_svg.py
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 20
BOTTOM_PAD = 34


def build_weeks(days):
    """Bucket the flat day list into weeks (columns), Sunday-first."""
    weeks = []
    current_week = [None] * 7
    for d in days:
        import datetime

        dt = datetime.date.fromisoformat(d["date"])
        dow = (dt.weekday() + 1) % 7  # convert Mon=0 -> Sun=0
        if dow == 0 and any(x is not None for x in current_week):
            weeks.append(current_week)
            current_week = [None] * 7
        current_week[dow] = d
    weeks.append(current_week)
    return weeks


def level_color(level):
    level = max(0, min(level, len(PALETTE) - 1))
    return PALETTE[level]


def render(payload):
    days = payload["days"]
    stats = payload.get("stats", {})
    username = payload.get("username", "")
    weeks = build_weeks(days)

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    rects = []
    delay_step = 0.012  # seconds between diagonal steps
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            color = level_color(day["level"])
            # Diagonal stagger: earlier columns + earlier rows appear first.
            delay = (wi + di) * delay_step
            rects.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" ry="2" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s" '
                f'data-date="{day["date"]}"><title>{day["date"]}: level {day["level"]}</title></rect>'
            )

    legend_x = width - 150
    legend_y = height - 14
    legend_boxes = []
    for i, color in enumerate(PALETTE):
        legend_boxes.append(
            f'<rect x="{legend_x + i * (CELL + 2)}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="2" ry="2" fill="{color}" />'
        )

    total = stats.get("active_days_in_range", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = (
        f'{total} active days in the last year &middot; current streak {streak} &middot; longest streak {longest}'
    )

    svg = f'''<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">
  <style>
    .cell {{
      opacity: 0;
      transform: translate(-6px, -6px);
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      from {{ opacity: 0; transform: translate(-6px, -6px); }}
      to   {{ opacity: 1; transform: translate(0, 0); }}
    }}
    .label {{ fill: #8b949e; font-size: 10px; }}
    .footer {{ fill: #c9d1d9; font-size: 11px; }}
  </style>
  <text x="{LEFT_PAD}" y="12" class="label">{username}'s contributions</text>
  <g>
    {''.join(rects)}
  </g>
  <text x="{legend_x - 42}" y="{legend_y + 9}" class="label">Less</text>
  {''.join(legend_boxes)}
  <text x="{legend_x + len(PALETTE) * (CELL + 2) + 6}" y="{legend_y + 9}" class="label">More</text>
  <text x="{LEFT_PAD}" y="{height - 4}" class="footer">{footer}</text>
</svg>'''
    return svg


def main():
    payload = json.loads(DATA_PATH.read_text())
    svg = render(payload)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
