import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")

CLUBS = {
    "Man City": ("Man_City_43", "43"),
    "West Ham": ("West_Ham_21", "21"),
    "Bournemouth": ("Bournemouth_91", "91"),
}

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

UK = ZoneInfo("Europe/London")


def load_csv(path):
    with open(path, "r", encoding="latin-1", newline="") as f:
        return list(csv.DictReader(f))


fixtures = load_csv(FIXTURE_FILE)

print()
print("=" * 78)
print(" FIRST-FIXTURE TEAM-ID GENERATION AUDIT")
print("=" * 78)
print()

results = []

for club, (folder, persistent_id) in CLUBS.items():

    print(f"{club} | persistent club ID = {persistent_id}")
    print("-" * 78)

    for season in SEASONS:

        path = os.path.join(
            PL_ROOT,
            folder,
            "events_stats",
            f"{season}_events_stats.csv",
        )

        if not os.path.isfile(path):
            print(f"{season}: NO EVENT FILE")
            continue

        rows = load_csv(path)

        # The first row in these files is the first recorded fixture.
        first = rows[0]

        archive_local = datetime.strptime(
            first["kickoff"],
            "%Y-%m-%d %H:%M:%S",
        ).replace(tzinfo=UK)

        archive_utc = archive_local.astimezone(
            ZoneInfo("UTC")
        )

        gameweek = int(float(first["gameweek"]))
        venue = first["venue"].strip().lower()

        candidates = []

        for fixture in fixtures:

            if fixture["season"] != season:
                continue

            if int(float(fixture["gameweek"])) != gameweek:
                continue

            fixture_time = datetime.fromisoformat(
                fixture["kickoff_time"].replace(
                    "Z",
                    "+00:00",
                )
            ).astimezone(ZoneInfo("UTC"))

            if fixture_time != archive_utc:
                continue

            candidates.append(fixture)

        local_ids = set()

        for fixture in candidates:

            if venue == "home":
                local_ids.add(
                    fixture["home_team_id"]
                )

            elif venue == "away":
                local_ids.add(
                    fixture["away_team_id"]
                )

        if len(local_ids) == 1:
            local_id = next(iter(local_ids))
        else:
            local_id = "AMBIGUOUS"

        print(
            f"{season}: "
            f"matchId={first['matchId']} | "
            f"archive={first['kickoff']} | "
            f"venue={first['venue']} | "
            f"fixture_candidates={len(candidates)} | "
            f"local_team_id={local_id}"
        )

        results.append(
            (
                season,
                club,
                local_id,
            )
        )

    print()

print("=" * 78)
print("COMPACT ID TABLE")
print("=" * 78)
print()

print(
    f"{'Season':<10}"
    f"{'Man City':>12}"
    f"{'West Ham':>12}"
    f"{'Bournemouth':>14}"
)

for season in SEASONS:

    values = {}

    for s, club, local_id in results:
        if s == season:
            values[club] = local_id

    print(
        f"{season:<10}"
        f"{values.get('Man City', '-'):>12}"
        f"{values.get('West Ham', '-'):>12}"
        f"{values.get('Bournemouth', '-'):>14}"
    )

print()
print("=" * 78)
print("AUDIT COMPLETE")
print("=" * 78)
