import csv
from collections import Counter

FILE = r".\fixtures_master.csv"

with open(FILE, "r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

def signature(row):
    return (
        row["kickoff_time"],
        row["home_team_id"],
        row["away_team_id"],
        row["home_score"],
        row["away_score"],
        row["gameweek"],
    )

sets = {}

for season in (
    "2020-21",
    "2021-22",
    "2022-23",
):

    sets[season] = {
        signature(row)
        for row in rows
        if row["season"] == season
    }

print()
print("=" * 90)
print("SEASON DUPLICATION CHECK")
print("=" * 90)
print()

for a, b in (
    ("2020-21", "2021-22"),
    ("2021-22", "2022-23"),
    ("2020-21", "2022-23"),
):

    intersection = (
        sets[a] & sets[b]
    )

    print(
        f"{a} vs {b}: "
        f"{len(intersection)} identical "
        f"fixture signatures"
    )

print()
print(
    "Expected if our diagnosis is correct:"
)
print(
    "2021-22 vs 2022-23 should be 380."
)
print()
print("=" * 90)
