import csv
import os
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")

CLUBS = {
    "Manchester City": {
        "folder": "Man_City_43",
        "persistent_id": "43",
    },
    "West Ham": {
        "folder": "West_Ham_21",
        "persistent_id": "21",
    },
    "Bournemouth": {
        "folder": "Bournemouth_91",
        "persistent_id": "91",
    },
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
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalise_archive_kickoff(value):
    """
    Historical club archive kickoff appears to be naive UK local time.
    Convert it to UTC so it can be compared with fixtures_master.
    """
    local_dt = datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=UK)

    return local_dt.astimezone(ZoneInfo("UTC"))


def normalise_fixture_kickoff(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(ZoneInfo("UTC"))


def event_rows_for_season(folder, season):
    path = os.path.join(
        PL_ROOT,
        folder,
        "events_stats",
        f"{season}_events_stats.csv",
    )

    if not os.path.isfile(path):
        return None, path

    return load_csv(path), path


def build_fixture_indexes(fixtures):
    exact = defaultdict(list)
    fallback = defaultdict(list)

    for row in fixtures:
        kickoff = normalise_fixture_kickoff(
            row["kickoff_time"]
        )

        home_id = row["home_team_id"]
        away_id = row["away_team_id"]

        exact_key = (
            row["season"],
            str(int(float(row["gameweek"]))),
            kickoff,
            "home",
        )
        exact[exact_key].append(row)

        exact_key = (
            row["season"],
            str(int(float(row["gameweek"]))),
            kickoff,
            "away",
        )
        exact[exact_key].append(row)

        # Fallback deliberately uses date rather than time.
        # This is ONLY for diagnosis; it is never treated as
        # equivalent to an exact match without being flagged.
        date_key = (
            row["season"],
            str(int(float(row["gameweek"]))),
            kickoff.date(),
            "home",
        )
        fallback[date_key].append(row)

        date_key = (
            row["season"],
            str(int(float(row["gameweek"]))),
            kickoff.date(),
            "away",
        )
        fallback[date_key].append(row)

    return exact, fallback


def audit_club(club_name, config, fixtures):
    exact, fallback = build_fixture_indexes(fixtures)

    all_results = []

    for season in SEASONS:
        rows, path = event_rows_for_season(
            config["folder"],
            season,
        )

        if rows is None:
            all_results.append({
                "season": season,
                "status": "MISSING_SOURCE",
                "persistent_id": config["persistent_id"],
                "local_ids": set(),
                "matched": 0,
                "unmatched": 0,
                "ambiguous": 0,
                "fallback": 0,
                "examples": [path],
            })
            continue

        # Keep only aggregate rows for the persistent club.
        rows = [
            row for row in rows
            if str(row.get("team_id", "")) == str(
                config["persistent_id"]
            )
        ]

        matched = 0
        unmatched = 0
        ambiguous = 0
        fallback_count = 0
        local_ids = set()
        examples = []

        # A source event may occasionally be duplicated. We audit
        # each row first, but record all results.
        for event in rows:
            try:
                gameweek = str(
                    int(float(event["gameweek"]))
                )

                kickoff_utc = normalise_archive_kickoff(
                    event["kickoff"]
                )

            except Exception as exc:
                unmatched += 1
                examples.append(
                    f"BAD_SOURCE_ROW: {exc}"
                )
                continue

            venue = str(
                event.get("venue", "")
            ).strip().lower()

            side = (
                "home"
                if venue == "home"
                else "away"
                if venue == "away"
                else None
            )

            if side is None:
                unmatched += 1
                examples.append(
                    f"UNKNOWN_VENUE matchId={event.get('matchId')}"
                )
                continue

            key = (
                season,
                gameweek,
                kickoff_utc,
                side,
            )

            candidates = exact.get(key, [])

            if len(candidates) == 1:
                fixture = candidates[0]
                matched += 1

                local_id = (
                    fixture["home_team_id"]
                    if side == "home"
                    else fixture["away_team_id"]
                )

                local_ids.add(str(local_id))
                continue

            if len(candidates) > 1:
                ambiguous += 1
                examples.append(
                    "AMBIGUOUS_EXACT "
                    f"matchId={event.get('matchId')} "
                    f"season={season} "
                    f"gameweek={gameweek} "
                    f"kickoff={kickoff_utc.isoformat()} "
                    f"venue={venue} "
                    f"candidates={len(candidates)}"
                )
                continue

            # Diagnostic fallback: same season + gameweek + date +
            # venue. This is not counted as an exact match.
            fallback_key = (
                season,
                gameweek,
                kickoff_utc.date(),
                side,
            )

            fallback_candidates = fallback.get(
                fallback_key,
                []
            )

            if len(fallback_candidates) == 1:
                fallback_count += 1

                fixture = fallback_candidates[0]

                local_id = (
                    fixture["home_team_id"]
                    if side == "home"
                    else fixture["away_team_id"]
                )

                local_ids.add(str(local_id))

                examples.append(
                    "DATE_FALLBACK "
                    f"matchId={event.get('matchId')} "
                    f"source_kickoff={event.get('kickoff')} "
                    f"fixture_kickoff={fixture.get('kickoff_time')} "
                    f"local_team_id={local_id}"
                )
                continue

            if len(fallback_candidates) > 1:
                ambiguous += 1
                examples.append(
                    "AMBIGUOUS_DATE_FALLBACK "
                    f"matchId={event.get('matchId')} "
                    f"candidates={len(fallback_candidates)}"
                )
                continue

            unmatched += 1

            if len(examples) < 5:
                examples.append(
                    "UNMATCHED "
                    f"matchId={event.get('matchId')} "
                    f"gameweek={gameweek} "
                    f"kickoff={kickoff_utc.isoformat()} "
                    f"venue={venue}"
                )

        all_results.append({
            "season": season,
            "status": "OK",
            "persistent_id": config["persistent_id"],
            "local_ids": local_ids,
            "matched": matched,
            "unmatched": unmatched,
            "ambiguous": ambiguous,
            "fallback": fallback_count,
            "examples": examples[:5],
            "source_rows": len(rows),
        })

    return all_results


fixtures = load_csv(FIXTURE_FILE)

print()
print("=" * 78)
print(" THREE-CLUB IDENTITY FORENSIC AUDIT")
print("=" * 78)
print()
print(
    "Matching evidence: season + gameweek + UK-local kickoff "
    "converted to UTC + home/away status."
)
print()
print("Date-only matches are diagnostic fallbacks and are NOT treated")
print("as equivalent to exact matches.")
print()

for club_name, config in CLUBS.items():

    results = audit_club(
        club_name,
        config,
        fixtures,
    )

    print("=" * 78)
    print(club_name)
    print(
        f"Persistent archive ID: {config['persistent_id']}"
    )
    print("=" * 78)

    overall_local_ids = set()
    total_matched = 0
    total_unmatched = 0
    total_ambiguous = 0
    total_fallback = 0

    for result in results:

        ids_text = (
            ",".join(
                sorted(
                    result["local_ids"],
                    key=int,
                )
            )
            if result["local_ids"]
            else "-"
        )

        print(
            f"{result['season']} | "
            f"source_rows={result.get('source_rows', 0):>2} | "
            f"exact={result['matched']:>2} | "
            f"fallback={result['fallback']:>2} | "
            f"unmatched={result['unmatched']:>2} | "
            f"ambiguous={result['ambiguous']:>2} | "
            f"local_id={ids_text}"
        )

        overall_local_ids.update(
            result["local_ids"]
        )

        total_matched += result["matched"]
        total_unmatched += result["unmatched"]
        total_ambiguous += result["ambiguous"]
        total_fallback += result["fallback"]

        for example in result["examples"]:
            print(
                f"    {example}"
            )

    print()
    print(
        f"UNIQUE LOCAL IDS ACROSS 10 SEASONS: "
        f"{', '.join(sorted(overall_local_ids, key=int))}"
    )
    print(
        f"TOTAL EXACT MATCHES: {total_matched}"
    )
    print(
        f"TOTAL DATE FALLBACKS: {total_fallback}"
    )
    print(
        f"TOTAL UNMATCHED: {total_unmatched}"
    )
    print(
        f"TOTAL AMBIGUOUS: {total_ambiguous}"
    )
    print()

print("=" * 78)
print("AUDIT COMPLETE")
print("=" * 78)
