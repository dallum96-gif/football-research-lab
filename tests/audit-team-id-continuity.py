import csv
import os
from collections import defaultdict

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")


def load_fixtures():
    with open(
        FIXTURE_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as handle:
        return list(csv.DictReader(handle))


fixtures = load_fixtures()

# season -> set of source team IDs
season_team_ids = defaultdict(set)

for row in fixtures:
    season_team_ids[row["season"]].add(row["home_team_id"])
    season_team_ids[row["season"]].add(row["away_team_id"])

seasons = sorted(season_team_ids)

print("=== TEAM ID CONTINUITY AUDIT ===")
print()

for season in seasons:
    ids = sorted(
        season_team_ids[season],
        key=int
    )

    print(
        f"{season}: "
        f"{len(ids)} teams | "
        f"IDs: {', '.join(ids)}"
    )

print()
print("=== ID CHANGES BETWEEN CONSECUTIVE SEASONS ===")
print()

for previous, current in zip(seasons, seasons[1:]):

    previous_ids = season_team_ids[previous]
    current_ids = season_team_ids[current]

    retained = sorted(
        previous_ids & current_ids,
        key=int
    )

    disappeared = sorted(
        previous_ids - current_ids,
        key=int
    )

    appeared = sorted(
        current_ids - previous_ids,
        key=int
    )

    print(f"{previous} -> {current}")
    print(f"  Retained IDs : {', '.join(retained)}")
    print(f"  Disappeared  : {', '.join(disappeared)}")
    print(f"  Appeared     : {', '.join(appeared)}")
    print()

print("=== COMPLETE ===")
