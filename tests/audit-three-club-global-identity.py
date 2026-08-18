import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta
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

# The archive kickoff appears to be UK local time.
# Candidate matching allows a small tolerance because of
# source inconsistencies / postponed fixtures.
KICKOFF_TOLERANCE_HOURS = 18


def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fixture_kickoff(row):
    return datetime.fromisoformat(
        row["kickoff_time"].replace("Z", "+00:00")
    ).astimezone(UTC)


def archive_kickoff(value):
    local_dt = datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=UK)

    return local_dt.astimezone(UTC)


def event_file(folder, season):
    return os.path.join(
        PL_ROOT,
        folder,
        "events_stats",
        f"{season}_events_stats.csv",
    )


def normalise_gameweek(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def side_from_venue(value):
    venue = str(value or "").strip().lower()

    if venue == "home":
        return "home"

    if venue == "away":
        return "away"

    return None


def build_candidate_graph(events, fixtures, season):
    """
    Candidate edge score:
      + very strong: same gameweek
      + strong: same venue side
      + strong: close kickoff
      + small bonus: exact calendar date

    We don't use goalsFor/goalsAgainst because those fields are
    incomplete in the historical event source.
    """

    season_fixtures = [
        row for row in fixtures
        if row["season"] == season
    ]

    candidate_graph = {}
    edge_score = {}

    for event_index, event in enumerate(events):

        ew = normalise_gameweek(event.get("gameweek"))
        ek = archive_kickoff(event["kickoff"])
        side = side_from_venue(event.get("venue"))

        candidates = []

        for fixture_index, fixture in enumerate(season_fixtures):

            fw = normalise_gameweek(fixture.get("gameweek"))

            if ew is not None and fw != ew:
                continue

            fixture_side = (
                "home"
                if side == "home"
                else "away"
            )

            fk = fixture_kickoff(fixture)

            delta_hours = abs(
                (fk - ek).total_seconds()
            ) / 3600.0

            if delta_hours > KICKOFF_TOLERANCE_HOURS:
                continue

            score = 0.0

            if ew == fw:
                score += 100.0

            if fixture_side == side:
                score += 50.0

            if fk.date() == ek.date():
                score += 30.0

            # Smaller time difference = stronger match.
            score += max(
                0.0,
                20.0 - delta_hours
            )

            candidates.append(fixture_index)
            edge_score[
                (event_index, fixture_index)
            ] = score

        candidate_graph[event_index] = candidates

    return season_fixtures, candidate_graph, edge_score


def maximum_matching(candidate_graph, edge_score):
    """
    Find a maximum-cardinality matching using DFS augmenting paths.

    Because candidate lists are sorted by edge score, ties are handled
    consistently. This is an audit tool, not an optimiser that gets
    to decide football identity on its own.
    """

    ordered_candidates = {}

    for event_index, candidates in candidate_graph.items():

        ordered_candidates[event_index] = sorted(
            candidates,
            key=lambda fixture_index: (
                -edge_score[(event_index, fixture_index)],
                fixture_index,
            )
        )

    fixture_to_event = {}

    def visit(event_index, seen):

        for fixture_index in ordered_candidates[event_index]:

            if fixture_index in seen:
                continue

            seen.add(fixture_index)

            previous_event = fixture_to_event.get(
                fixture_index
            )

            if (
                previous_event is None
                or visit(previous_event, seen)
            ):
                fixture_to_event[
                    fixture_index
                ] = event_index

                return True

        return False

    matched = 0

    for event_index in ordered_candidates:
        if visit(event_index, set()):
            matched += 1

    event_to_fixture = {
        event_index: fixture_index
        for fixture_index, event_index
        in fixture_to_event.items()
    }

    return event_to_fixture, matched


def audit_season(
    club_name,
    folder,
    persistent_id,
    season,
    fixtures,
):
    path = event_file(folder, season)

    if not os.path.isfile(path):
        return {
            "season": season,
            "status": "NO_EVENT_FILE",
            "events": 0,
            "matched": 0,
            "unmatched_events": 0,
            "duplicate_fixture_use": 0,
            "candidate_ambiguous": 0,
            "local_ids": set(),
            "examples": [path],
        }

    rows = [
        row
        for row in load_csv(path)
        if str(row.get("team_id", "")) == persistent_id
    ]

    season_fixtures, graph, scores = build_candidate_graph(
        rows,
        fixtures,
        season,
    )

    # A useful sanity condition.
    if len(rows) != 38:
        row_warning = (
            f"expected 38 events, found {len(rows)}"
        )
    else:
        row_warning = None

    # Count events with multiple candidates before global matching.
    candidate_ambiguous = sum(
        1
        for candidates in graph.values()
        if len(candidates) > 1
    )

    event_to_fixture, matched = maximum_matching(
        graph,
        scores,
    )

    local_ids = set()
    examples = []

    for event_index, fixture_index in event_to_fixture.items():

        event = rows[event_index]
        fixture = season_fixtures[fixture_index]

        side = side_from_venue(
            event.get("venue")
        )

        local_id = (
            fixture["home_team_id"]
            if side == "home"
            else fixture["away_team_id"]
        )

        local_ids.add(str(local_id))

    unmatched_events = len(rows) - matched

    # Record representative unresolved cases.
    for event_index, candidates in graph.items():

        if event_index in event_to_fixture:
            continue

        if len(examples) >= 5:
            break

        event = rows[event_index]

        examples.append(
            "UNMATCHED "
            f"matchId={event.get('matchId')} "
            f"GW={event.get('gameweek')} "
            f"kickoff={event.get('kickoff')} "
            f"venue={event.get('venue')} "
            f"candidates={len(candidates)}"
        )

    # Decide how strong the season-level mapping is.
    if matched == 38 and len(local_ids) == 1:
        status = "STRONG"

    elif matched == 38 and len(local_ids) > 1:
        status = "IDENTITY_CONFLICT"

    elif matched < 38:
        status = "INCOMPLETE"

    else:
        status = "REVIEW"

    if row_warning:
        examples.insert(0, row_warning)

    return {
        "season": season,
        "status": status,
        "events": len(rows),
        "matched": matched,
        "unmatched_events": unmatched_events,
        "duplicate_fixture_use": 0,
        "candidate_ambiguous": candidate_ambiguous,
        "local_ids": local_ids,
        "examples": examples,
    }


fixtures = load_csv(FIXTURE_FILE)

print()
print("=" * 82)
print(" THREE-CLUB GLOBAL IDENTITY AUDIT")
print("=" * 82)
print()
print(
    "Persistent club event records are matched to season fixtures using:"
)
print(
    "season + gameweek + venue + UK-local kickoff converted to UTC"
)
print()
print(
    "The solver enforces one event -> one fixture and one fixture -> one event."
)
print(
    "It does NOT use goalsFor/goalsAgainst because those fields are incomplete."
)
print()

overall = {}

for club_name, (folder, persistent_id) in CLUBS.items():

    print("=" * 82)
    print(
        f"{club_name} "
        f"(persistent ID {persistent_id})"
    )
    print("=" * 82)

    season_results = []

    for season in SEASONS:

        result = audit_season(
            club_name,
            folder,
            persistent_id,
            season,
            fixtures,
        )

        season_results.append(result)

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
            f"{season} | "
            f"status={result['status']:<17} "
            f"events={result['events']:>2} "
            f"matched={result['matched']:>2} "
            f"unmatched={result['unmatched_events']:>2} "
            f"candidate_ambiguous={result['candidate_ambiguous']:>2} "
            f"local_id={ids_text}"
        )

        for example in result["examples"]:
            print(
                f"    {example}"
            )

    all_ids = set()

    for result in season_results:
        all_ids.update(
            result["local_ids"]
        )

    print()
    print(
        "LOCAL IDS OBSERVED ACROSS SEASONS: "
        + (
            ", ".join(
                sorted(all_ids, key=int)
            )
            if all_ids
            else "-"
        )
    )

    strong_seasons = [
        result["season"]
        for result in season_results
        if result["status"] == "STRONG"
    ]

    print(
        "STRONG SEASONS: "
        + (
            ", ".join(strong_seasons)
            if strong_seasons
            else "-"
        )
    )

    overall[club_name] = season_results

print()
print("=" * 82)
print("AUDIT COMPLETE")
print("=" * 82)
print()
