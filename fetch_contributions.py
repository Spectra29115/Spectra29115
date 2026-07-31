"""
fetch_contributions.py

Pulls the public contribution calendar for a GitHub user with NO auth token.
GitHub serves this as plain HTML at /users/<username>/contributions -- the
same fragment the profile page itself renders. We parse the day cells with
BeautifulSoup and write a small JSON file with the raw days plus a few
derived stats (current streak, longest streak, best day, monthly totals).

Usage:
    python fetch_contributions.py <github_username>
"""

import sys
import json
import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(username: str):
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> or <rect> with a data-date/date attr
    # depending on markup version; handle both defensively.
    cells = soup.select("td.ContributionCalendar-day") or soup.select("rect.ContributionCalendar-day") or soup.select("[data-date]")

    for cell in cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue
        level_attr = cell.get("data-level")
        if level_attr is not None:
            level = int(level_attr)
        else:
            # Fall back to parsing the tooltip text for a count, then bucket it.
            title = cell.get("title") or cell.text or ""
            level = 0
            if "No contributions" not in title:
                level = 1
        days.append({"date": date_str, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(1 for d in days if d["level"] > 0)

    # current streak: walk backwards from the most recent day
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest = running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["level"])

    by_month = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        by_month[month] = by_month.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "active_days_in_range": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best_day["date"],
        "by_month": by_month,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_contributions.py <github_username>")
        sys.exit(1)

    username = sys.argv[1]
    days = fetch_days(username)
    stats = derive_stats(days)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"username": username, "days": days, "stats": stats}, indent=2))
    print(f"Wrote {len(days)} days -> {OUT_PATH}")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
