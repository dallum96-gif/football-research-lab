import csv
import os
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")

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
    with open(path, "r", encoding="latin-1", newline="") as handle:
        return list(csv.DictReader(handle))


def archive_to_utc(value):
    local = datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=UK)

    return local.astimezone(UTC)


def fixture_to_utc(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(UTC)


fixtures = load_csv(FIXTURE_FILE)

# Build lookup by season + exact kickoff.
fixture_lookup = defaultdict(list)

for fixture in fixtures:
    fixture_lookup[
        (
            fixture["season"],
            fixture_to_utc(fixture["kickoff_time"]),
        )
    ].append(fixture)


# Persistent club folders are the source-level club identities.
club_dirs = []

for entry in os.scandir(PL_ROOT):
    if not entry.is_dir():
        continue

    name = entry.name

    if "_" not in name:
        continue

    base, separator, code = name.rpartition("_")

    if not separator or not code.isdigit():
        continue

    # Ignore structural folders.
    if name in {"_badges", "_index", "_merged"}:
        continue

    club_dirs.append(
        {
            "folder": name,
            "club_name": base.replace("_", " "),
            "persistent_id": code,
        }
    )

club_dirs.sort(
    key=lambda x: x["club_name"].lower()
)


records = []


for club in club_dirs:

    for season in SEASONS:

        event_file = os.path.join(
            PL_ROOT,
            club["folder"],
            "events_stats",
            f"{season}_events_stats.csv",
        )

        if not os.path.isfile(event_file):
            continue

        rows = load_csv(event_file)

        if not rows:
            continue

        # First recorded match for this club-season.
        first = rows[0]

        try:
            kickoff_utc = archive_to_utc(
                first["kickoff"]
            )
        except Exception:
            records.append(
                {
                    "club_name": club["club_name"],
                    "persistent_id": club["persistent_id"],
                    "season": season,
                    "local_id": "INVALID_TIME",
                    "status": "REVIEW",
                }
            )
            continue

        candidates = fixture_lookup.get(
            (season, kickoff_utc),
            []
        )

        venue = first.get("venue", "").strip().lower()

        candidate_ids = set()

        for fixture in candidates:

            if venue == "home":
                candidate_ids.add(
                    str(fixture["home_team_id"])
                )

            elif venue == "away":
                candidate_ids.add(
                    str(fixture["away_team_id"])
                )

        if len(candidate_ids) == 1:

            local_id = next(
                iter(candidate_ids)
            )

            status = "VERIFIED"

        elif len(candidate_ids) == 0:

            local_id = "-"
            status = "UNRESOLVED"

        else:

            local_id = "/".join(
                sorted(candidate_ids, key=int)
            )
            status = "AMBIGUOUS"

        records.append(
            {
                "club_name": club["club_name"],
                "persistent_id": club["persistent_id"],
                "season": season,
                "local_id": local_id,
                "status": status,
            }
        )


print()
print("=" * 100)
print(" ALL CLUB FIRST-GAME IDENTITY AUDIT")
print("=" * 100)
print()

print(
    f"{'Club':<28}"
    f"{'Persistent':>10} "
    f"{'Season':<10}"
    f"{'Local ID':>10} "
    f"{'Status':<12}"
)

print("-" * 100)

for record in records:

    print(
        f"{record['club_name']:<28}"
        f"{record['persistent_id']:>10} "
        f"{record['season']:<10}"
        f"{record['local_id']:>10} "
        f"{record['status']:<12}"
    )


print()
print("=" * 100)
print(" ID TRANSITIONS")
print("=" * 100)
print()

by_club = defaultdict(list)

for record in records:
    by_club[record["persistent_id"]].append(record)

transition_count = 0

for persistent_id in sorted(
    by_club,
    key=lambda x: by_club[x][0]["club_name"].lower()
):

    club_records = sorted(
        by_club[persistent_id],
        key=lambda x: SEASONS.index(x["season"])
    )

    changes = []

    previous = None
    previous_season = None

    for record in club_records:

        local_id = record["local_id"]

        if (
            previous is not None
            and local_id not in {"-", "AMBIGUOUS", "INVALID_TIME", "UNRESOLVED"}
            and previous not in {"-", "AMBIGUOUS", "INVALID_TIME", "UNRESOLVED"}
            and local_id != previous
        ):
            changes.append(
                (
                    previous_season,
                    previous,
                    record["season"],
                    local_id,
                )
            )

        if local_id not in {
            "-",
            "AMBIGUOUS",
            "INVALID_TIME",
            "UNRESOLVED",
        }:
            previous = local_id
            previous_season = record["season"]

    if changes:
        transition_count += len(changes)

        club_name = club_records[0]["club_name"]

        print(
            f"{club_name} "
            f"(persistent ID {persistent_id})"
        )

        for (
            from_season,
            from_id,
            to_season,
            to_id,
        ) in changes:

            print(
                f"  {from_season} -> {to_season}: "
                f"{from_id} -> {to_id}"
            )

        print()


print("=" * 100)
print("SUMMARY")
print("=" * 100)

verified = sum(
    1 for r in records
    if r["status"] == "VERIFIED"
)

ambiguous = sum(
    1 for r in records
    if r["status"] == "AMBIGUOUS"
)

unresolved = sum(
    1 for r in records
    if r["status"] == "UNRESOLVED"
)

print(f"Club-season records: {len(records)}")
print(f"Verified:            {verified}")
print(f"Ambiguous:           {ambiguous}")
print(f"Unresolved:          {unresolved}")
print(f"Observed transitions:{transition_count}")

print()
print("=" * 100)
print("AUDIT COMPLETE")
print("=" * 100)
