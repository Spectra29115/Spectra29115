import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "contributions.json"
OUTPUT_FILE = ROOT / "contrib-heatmap.svg"

WIDTH = 770
HEIGHT = 152

CELL = 11
GAP = 3

COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_days(data):
    return {
        item["date"]: int(item.get("level", 0))
        for item in data.get("days", [])
    }


def get_last_year(days):
    """
    Return exactly the latest 365 days ending today.
    """
    today = datetime.utcnow().date()

    start = today - timedelta(days=364)

    result = []

    current = start

    while current <= today:
        date_string = current.isoformat()

        result.append(
            {
                "date": date_string,
                "level": days.get(date_string, 0),
            }
        )

        current += timedelta(days=1)

    return result


def calculate_stats(days):
    active = sum(1 for d in days if d["level"] > 0)

    current_streak = 0

    for day in reversed(days):
        if day["level"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0

    for day in days:
        if day["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(
        days,
        key=lambda x: x["level"],
        default={"date": "N/A", "level": 0},
    )

    return {
        "active": active,
        "current": current_streak,
        "longest": longest_streak,
        "best_day": best_day,
    }


def build_svg(username, days, stats):
    """
    GitHub-friendly static SVG.

    IMPORTANT:
    No JavaScript.
    No CSS animation.
    No SMIL animation.
    """

    # Find the Sunday before/at the start date.
    first_date = datetime.strptime(
        days[0]["date"],
        "%Y-%m-%d",
    ).date()

    first_sunday = first_date - timedelta(
        days=(first_date.weekday() + 1) % 7
    )

    # Create a lookup table.
    lookup = {
        d["date"]: d["level"]
        for d in days
    }

    cells = []

    current = first_sunday

    # 53 columns × 7 rows
    for column in range(53):

        for row in range(7):

            date = current + timedelta(
                days=column * 7 + row
            )

            date_string = date.isoformat()

            level = lookup.get(date_string, 0)

            x = 28 + column * (CELL + GAP)
            y = 20 + row * (CELL + GAP)

            color = COLORS.get(level, COLORS[0])

            cells.append(
                f'''
    <rect
      x="{x}"
      y="{y}"
      width="{CELL}"
      height="{CELL}"
      rx="2"
      ry="2"
      fill="{color}"
    >
      <title>{date_string}: contribution level {level}</title>
    </rect>'''
            )

    svg = f'''<svg
  viewBox="0 0 {WIDTH} {HEIGHT}"
  width="{WIDTH}"
  height="{HEIGHT}"
  xmlns="http://www.w3.org/2000/svg"
  font-family="Consolas, 'Courier New', monospace"
>

  <style>
    .label {{
      fill: #8b949e;
      font-size: 10px;
    }}

    .footer {{
      fill: #c9d1d9;
      font-size: 11px;
    }}
  </style>

  <text
    x="28"
    y="12"
    class="label"
  >
    {username}'s contributions
  </text>

  <g>
    {"".join(cells)}
  </g>

  <!-- Legend -->

  <text
    x="578"
    y="147"
    class="label"
  >
    Less
  </text>

  <rect
    x="620"
    y="138"
    width="11"
    height="11"
    rx="2"
    fill="{COLORS[0]}"
  />

  <rect
    x="633"
    y="138"
    width="11"
    height="11"
    rx="2"
    fill="{COLORS[1]}"
  />

  <rect
    x="646"
    y="138"
    width="11"
    height="11"
    rx="2"
    fill="{COLORS[2]}"
  />

  <rect
    x="659"
    y="138"
    width="11"
    height="11"
    rx="2"
    fill="{COLORS[3]}"
  />

  <rect
    x="672"
    y="138"
    width="11"
    height="11"
    rx="2"
    fill="{COLORS[4]}"
  />

  <text
    x="690"
    y="147"
    class="label"
  >
    More
  </text>

  <text
    x="28"
    y="148"
    class="footer"
  >
    {stats["active"]} active days
    · current streak {stats["current"]}
    · longest streak {stats["longest"]}
  </text>

</svg>
'''

    return svg


def main():

    data = load_data()

    username = data.get(
        "username",
        "Spectra29115",
    )

    all_days = normalize_days(data)

    days = get_last_year(all_days)

    stats = calculate_stats(days)

    svg = build_svg(
        username,
        days,
        stats,
    )

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"Generated {OUTPUT_FILE}"
    )

    print(
        f"Active days: {stats['active']}"
    )

    print(
        f"Current streak: {stats['current']}"
    )

    print(
        f"Longest streak: {stats['longest']}"
    )


if __name__ == "__main__":
    main()
