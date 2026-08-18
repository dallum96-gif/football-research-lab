import csv
import os
from collections import Counter, defaultdict
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
    return datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=UK).astimezone(UTC)


def fixture_to_utc(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(UTC)


fixtures = load_csv(FIXTURE_FILE)

# Season + exact UTC kickoff -> fixture rows
fixture_lookup = defaultdict(list)

for fixture in fixtures:
    try:
        key = (
            fixture["season"],
            fixture_to_utc(
                fixture["kickoff_time"]
            ),
        )
        fixture_lookup[key].append(fixture)
    except Exception:
        pass


# Persistent club identities from pl_stats folders
clubs = []

for entry in os.scandir(PL_ROOT):

    if not entry.is_dir():
        continue

    if "_" not in entry.name:
        continue

    base, sep, code = entry.name.rpartition("_")

    if not sep or not code.isdigit():
        continue

    if entry.name in {
        "_badges",
        "_index",
        "_merged",
    }:
        continue

    clubs.append({
        "name": base.replace("_", " "),
        "folder": entry.name,
        "persistent_id": code,
    })

clubs.sort(
    key=lambda x: x["name"].lower()
)


def infer_local_id(club, season):

    event_file = os.path.join(
        PL_ROOT,
        club["folder"],
        "events_stats",
        f"{season}_events_stats.csv",
    )

    if not os.path.isfile(event_file):
        return {
            "status": "NO_SOURCE",
            "local_id": None,
            "evidence": 0,
            "distribution": {},
        }

    events = [
        row for row in load_csv(event_file)
        if str(row.get("team_id", "")).strip()
        == club["persistent_id"]
    ]

    observations = []

    for event in events:

        try:
            kickoff = archive_to_utc(
                event["kickoff"]
            )

            season_fixtures = fixture_lookup.get(
                (season, kickoff),
                []
            )

            venue = (
                str(event.get("venue", ""))
                .strip()
                .lower()
            )

            ids = set()

            for fixture in season_fixtures:

                if venue == "home":
                    ids.add(
                        str(fixture["home_team_id"])
                    )

                elif venue == "away":
                    ids.add(
                        str(fixture["away_team_id"])
                    )

            # Only accept the event when it identifies
            # one local team ID unambiguously.
            if len(ids) == 1:
                observations.append(
                    next(iter(ids))
                )

        except Exception:
            continue

    counts = Counter(observations)

    if not counts:
        return {
            "status": "UNRESOLVED",
            "local_id": None,
            "evidence": 0,
            "distribution": {},
        }

    best_id, best_count = counts.most_common(1)[0]
    total = sum(counts.values())

    # Confidence is based on agreement among clean observations.
    confidence = best_count / total

    if confidence == 1.0:
        status = "VERIFIED"

    elif confidence >= 0.80 and best_count >= 3:
        status = "LIKELY"

    else:
        status = "REVIEW"

    return {
        "status": status,
        "local_id": best_id,
        "evidence": total,
        "distribution": dict(
            counts.most_common()
        ),
    }


records = []

for club in clubs:

    for season in SEASONS:

        result = infer_local_id(
            club,
            season,
        )

        records.append({
            "club": club["name"],
            "persistent_id": club["persistent_id"],
            "season": season,
            **result,
        })


print()
print("=" * 100)
print(" ALL CLUB / SEASON LOCAL-ID AUDIT V2")
print("=" * 100)
print()

print(
    f"{'Club':<28}"
    f"{'Persistent':>10} "
    f"{'Season':<10}"
    f"{'Local ID':>10} "
    f"{'Evidence':>9} "
    f"{'Status':<12}"
)

print("-" * 100)

for record in records:

    print(
        f"{record['club']:<28}"
        f"{record['persistent_id']:>10} "
        f"{record['season']:<10}"
        f"{record['local_id'] or '-':>10} "
        f"{record['evidence']:>9} "
        f"{record['status']:<12}"
    )


print()
print("=" * 100)
print(" OBSERVED ID TRANSITIONS")
print("=" * 100)
print()

by_club = defaultdict(list)

for record in records:
    by_club[
        record["persistent_id"]
    ].append(record)


for persistent_id in sorted(
    by_club,
    key=lambda pid: by_club[pid][0]["club"].lower()
):

    club_records = sorted(
        by_club[persistent_id],
        key=lambda r: SEASONS.index(r["season"])
    )

    # Only compare verified/likely mappings.
    clean = [
        r for r in club_records
        if r["local_id"] is not None
        and r["status"] in {
            "VERIFIED",
            "LIKELY",
        }
    ]

    transitions = []

    for previous, current in zip(
        clean,
        clean[1:]
    ):

        if previous["local_id"] != current["local_id"]:

            transitions.append(
                (
                    previous["season"],
                    previous["local_id"],
                    current["season"],
                    current["local_id"],
                )
            )

    if transitions:

        print(
            f"{club_records[0]['club']} "
            f"(persistent ID {persistent_id})"
        )

        for transition in transitions:

            print(
                f"  {transition[0]} -> {transition[2]}: "
                f"{transition[1]} -> {transition[3]}"
            )

        print()


print("=" * 100)
print(" SUMMARY")
print("=" * 100)

status_counts = Counter(
    record["status"]
    for record in records
)

print(
    f"Club-season records: {len(records)}"
)

for status in (
    "VERIFIED",
    "LIKELY",
    "REVIEW",
    "UNRESOLVED",
    "NO_SOURCE",
):

    print(
        f"{status:<12}: "
        f"{status_counts.get(status, 0)}"
    )

print()
print("=" * 100)
print(" AUDIT COMPLETE")
print("=" * 100)
