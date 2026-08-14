import csv
from collections import defaultdict
from datetime import datetime

FILE = r".\fixtures_master.csv"

with open(FILE, "r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

by_season = defaultdict(list)

for row in rows:
    dt = datetime.fromisoformat(
        row["kickoff_time"].replace("Z", "+00:00")
    )
    by_season[row["season"]].append(dt)

print()
print("=" * 100)
print("FIXTURE MASTER SEASON-LABEL AUDIT")
print("=" * 100)
print()

for season in sorted(by_season):

    dates = sorted(by_season[season])

    years = sorted({
        d.year
        for d in dates
    })

    print(
        f"{season}: "
        f"rows={len(dates):3} | "
        f"first={dates[0].date()} | "
        f"last={dates[-1].date()} | "
        f"calendar_years={years}"
    )

print()
print("=" * 100)
print("AUDIT COMPLETE")
print("=" * 100)
