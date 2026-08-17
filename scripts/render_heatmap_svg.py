import json
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "contributions.json"
OUTPUT_FILE = ROOT / "contrib-heatmap.svg"
WIDTH = 770
HEIGHT = 152
CELL = 11
GAP = 3
COLORS = {0: "#161b22", 1: "#0e4429", 2: "#006d32", 3: "#26a641", 4: "#39d353"}


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_days(data):
    return {item["date"]: int(item.get("level", 0)) for item in data.get("days", [])}


def get_last_year(days):
    today = datetime.now().date()
    start = today - timedelta(days=364)
    return [
        {"date": (start + timedelta(days=i)).isoformat(),
         "level": days.get((start + timedelta(days=i)).isoformat(), 0)}
        for i in range(365)
    ]


def calculate_stats(days):
    active = sum(d["level"] > 0 for d in days)
    current = 0
    for day in reversed(days):
        if day["level"] > 0:
            current += 1
        else:
            break
    longest = running = 0
    for day in days:
        if day["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    return active, current, longest


def build_svg(username, days, stats):
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    first_sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    lookup = {d["date"]: d["level"] for d in days}
    cells = []
    for col in range(53):
        for row in range(7):
            date = first_sunday + timedelta(days=col * 7 + row)
            key = date.isoformat()
            level = lookup.get(key, 0)
            x = 28 + col * (CELL + GAP)
            y = 20 + row * (CELL + GAP)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{COLORS.get(level, COLORS[0])}">'
                f'<title>{key}: contribution level {level}</title></rect>'
            )
    active, current, longest = stats
    return f'''<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">
  <style>
    .label {{ fill: #8b949e; font-size: 10px; }}
    .footer {{ fill: #c9d1d9; font-size: 11px; }}
  </style>
  <text x="28" y="12" class="label">{username}'s contributions</text>
  <g>{''.join(cells)}</g>
  <text x="578" y="147" class="label">Less</text>
  <rect x="620" y="138" width="11" height="11" rx="2" fill="{COLORS[0]}"/>
  <rect x="633" y="138" width="11" height="11" rx="2" fill="{COLORS[1]}"/>
  <rect x="646" y="138" width="11" height="11" rx="2" fill="{COLORS[2]}"/>
  <rect x="659" y="138" width="11" height="11" rx="2" fill="{COLORS[3]}"/>
  <rect x="672" y="138" width="11" height="11" rx="2" fill="{COLORS[4]}"/>
  <text x="690" y="147" class="label">More</text>
  <text x="28" y="148" class="footer">{active} active days · current streak {current} · longest streak {longest}</text>
</svg>
'''


def main():
    data = load_data()
    username = data.get("username", "Spectra29115")
    days = get_last_year(normalize_days(data))
    stats = calculate_stats(days)
    OUTPUT_FILE.write_text(build_svg(username, days, stats), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
