import sys
import json
import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "data" / "contributions.json"


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        level = cell.get("data-level")
        if level is None:
            aria = cell.get("aria-label", "")
            level = 0 if "No contributions" in aria else 1
        try:
            level = int(level)
        except ValueError:
            level = 0
        days.append({"date": date, "level": max(0, min(4, level))})
    days.sort(key=lambda item: item["date"])
    return days


def calculate_stats(days):
    active = sum(day["level"] > 0 for day in days)
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
    best = max(days, key=lambda d: d["level"], default={"date": None, "level": 0})
    return {"active_days_in_range": active, "current_streak": current, "longest_streak": longest, "best_day": best, "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}


def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_contributions.py <github_username>")
        sys.exit(1)
    username = sys.argv[1]
    days = fetch_days(username)
    output = {"username": username, "days": days, "stats": calculate_stats(days)}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Fetched {len(days)} contribution days.")


if __name__ == "__main__":
    main()
