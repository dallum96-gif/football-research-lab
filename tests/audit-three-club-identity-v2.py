import csv
import os
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")

CLUBS = {
    "Manchester City": ("Man_City_43", "43"),
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
UTC = ZoneInfo("UTC")


def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def archive_to_utc(value):
    local = datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=UK)

    return local.astimezone(UTC)


def fixture_to_utc(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(UTC)


def score_pair(event):
    gf = event.get("goalsFor", "")
    ga = event.get("goalsAgainst", "")

    if gf in ("", None) or ga in ("", None):
        return None

    try:
        return int(float(gf)), int(float(ga))
    except ValueError:
        return None


fixtures = load_csv(FIXTURE_FILE)

# Exact lookup with score included.
lookup = defaultdict(list)

for row in fixtures:
    kickoff = fixture_to_utc(row["kickoff_time"])
    season = row["season"]
    gameweek = str(int(float(row["gameweek"])))

    if row["home_score"] == "" or row["away_score"] == "":
        continue

    home_score = int(row["home_score"])
    away_score = int(row["away_score"])

    lookup[
        (
            season,
            gameweek,
            kickoff,
            "home",
            home_score,
            away_score,
        )
    ].append(row)

    lookup[
        (
            season,
            gameweek,
            kickoff,
            "away",
            away_score,
            home_score,
        )
    ].append(row)


print()
print("=" * 78)
print(" THREE-CLUB IDENTITY AUDIT V2")
print(" MATCHING SCORE AS AN ADDITIONAL KEY")
print("=" * 78)
print()

for club_name, (folder, persistent_id) in CLUBS.items():

    print("=" * 78)
    print(club_name)
    print(f"Persistent ID: {persistent_id}")
    print("=" * 78)

    all_local_ids = set()

    for season in SEASONS:

        path = os.path.join(
            PL_ROOT,
            folder,
            "events_stats",
            f"{season}_events_stats.csv",
        )

        if not os.path.isfile(path):
            print(
                f"{season} | NO EVENT FILE"
            )
            continue

        events = [
            row
            for row in load_csv(path)
            if str(row.get("team_id", "")) == persistent_id
        ]

        exact = 0
        ambiguous = 0
        unmatched = 0
        local_ids = set()

        for event in events:

            score = score_pair(event)

            if score is None:
                unmatched += 1
                continue

            try:
                gameweek = str(
                    int(float(event["gameweek"]))
                )

                kickoff = archive_to_utc(
                    event["kickoff"]
                )

            except Exception:
                unmatched += 1
                continue

            venue = str(
                event.get("venue", "")
            ).strip().lower()

            if venue not in ("home", "away"):
                unmatched += 1
                continue

            gf, ga = score

            key = (
                season,
                gameweek,
                kickoff,
                venue,
                gf,
                ga,
            )

            candidates = lookup.get(key, [])

            if len(candidates) == 1:

                fixture = candidates[0]

                local_id = (
                    fixture["home_team_id"]
                    if venue == "home"
                    else fixture["away_team_id"]
                )

                local_ids.add(str(local_id))
                exact += 1

            elif len(candidates) > 1:

                ambiguous += 1

            else:

                unmatched += 1

        all_local_ids.update(local_ids)

        print(
            f"{season} | "
            f"events={len(events):>2} | "
            f"exact={exact:>2} | "
            f"ambiguous={ambiguous:>2} | "
            f"unmatched={unmatched:>2} | "
            f"local_id="
            f"{','.join(sorted(local_ids, key=int)) or '-'}"
        )

    print()
    print(
        "ALL OBSERVED LOCAL IDS: "
        + ", ".join(
            sorted(all_local_ids, key=int)
        )
    )
    print()

print("=" * 78)
print("AUDIT COMPLETE")
print("=" * 78)
