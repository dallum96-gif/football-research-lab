import csv
import os
from collections import defaultdict

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"

FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")
PLAYER_DIR = os.path.join(ROOT, "_merged", "players")

SEASONS = [
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]


def load_csv(path):
    # These files are only being used for structural fields here.
    # latin-1 can decode both ASCII and the common legacy single-byte
    # characters without blocking the audit on a player name.
    with open(path, "r", encoding="latin-1", newline="") as handle:
        return list(csv.DictReader(handle))


fixtures = load_csv(FIXTURE_FILE)

fixture_lookup = {
    (row["season"], str(row["fixture_id"])): row
    for row in fixtures
}

mapping = defaultdict(lambda: defaultdict(set))

rows_used = 0
season_row_counts = {}


for season in SEASONS:

    player_file = os.path.join(
        PLAYER_DIR,
        f"{season}_all_players_gw.csv"
    )

    rows = load_csv(player_file)
    season_row_counts[season] = len(rows)

    for row in rows:

        fixture_id = str(row.get("fixture", "")).strip()
        team_code = str(row.get("team_code", "")).strip()
        was_home = str(row.get("was_home", "")).strip().lower()

        if not fixture_id or not team_code:
            continue

        fixture = fixture_lookup.get((season, fixture_id))

        if fixture is None:
            continue

        if was_home == "true":
            local_team_id = str(fixture["home_team_id"])
        elif was_home == "false":
            local_team_id = str(fixture["away_team_id"])
        else:
            continue

        mapping[season][local_team_id].add(team_code)
        rows_used += 1


print()
print("=" * 78)
print(" PLAYER TEAM_CODE -> FIXTURE LOCAL-ID BRIDGE")
print("=" * 78)
print()
print(f"Player rows used: {rows_used:,}")
print()

print("Season player-row counts:")
for season in SEASONS:
    print(f"  {season}: {season_row_counts[season]:,}")

print()

for season in SEASONS:

    print(season)

    conflicts = 0

    for local_team_id in sorted(mapping[season], key=int):

        codes = sorted(mapping[season][local_team_id])

        if len(codes) > 1:
            conflicts += 1

        print(
            f"  local team {local_team_id:>2} "
            f"-> team_code {','.join(codes)}"
        )

    print(f"  Local-ID conflicts: {conflicts}")
    print()


TARGET_CODES = {
    "43": "Manchester City",
    "21": "West Ham",
    "91": "Bournemouth",
}

print("=" * 78)
print("THREE-CLUB IDENTITY HISTORY")
print("=" * 78)
print()

for team_code, name in TARGET_CODES.items():

    print(name)

    for season in SEASONS:

        local_ids = []

        for local_id, codes in mapping[season].items():

            if team_code in codes:
                local_ids.append(local_id)

        print(
            f"  {season}: "
            f"{','.join(sorted(local_ids, key=int)) or 'NOT FOUND'}"
        )

    print()

print("=" * 78)
print("AUDIT COMPLETE")
print("=" * 78)
