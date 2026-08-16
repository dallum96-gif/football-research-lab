import argparse
import csv
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

PLAYER_DIR = os.path.join(
    ROOT,
    "_merged",
    "players"
)

FIXTURE_FILE = os.path.join(
    ROOT,
    "fixtures_master_corrected.csv"
)

IDENTITY_FILE = os.path.join(
    ROOT,
    "identity",
    "team_seasons.csv"
)

CORRECTIONS_FILE = os.path.join(
    ROOT,
    "identity",
    "data_quality",
    "fixture_corrections.csv"
)

QUERY_VERSION = "0.4.1"

METRICS = {
    "goals": "goals_scored",
    "assists": "assists",
    "minutes": "minutes",
    "points": "total_points",
    "bonus": "bonus",
    "bps": "bps",
    "xg": "expected_goals",
    "xa": "expected_assists",
    "xgi": "expected_goal_involvements",
    "saves": "saves",
    "clean_sheets": "clean_sheets",
    "yellow_cards": "yellow_cards",
    "red_cards": "red_cards",
}


def load_csv(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    for encoding in (
        "utf-8-sig",
        "cp1252",
        "latin-1",
    ):
        try:
            with open(
                path,
                "r",
                encoding=encoding,
                newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Could not decode CSV: {path}"
    )


def normalise_team_name(value):
    value = str(value or "").strip().casefold()

    replacements = {
        "_": " ",
        "-": " ",
        ".": "",
        "'": "",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    value = " ".join(value.split())

    aliases = {
        "man city": "manchester city",
        "manchester city": "manchester city",
        "mancity": "manchester city",

        "man utd": "manchester united",
        "man united": "manchester united",
        "manchester united": "manchester united",
        "manutd": "manchester united",

        "spurs": "tottenham hotspur",
        "tottenham": "tottenham hotspur",
        "tottenham hotspur": "tottenham hotspur",

        "a villa": "aston villa",
        "aston villa": "aston villa",

        "c palace": "crystal palace",
        "crystal palace": "crystal palace",

        "nottm forest": "nottingham forest",
        "nottingham forest": "nottingham forest",

        "west ham": "west ham united",
        "west ham united": "west ham united",

        "west brom": "west bromwich albion",
        "west bromwich albion": "west bromwich albion",

        "leeds": "leeds united",
        "leeds united": "leeds united",

        "newcastle": "newcastle united",
        "newcastle united": "newcastle united",

        "wolves": "wolverhampton wanderers",
        "wolverhampton wanderers": "wolverhampton wanderers",

        "brighton": "brighton and hove albion",
        "brighton and hove albion": "brighton and hove albion",

        "sheffield utd": "sheffield united",
        "sheffield united": "sheffield united",

        "bournemouth": "bournemouth",
        "brentford": "brentford",
        "arsenal": "arsenal",
        "chelsea": "chelsea",
        "everton": "everton",
        "fulham": "fulham",
        "liverpool": "liverpool",
        "burnley": "burnley",
        "leicester": "leicester city",
        "leicester city": "leicester city",
        "southampton": "southampton",
        "sunderland": "sunderland",
        "ipswich": "ipswich town",
        "ipswich town": "ipswich town",
        "norwich": "norwich city",
        "norwich city": "norwich city",
    }

    return aliases.get(
        value,
        value
    )


def load_identity_registry():
    rows, columns = load_csv(
        IDENTITY_FILE
    )

    required = {
        "season",
        "club_id",
        "canonical_name",
        "persistent_team_code",
        "local_team_id",
        "mapping_status",
    }

    missing = sorted(
        required - set(columns)
    )

    if missing:
        raise ValueError(
            "Identity registry is missing "
            "required columns: "
            + ", ".join(missing)
        )

    return rows


def resolve_team(
    season,
    search,
):
    if not season:
        raise ValueError(
            "--season is required when "
            "resolving a team by name."
        )

    rows = load_identity_registry()

    search_normalised = normalise_team_name(
        search
    )

    candidates = []

    for row in rows:

        if row["season"] != season:
            continue

        names = {
            normalise_team_name(
                row.get("canonical_name")
            ),
            normalise_team_name(
                row.get("source_name")
            ),
            normalise_team_name(
                row.get("club_id")
            ),
            str(
                row.get("persistent_team_code", "")
            ).strip().casefold(),
        }

        if search_normalised in names:
            candidates.append(row)

    # Direct persistent numeric code support.
    if not candidates and str(search).strip().isdigit():

        code = str(search).strip()

        candidates = [
            row
            for row in rows
            if (
                row["season"] == season
                and row["persistent_team_code"] == code
            )
        ]

    unique_codes = {
        row["persistent_team_code"]
        for row in candidates
    }

    if not candidates:
        raise ValueError(
            f"No team matching '{search}' "
            f"found in identity registry for "
            f"{season}."
        )

    if len(unique_codes) > 1:
        names = sorted(
            {
                row["canonical_name"]
                for row in candidates
            }
        )

        raise ValueError(
            "Team search was ambiguous. "
            "Candidates: "
            + ", ".join(names)
        )

    row = candidates[0]

    if row["mapping_status"] != "VERIFIED":
        raise ValueError(
            f"Identity mapping for "
            f"{row['canonical_name']} "
            f"in {season} is not verified."
        )

    return {
        "requested": search,
        "canonical_name": row["canonical_name"].replace("_", " "),
        "persistent_team_code": row[
            "persistent_team_code"
        ],
        "local_team_id": row[
            "local_team_id"
        ],
        "season": row["season"],
        "mapping_status": row[
            "mapping_status"
        ],
    }


def season_files():
    if not os.path.isdir(PLAYER_DIR):
        raise FileNotFoundError(
            f"Canonical player directory not found: "
            f"{PLAYER_DIR}"
        )

    files = {}

    for filename in os.listdir(
        PLAYER_DIR
    ):
        if filename.endswith(
            "_all_players_gw.csv"
        ):
            season = filename.replace(
                "_all_players_gw.csv",
                ""
            )

            files[season] = os.path.join(
                PLAYER_DIR,
                filename
            )

    return dict(
        sorted(files.items())
    )


def load_player_rows(season):
    files = season_files()

    if season not in files:
        available = ", ".join(files)

        raise ValueError(
            f"Unknown season '{season}'. "
            f"Available seasons: {available}"
        )

    rows, columns = load_csv(
        files[season]
    )

    return (
        rows,
        files[season],
        columns
    )



def to_number(value):
    if value in (None, ""):
        return 0.0

    return float(value)


def player_key(row):
    return (
        row.get("player_code")
        or row.get("element")
        or row.get("id")
        or row.get("name")
    )


def display_name(row):
    first = row.get(
        "first_name",
        ""
    ).strip()

    second = row.get(
        "second_name",
        ""
    ).strip()

    if first or second:
        return " ".join(
            part
            for part in (first, second)
            if part
        )

    name = row.get(
        "name",
        ""
    ).strip()

    if "_" in name:
        return name.rsplit(
            "_",
            1
        )[0].replace(
            "_",
            " "
        )

    return name


def top_players(
    season,
    metric,
    limit
):
    rows, path, columns = load_player_rows(
        season
    )

    source_column = METRICS[metric]

    if source_column not in columns:
        raise ValueError(
            f"Column '{source_column}' "
            f"is not present in {season}"
        )

    totals = {}
    names = {}

    for row in rows:

        key = player_key(row)

        totals[key] = (
            totals.get(
                key,
                0.0
            )
            + to_number(
                row.get(source_column)
            )
        )

        names[key] = display_name(row)

    ranked = sorted(
        totals.items(),
        key=lambda item: (
            -item[1],
            names[item[0]].lower()
        )
    )[:limit]

    return {
        "query_type": "top_players",
        "query_version": QUERY_VERSION,
        "season": season,
        "metric": metric,
        "source_column": source_column,
        "source_file": path,
        "source_rows": len(rows),
        "generated_at":
            datetime.now().astimezone().isoformat(),
        "results": [
            {
                "rank": rank,
                "player_key": key,
                "player": names[key],
                "value": value
            }
            for rank, (key, value)
            in enumerate(
                ranked,
                start=1
            )
        ]
    }


def player_total(
    season,
    player_search,
    metric
):
    rows, path, columns = load_player_rows(
        season
    )

    source_column = METRICS[metric]

    if source_column not in columns:
        raise ValueError(
            f"Column '{source_column}' "
            f"is not present in {season}"
        )

    search = player_search.casefold()

    matches = []

    for row in rows:

        name = display_name(row)

        if search in name.casefold():
            matches.append(row)

    if not matches:
        raise ValueError(
            f"No player matching "
            f"'{player_search}' found in {season}"
        )

    unique_players = {
        player_key(row)
        for row in matches
    }

    if len(unique_players) > 1:

        candidates = sorted(
            {
                display_name(row)
                for row in matches
            }
        )

        raise ValueError(
            "Player search was ambiguous. "
            "Candidates: "
            + ", ".join(candidates)
        )

    total = sum(
        to_number(
            row.get(source_column)
        )
        for row in matches
    )

    player = display_name(matches[0])

    return {
        "query_type": "player_total",
        "query_version": QUERY_VERSION,
        "season": season,
        "metric": metric,
        "player_search": player_search,
        "player": player,
        "player_key": player_key(
            matches[0]
        ),
        "source_column": source_column,
        "source_file": path,
        "source_rows": len(rows),
        "matching_rows": len(matches),
        "generated_at":
            datetime.now().astimezone().isoformat(),
        "result": {
            "value": total
        }
    }


def print_top_players(
    result,
    explain=False
):
    print()

    print(
        f"Top {len(result['results'])} "
        f"players by {result['metric']} "
        f"? {result['season']}"
    )

    print()

    print(
        f"{'Rank':>4}  "
        f"{'Player':<40}  "
        f"{'Value':>10}"
    )

    print("-" * 60)

    for item in result["results"]:

        value = item["value"]

        formatted = (
            str(int(value))
            if float(value).is_integer()
            else f"{value:.2f}"
        )

        print(
            f"{item['rank']:>4}  "
            f"{item['player']:<40}  "
            f"{formatted:>10}"
        )

    if explain:

        print()
        print("Evidence")
        print("-------")
        print(
            f"Query version: "
            f"{result['query_version']}"
        )
        print(
            f"Source file:   "
            f"{result['source_file']}"
        )
        print(
            f"Source column: "
            f"{result['source_column']}"
        )
        print(
            f"Rows scanned:  "
            f"{result['source_rows']}"
        )
        print(
            f"Generated:     "
            f"{result['generated_at']}"
        )


def print_player_total(
    result,
    explain=False
):
    value = result[
        "result"
    ]["value"]

    formatted = (
        str(int(value))
        if float(value).is_integer()
        else f"{value:.2f}"
    )

    print()

    print(
        f"{result['player']} "
        f"? {result['metric']} "
        f"? {result['season']}"
    )

    print()

    print(
        f"Value: {formatted}"
    )

    if explain:

        print()
        print("Evidence")
        print("-------")
        print(
            f"Query version: "
            f"{result['query_version']}"
        )
        print(
            f"Source file:   "
            f"{result['source_file']}"
        )
        print(
            f"Source column: "
            f"{result['source_column']}"
        )
        print(
            f"Rows scanned:  "
            f"{result['source_rows']}"
        )
        print(
            f"Rows contributing: "
            f"{result['matching_rows']}"
        )
        print(
            f"Generated: "
            f"{result['generated_at']}"
        )


def load_fixture_corrections():
    if not os.path.isfile(CORRECTIONS_FILE):
        return {}

    rows, _ = load_csv(
        CORRECTIONS_FILE
    )

    return {
        (
            row["season"],
            row["fixture_id"],
        ): row
        for row in rows
    }


def apply_fixture_corrections(rows):
    corrections = load_fixture_corrections()

    output = []

    for row in rows:

        working = dict(row)

        key = (
            row["season"],
            row["fixture_id"],
        )

        correction = corrections.get(key)

        # Preserve the raw scheduled kickoff.
        working["scheduled_kickoff_time"] = (
            row["kickoff_time"]
        )

        if correction:

            working["kickoff_time"] = (
                correction["actual_kickoff"]
            )

            working["home_score"] = (
                correction["home_score"]
            )

            working["away_score"] = (
                correction["away_score"]
            )

            working["data_corrected"] = "true"

            working["correction_status"] = (
                correction["status"]
            )

            working["correction_source"] = (
                correction["source"]
            )

        else:

            working["data_corrected"] = "false"
            working["correction_status"] = ""
            working["correction_source"] = ""

        output.append(working)

    return output


def load_fixtures():
    rows, columns = load_csv(
        FIXTURE_FILE
    )

    required = {
        "season",
        "fixture_id",
        "fixture_code",
        "kickoff_time",
        "gameweek",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score",
    }

    missing = sorted(
        required - set(columns)
    )

    if missing:
        raise ValueError(
            "Fixture master is missing "
            "required columns: "
            + ", ".join(missing)
        )

    return apply_fixture_corrections(
        rows
    )


def fixture_result(
    row,
    team_id
):
    home_id = str(
        row["home_team_id"]
    )

    away_id = str(
        row["away_team_id"]
    )

    if str(team_id) == home_id:

        if (
            row["home_score"] == ""
            or row["away_score"] == ""
        ):
            return "UNPLAYED"

        home_score = int(
            row["home_score"]
        )

        away_score = int(
            row["away_score"]
        )

        if home_score > away_score:
            return "W"

        if home_score < away_score:
            return "L"

        return "D"

    if str(team_id) == away_id:

        if (
            row["home_score"] == ""
            or row["away_score"] == ""
        ):
            return "UNPLAYED"

        home_score = int(
            row["home_score"]
        )

        away_score = int(
            row["away_score"]
        )

        if away_score > home_score:
            return "W"

        if away_score < home_score:
            return "L"

        return "D"

    return None


def query_fixtures(
    season=None,
    team_id=None,
    opponent_id=None,
    team=None,
    opponent=None,
    venue=None,
    result=None,
    limit=100
):

    rows = load_fixtures()

    identity_evidence = {
        "identity_file":
            IDENTITY_FILE,
        "team":
            None,
        "opponent":
            None,
    }

    resolved_team = None
    resolved_opponent = None

    if team:

        resolved_team = resolve_team(
            season,
            team
        )

        team_id = resolved_team[
            "local_team_id"
        ]

        identity_evidence["team"] = (
            resolved_team
        )

    if opponent:

        resolved_opponent = resolve_team(
            season,
            opponent
        )

        opponent_id = resolved_opponent[
            "local_team_id"
        ]

        identity_evidence["opponent"] = (
            resolved_opponent
        )

    matches = []

    selected_team_id = (
        str(team_id)
        if team_id is not None
        else None
    )

    selected_opponent_id = (
        str(opponent_id)
        if opponent_id is not None
        else None
    )

    for row in rows:

        if (
            season
            and row["season"] != season
        ):
            continue

        home_id = str(
            row["home_team_id"]
        )

        away_id = str(
            row["away_team_id"]
        )

        if selected_team_id:

            if selected_team_id not in {
                home_id,
                away_id,
            }:
                continue

        if selected_opponent_id:

            if selected_team_id:

                selected_opponent = (
                    away_id
                    if home_id
                    == selected_team_id
                    else home_id
                )

                if (
                    selected_opponent
                    != selected_opponent_id
                ):
                    continue

            elif selected_opponent_id not in {
                home_id,
                away_id,
            }:
                continue

        if venue and selected_team_id:

            if (
                venue == "home"
                and home_id != selected_team_id
            ):
                continue

            if (
                venue == "away"
                and away_id != selected_team_id
            ):
                continue

        if result and selected_team_id:

            if (
                fixture_result(
                    row,
                    selected_team_id
                )
                != result.upper()
            ):
                continue

        matches.append(row)

    matches.sort(
        key=lambda row: (
            datetime.fromisoformat(
                row[
                    "kickoff_time"
                ].replace(
                    "Z",
                    "+00:00"
                )
            ),
            row["season"],
            int(row["fixture_id"]),
        )
    )

    # Enrich fixture rows with canonical team names.
    identity_rows = load_identity_registry()

    name_lookup = {
        (
            item["season"],
            item["local_team_id"],
        ): item["canonical_name"].replace("_", " ")
        for item in identity_rows
    }

    enriched_matches = []

    for row in matches:
        enriched = dict(row)

        enriched["home_team_name"] = name_lookup.get(
            (
                row["season"],
                str(row["home_team_id"]),
            ),
            f"ID {row['home_team_id']}",
        )

        enriched["away_team_name"] = name_lookup.get(
            (
                row["season"],
                str(row["away_team_id"]),
            ),
            f"ID {row['away_team_id']}",
        )

        enriched_matches.append(enriched)

    matches = enriched_matches

    total_matches = len(matches)

    if limit:
        matches = matches[:limit]

    return {
        "query_type":
            "fixtures",

        "query_version":
            QUERY_VERSION,

        "source_file":
            FIXTURE_FILE,

        "identity_source_file":
            IDENTITY_FILE,

        "generated_at":
            datetime.now().astimezone().isoformat(),

        "filters": {
            "season":
                season,

            "team":
                team,

            "opponent":
                opponent,

            "team_id":
                selected_team_id,

            "opponent_id":
                selected_opponent_id,

            "venue":
                venue,

            "result": (
                result.upper()
                if result
                else None
            ),
        },

        "identity_resolution":
            identity_evidence,

        "total_matches":
            total_matches,

        "returned_matches":
            len(matches),

        "results":
            matches,
    }


def fixture_detail(
    season,
    fixture_id,
):
    if not season:
        raise ValueError("season is required")

    if fixture_id in (None, ""):
        raise ValueError("fixture_id is required")

    fixtures = load_fixtures()

    matches = [
        row
        for row in fixtures
        if row["season"] == str(season)
        and str(row["fixture_id"]) == str(fixture_id)
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one fixture for "
            f"{season}/{fixture_id}; found {len(matches)}"
        )

    fixture = dict(matches[0])

    identity_rows = load_identity_registry()

    names = {
        (
            row["season"],
            str(row["local_team_id"]),
        ): row["canonical_name"].replace("_", " ")
        for row in identity_rows
    }

    fixture["home_team_name"] = names.get(
        (
            season,
            str(fixture["home_team_id"]),
        ),
        f"ID {fixture['home_team_id']}",
    )

    fixture["away_team_name"] = names.get(
        (
            season,
            str(fixture["away_team_id"]),
        ),
        f"ID {fixture['away_team_id']}",
    )

    from match_stats import fixture_stats

    stats = fixture_stats(
        fixture,
        identity_rows,
    )

    return {
        "query_type": "fixture_detail",
        "query_version": QUERY_VERSION,
        "fixture": fixture,
        "stats": stats,
        "provenance": {
            "canonical_source": FIXTURE_FILE,
            "identity_source": IDENTITY_FILE,
            "correction_source": CORRECTIONS_FILE,
            "source_match_id": stats.get(
                "source_match_id"
            ),
        },
        "generated_at":
            datetime.now().astimezone().isoformat(),
    }

def team_form(
    season,
    team=None,
    team_id=None,
):
    if not season:
        raise ValueError("--season is required")

    if team and team_id:
        raise ValueError(
            "Use either team or team_id, not both."
        )

    if team is None and team_id is None:
        raise ValueError(
            "Either team or team_id is required."
        )

    fixture_query = query_fixtures(
        season=season,
        team=team,
        team_id=team_id,
        limit=None,
    )

    selected_team_id = fixture_query[
        "filters"
    ]["team_id"]

    completed = []

    for row in fixture_query["results"]:
        result_code = fixture_result(
            row,
            selected_team_id,
        )

        if result_code == "UNPLAYED":
            continue

        if (
            str(row["home_team_id"])
            == str(selected_team_id)
        ):
            goals_for = int(row["home_score"])
            goals_against = int(row["away_score"])
        else:
            goals_for = int(row["away_score"])
            goals_against = int(row["home_score"])

        completed.append(
            {
                **row,
                "result": result_code,
                "points": {
                    "W": 3,
                    "D": 1,
                    "L": 0,
                }[result_code],
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": (
                    goals_for - goals_against
                ),
                "clean_sheet": (
                    goals_against == 0
                ),
                "scored": (
                    goals_for > 0
                ),
            }
        )

    completed.sort(
        key=lambda row: datetime.fromisoformat(
            row["kickoff_time"].replace(
                "Z",
                "+00:00",
            )
        )
    )

    def current_streak(predicate):
        total = 0

        for row in reversed(completed):
            if not predicate(row):
                break

            total += 1

        return total

    def window_summary(window):
        recent = completed[-window:]

        return {
            "matches": len(recent),
            "results": [
                row["result"]
                for row in recent
            ],
            "points": sum(
                row["points"]
                for row in recent
            ),
            "goals_for": sum(
                row["goals_for"]
                for row in recent
            ),
            "goals_against": sum(
                row["goals_against"]
                for row in recent
            ),
            "goal_difference": sum(
                row["goal_difference"]
                for row in recent
            ),
        }

    windows = {
        "3": window_summary(3),
        "5": window_summary(5),
    }

    streaks = {
        "current_win_streak": current_streak(
            lambda row: row["result"] == "W"
        ),
        "current_unbeaten_streak": current_streak(
            lambda row: row["result"] in {"W", "D"}
        ),
        "current_loss_streak": current_streak(
            lambda row: row["result"] == "L"
        ),
        "current_clean_sheet_streak": current_streak(
            lambda row: row["clean_sheet"]
        ),
        "current_scoring_streak": current_streak(
            lambda row: row["scored"]
        ),
    }

    return {
        "query_type": "team_form",
        "query_version": QUERY_VERSION,
        "season": season,
        "matches": completed,
        "windows": windows,
        "streaks": streaks,
        "excluded_unplayed": (
            fixture_query["total_matches"]
            - len(completed)
        ),
        "filters": fixture_query["filters"],
        "identity_resolution": (
            fixture_query[
                "identity_resolution"
            ]
        ),
        "source_file": fixture_query[
            "source_file"
        ],
        "identity_source_file": (
            fixture_query[
                "identity_source_file"
            ]
        ),
    }

def team_summary(
    season,
    team=None,
    team_id=None,
):
    if not season:
        raise ValueError("--season is required")

    if team and team_id:
        raise ValueError(
            "Use either --team or --team-id, not both."
        )

    identity = None

    if team:
        identity = resolve_team(season, team)
        team_id = identity["local_team_id"]

    if team_id is None:
        raise ValueError(
            "Either --team or --team-id is required."
        )

    team_id = str(team_id)
    rows = load_fixtures()

    selected = [
        row
        for row in rows
        if (
            row["season"] == season
            and team_id in {
                str(row["home_team_id"]),
                str(row["away_team_id"]),
            }
        )
    ]

    selected.sort(
        key=lambda row: datetime.fromisoformat(
            row["kickoff_time"].replace("Z", "+00:00")
        )
    )

    identity_rows = load_identity_registry()

    name_lookup = {
        (
            row["season"],
            row["local_team_id"],
        ): row["canonical_name"].replace("_", " ")
        for row in identity_rows
    }

    played = 0
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    points = 0
    unplayed = []

    for row in selected:

        if (
            row["home_score"] == ""
            or row["away_score"] == ""
        ):
            unplayed.append({
                "season": row["season"],
                "fixture_id": row["fixture_id"],
                "gameweek": row["gameweek"],
                "kickoff_time": row["kickoff_time"],
                "home_team_id": row["home_team_id"],
                "away_team_id": row["away_team_id"],
                "home_team_name": name_lookup.get(
                    (
                        row["season"],
                        str(row["home_team_id"]),
                    ),
                    f"ID {row['home_team_id']}",
                ),
                "away_team_name": name_lookup.get(
                    (
                        row["season"],
                        str(row["away_team_id"]),
                    ),
                    f"ID {row['away_team_id']}",
                ),
            })
            continue

        played += 1

        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        if str(row["home_team_id"]) == team_id:
            goals_for += home_score
            goals_against += away_score

            if home_score > away_score:
                wins += 1
                points += 3
            elif home_score == away_score:
                draws += 1
                points += 1
            else:
                losses += 1

        else:
            goals_for += away_score
            goals_against += home_score

            if away_score > home_score:
                wins += 1
                points += 3
            elif away_score == home_score:
                draws += 1
                points += 1
            else:
                losses += 1

    if identity:
        team_name = identity["canonical_name"]
    else:
        matching = [
            row
            for row in identity_rows
            if (
                row["season"] == season
                and row["local_team_id"] == team_id
            )
        ]

        team_name = (
            matching[0]["canonical_name"].replace("_", " ")
            if len(matching) == 1
            else f"ID {team_id}"
        )

    return {
        "query_type": "team_summary",
        "query_version": QUERY_VERSION,
        "season": season,
        "team": team_name,
        "team_id": team_id,
        "persistent_team_code": (
            identity["persistent_team_code"]
            if identity
            else None
        ),
        "identity_resolution": identity,
        "source_file": FIXTURE_FILE,
        "identity_source_file": IDENTITY_FILE,
        "generated_at": datetime.now().astimezone().isoformat(),
        "summary": {
            "matches_in_schedule": len(selected),
            "played": played,
            "unplayed": len(unplayed),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": (
                goals_for - goals_against
            ),
            "points": points,
        },
        "data_quality": {
            "status": (
                "COMPLETE"
                if not unplayed
                else "INCOMPLETE"
            ),
            "unplayed_fixtures": unplayed,
        },
    }



def league_table(season):
    if not season:
        raise ValueError(
            "--season is required"
        )

    rows = load_fixtures()
    identity_rows = load_identity_registry()

    name_lookup = {
        (
            row["season"],
            row["local_team_id"],
        ): row["canonical_name"].replace("_", " ")
        for row in identity_rows
    }

    teams = {}

    season_rows = [
        row
        for row in rows
        if row["season"] == season
    ]

    for row in season_rows:

        home_id = str(row["home_team_id"])
        away_id = str(row["away_team_id"])

        if home_id not in teams:
            teams[home_id] = {
                "team_id": home_id,
                "team": name_lookup.get(
                    (
                        season,
                        home_id,
                    ),
                    f"ID {home_id}",
                ),
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0,
                "unplayed": 0,
            }

        if away_id not in teams:
            teams[away_id] = {
                "team_id": away_id,
                "team": name_lookup.get(
                    (
                        season,
                        away_id,
                    ),
                    f"ID {away_id}",
                ),
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0,
                "unplayed": 0,
            }

        home = teams[home_id]
        away = teams[away_id]

        if (
            row["home_score"] == ""
            or row["away_score"] == ""
        ):
            home["unplayed"] += 1
            away["unplayed"] += 1
            continue

        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        home["played"] += 1
        away["played"] += 1

        home["goals_for"] += home_score
        home["goals_against"] += away_score

        away["goals_for"] += away_score
        away["goals_against"] += home_score

        if home_score > away_score:

            home["wins"] += 1
            away["losses"] += 1
            home["points"] += 3

        elif home_score < away_score:

            away["wins"] += 1
            home["losses"] += 1
            away["points"] += 3

        else:

            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    table = []

    for team in teams.values():

        team = dict(team)

        team["goal_difference"] = (
            team["goals_for"]
            - team["goals_against"]
        )

        team["scheduled"] = (
            team["played"]
            + team["unplayed"]
        )

        team["complete"] = (
            team["unplayed"] == 0
        )

        table.append(team)

    table.sort(
        key=lambda team: (
            -team["points"],
            -team["goal_difference"],
            -team["goals_for"],
            team["team"].casefold(),
        )
    )

    for position, team in enumerate(
        table,
        start=1,
    ):
        team["position"] = position

    return {
        "query_type": "league_table",
        "query_version": QUERY_VERSION,
        "season": season,
        "source_file": FIXTURE_FILE,
        "identity_source_file": IDENTITY_FILE,
        "corrections_file": CORRECTIONS_FILE,
        "generated_at":
            datetime.now().astimezone().isoformat(),
        "complete": all(
            team["complete"]
            for team in table
        ),
        "teams": table,
    }



def team_compare(
    team,
    seasons,
):
    if not seasons:
        raise ValueError(
            "At least one season is required."
        )

    requested_seasons = list(
        dict.fromkeys(seasons)
    )

    identity_rows = load_identity_registry()

    requested_candidates = [
        row
        for row in identity_rows
        if (
            row["season"] in requested_seasons
            and (
                normalise_team_name(
                    row.get("canonical_name")
                )
                == normalise_team_name(team)
                or
                normalise_team_name(
                    row.get("source_name")
                )
                == normalise_team_name(team)
            )
            and row["mapping_status"] == "VERIFIED"
        )
    ]

    if not requested_candidates:
        raise ValueError(
            f"No team matching '{team}' "
            f"found in the requested seasons."
        )

    persistent_codes = {
        row["persistent_team_code"]
        for row in requested_candidates
    }

    if len(persistent_codes) != 1:
        raise ValueError(
            "Team comparison could not resolve "
            "a unique persistent club identity."
        )

    persistent_code = next(
        iter(persistent_codes)
    )

    canonical_name = (
        requested_candidates[0][
            "canonical_name"
        ].replace("_", " ")
    )

    participating_seasons = {
        row["season"]
        for row in identity_rows
        if (
            row["persistent_team_code"]
            == persistent_code
            and row["mapping_status"]
            == "VERIFIED"
        )
    }

    summaries = []
    skipped_seasons = []

    for season in requested_seasons:

        if season not in participating_seasons:
            skipped_seasons.append({
                "season": season,
                "status": "NOT_IN_PL",
            })
            continue

        summary = team_summary(
            season=season,
            team=canonical_name,
        )

        summaries.append(summary)

    return {
        "query_type": "team_compare",
        "query_version": QUERY_VERSION,
        "team": canonical_name,
        "persistent_team_code": persistent_code,
        "identity_source_file": IDENTITY_FILE,
        "fixture_source_file": FIXTURE_FILE,
        "corrections_file": CORRECTIONS_FILE,
        "generated_at":
            datetime.now().astimezone().isoformat(),
        "requested_seasons":
            requested_seasons,
        "skipped_seasons":
            skipped_seasons,
        "seasons": [
            {
                "season":
                    summary["season"],
                "team_id":
                    summary["team_id"],
                "played":
                    summary["summary"]["played"],
                "scheduled":
                    summary["summary"][
                        "matches_in_schedule"
                    ],
                "unplayed":
                    summary["summary"]["unplayed"],
                "complete":
                    summary["data_quality"][
                        "status"
                    ] == "COMPLETE",
                "wins":
                    summary["summary"]["wins"],
                "draws":
                    summary["summary"]["draws"],
                "losses":
                    summary["summary"]["losses"],
                "goals_for":
                    summary["summary"]["goals_for"],
                "goals_against":
                    summary["summary"][
                        "goals_against"
                    ],
                "goal_difference":
                    summary["summary"][
                        "goal_difference"
                    ],
                "points":
                    summary["summary"]["points"],
                "unplayed_fixtures":
                    summary["data_quality"][
                        "unplayed_fixtures"
                    ],
            }
            for summary in summaries
        ],
    }



def head_to_head(
    team,
    opponent,
    seasons,
):
    if not seasons:
        raise ValueError(
            "At least one season is required."
        )

    if not team or not opponent:
        raise ValueError(
            "Both team and opponent are required."
        )

    requested_seasons = list(
        dict.fromkeys(seasons)
    )

    matches = []
    skipped_seasons = []

    team_names = {}
    opponent_names = {}

    for season in requested_seasons:

        try:
            resolved_team = resolve_team(
                season,
                team,
            )
            resolved_opponent = resolve_team(
                season,
                opponent,
            )
        except ValueError:
            skipped_seasons.append({
                "season": season,
                "status": "NOT_BOTH_IN_PL",
            })
            continue

        team_names[season] = (
            resolved_team[
                "canonical_name"
            ]
        )

        opponent_names[season] = (
            resolved_opponent[
                "canonical_name"
            ]
        )

        fixture_result = query_fixtures(
            season=season,
            team=resolved_team[
                "canonical_name"
            ],
            opponent=resolved_opponent[
                "canonical_name"
            ],
            limit=100,
        )

        for row in fixture_result["results"]:

            home_score = row[
                "home_score"
            ]
            away_score = row[
                "away_score"
            ]

            if (
                home_score == ""
                or away_score == ""
            ):
                result = "UNPLAYED"
            else:
                home_score = int(
                    home_score
                )
                away_score = int(
                    away_score
                )

                team_is_home = (
                    row["home_team_name"]
                    == resolved_team[
                        "canonical_name"
                    ]
                )

                if (
                    team_is_home
                    and home_score > away_score
                ) or (
                    not team_is_home
                    and away_score > home_score
                ):
                    result = "W"
                elif (
                    home_score == away_score
                ):
                    result = "D"
                else:
                    result = "L"

            matches.append({
                "season":
                    season,
                "fixture_id":
                    row["fixture_id"],
                "gameweek":
                    row["gameweek"],
                "kickoff_time":
                    row["kickoff_time"],
                "home_team_name":
                    row["home_team_name"],
                "away_team_name":
                    row["away_team_name"],
                "home_score":
                    row["home_score"],
                "away_score":
                    row["away_score"],
                "team_result":
                    result,
            })

    matches.sort(
        key=lambda row: (
            row["kickoff_time"],
            row["season"],
            int(row["fixture_id"]),
        )
    )

    wins = sum(
        1
        for row in matches
        if row["team_result"] == "W"
    )

    draws = sum(
        1
        for row in matches
        if row["team_result"] == "D"
    )

    losses = sum(
        1
        for row in matches
        if row["team_result"] == "L"
    )

    goals_for = 0
    goals_against = 0

    for row in matches:

        if (
            row["home_score"] == ""
            or row["away_score"] == ""
        ):
            continue

        home_score = int(
            row["home_score"]
        )
        away_score = int(
            row["away_score"]
        )

        if (
            row["home_team_name"]
            == team_names[row["season"]]
        ):
            goals_for += home_score
            goals_against += away_score
        else:
            goals_for += away_score
            goals_against += home_score

    return {
        "query_type":
            "head_to_head",
        "query_version":
            QUERY_VERSION,
        "team":
            next(
                iter(team_names.values()),
                team,
            ),
        "opponent":
            next(
                iter(opponent_names.values()),
                opponent,
            ),
        "requested_seasons":
            requested_seasons,
        "skipped_seasons":
            skipped_seasons,
        "shared_seasons":
            [
                season
                for season
                in requested_seasons
                if season
                not in {
                    item["season"]
                    for item
                    in skipped_seasons
                }
            ],
        "summary": {
            "matches":
                len(matches),
            "wins":
                wins,
            "draws":
                draws,
            "losses":
                losses,
            "goals_for":
                goals_for,
            "goals_against":
                goals_against,
            "goal_difference":
                goals_for - goals_against,
        },
        "matches":
            matches,
    }


def print_team_summary(
    result,
    explain=False,
):
    summary = result["summary"]

    print()
    print(
        f"{result['team']} ? "
        f"{result['season']}"
    )
    print()

    print(
        f"Record: "
        f"{summary['wins']}W "
        f"{summary['draws']}D "
        f"{summary['losses']}L"
    )

    print(
        f"Goals:  "
        f"{summary['goals_for']}-"
        f"{summary['goals_against']} "
        f"(GD {summary['goal_difference']:+d})"
    )

    print(
        f"Points: "
        f"{summary['points']}"
    )

    print(
        f"Scheduled: "
        f"{summary['matches_in_schedule']}"
    )

    print(
        f"Played:    "
        f"{summary['played']}"
    )

    print(
        f"Unplayed:  "
        f"{summary['unplayed']}"
    )

    unplayed = result.get(
        "data_quality",
        {}
    ).get(
        "unplayed_fixtures",
        []
    )

    if unplayed:
        print()
        print("Data quality")
        print("------------")

        for fixture in unplayed:
            print(
                f"GW {fixture['gameweek']}: "
                f"{fixture['home_team_name']} "
                f"vs {fixture['away_team_name']} "
                f"(fixture {fixture['fixture_id']}) "
                f"? score missing"
            )

    if explain:

        print()
        print("Evidence")
        print("-------")
        print(
            f"Query version: "
            f"{result['query_version']}"
        )
        print(
            f"Fixture source: "
            f"{result['source_file']}"
        )
        print(
            f"Identity source: "
            f"{result['identity_source_file']}"
        )

        if result["identity_resolution"]:

            ident = result[
                "identity_resolution"
            ]

            print(
                f"Persistent club ID: "
                f"{ident['persistent_team_code']}"
            )

            print(
                f"Season-local team ID: "
                f"{ident['local_team_id']}"
            )

            print(
                f"Identity status: "
                f"{ident['mapping_status']}"
            )

        print(
            f"Generated: "
            f"{result['generated_at']}"
        )



def print_team_compare(
    result,
    explain=False,
):
    print()
    print(
        f"{result['team']} "
        f"season comparison"
    )
    print()

    print(
        f"{'Season':<10} "
        f"{'ID':>3} "
        f"{'W':>3} "
        f"{'D':>3} "
        f"{'L':>3} "
        f"{'GF':>4} "
        f"{'GA':>4} "
        f"{'GD':>5} "
        f"{'Pts':>4} "
        f"{'Played':>6} "
        f"{'Status':<10}"
    )

    print("-" * 76)

    for row in result["seasons"]:

        status = (
            "COMPLETE"
            if row["complete"]
            else f"{row['unplayed']} missing"
        )

        print(
            f"{row['season']:<10} "
            f"{row['team_id']:>3} "
            f"{row['wins']:>3} "
            f"{row['draws']:>3} "
            f"{row['losses']:>3} "
            f"{row['goals_for']:>4} "
            f"{row['goals_against']:>4} "
            f"{row['goal_difference']:>+5} "
            f"{row['points']:>4} "
            f"{row['played']:>3}/"
            f"{row['scheduled']:<2} "
            f"{status:<10}"
        )

    if explain:

        print()
        print("Evidence")
        print("-------")

        print(
            f"Persistent club ID: "
            f"{result['persistent_team_code']}"
        )

        print(
            f"Identity source: "
            f"{result['identity_source_file']}"
        )

        print(
            f"Fixture source: "
            f"{result['fixture_source_file']}"
        )

        print(
            f"Corrections source: "
            f"{result['corrections_file']}"
        )

        print(
            f"Query version: "
            f"{result['query_version']}"
        )

        print(
            f"Generated: "
            f"{result['generated_at']}"
        )

        incomplete = [
            row
            for row in result["seasons"]
            if not row["complete"]
        ]

        if incomplete:

            print()
            print("Incomplete seasons")
            print("------------------")

            for row in incomplete:

                print(
                    f"{row['season']}: "
                    f"{row['unplayed']} "
                    f"unplayed fixture(s)"
                )



def print_league_table(
    result,
    explain=False,
):
    print()
    print(
        f"Premier League ? "
        f"{result['season']}"
    )
    print()

    print(
        f"{'Pos':>3} "
        f"{'Team':<30} "
        f"{'P':>3} "
        f"{'W':>3} "
        f"{'D':>3} "
        f"{'L':>3} "
        f"{'GF':>4} "
        f"{'GA':>4} "
        f"{'GD':>5} "
        f"{'Pts':>4}"
    )

    print("-" * 78)

    for team in result["teams"]:

        print(
            f"{team['position']:>3} "
            f"{team['team']:<30} "
            f"{team['played']:>3} "
            f"{team['wins']:>3} "
            f"{team['draws']:>3} "
            f"{team['losses']:>3} "
            f"{team['goals_for']:>4} "
            f"{team['goals_against']:>4} "
            f"{team['goal_difference']:>+5} "
            f"{team['points']:>4}"
        )

    incomplete = [
        team
        for team in result["teams"]
        if not team["complete"]
    ]

    if incomplete:

        print()
        print("Data quality")
        print("------------")

        for team in incomplete:

            print(
                f"{team['team']}: "
                f"{team['unplayed']} "
                f"unplayed fixture(s)"
            )

    if explain:

        print()
        print("Evidence")
        print("-------")
        print(
            f"Fixture source: "
            f"{result['source_file']}"
        )
        print(
            f"Identity source: "
            f"{result['identity_source_file']}"
        )
        print(
            f"Corrections source: "
            f"{result['corrections_file']}"
        )
        print(
            f"Query version: "
            f"{result['query_version']}"
        )
        print(
            f"Table complete: "
            f"{result['complete']}"
        )
        print(
            f"Generated: "
            f"{result['generated_at']}"
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Football Research Laboratory "
            "Query Lab"
        )
    )

    parser.add_argument(
        "--query",
        choices=(
            "top-players",
            "player-total",
            "fixtures",
            "team-summary",
            "team-compare",
            "league-table",
        ),
        default="top-players",
    )

    parser.add_argument(
        "--season"
    )

    parser.add_argument(
        "--seasons",
        nargs="+",
        help=(
            "Multiple seasons for team-comparison queries."
        ),
    )

    parser.add_argument(
        "--metric",
        default="goals",
        choices=sorted(
            METRICS
        )
    )

    parser.add_argument(
        "--player"
    )

    parser.add_argument(
        "--team"
    )

    parser.add_argument(
        "--opponent"
    )

    parser.add_argument(
        "--team-id"
    )

    parser.add_argument(
        "--opponent-id"
    )

    parser.add_argument(
        "--venue",
        choices=(
            "home",
            "away",
        )
    )

    parser.add_argument(
        "--result",
        choices=(
            "W",
            "D",
            "L",
            "UNPLAYED",
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--explain",
        action="store_true",
    )

    parser.add_argument(
        "--json",
        action="store_true",
    )

    parser.add_argument(
        "--list-seasons",
        action="store_true",
    )

    parser.add_argument(
        "--list-metrics",
        action="store_true",
    )

    args = parser.parse_args()

    if args.list_seasons:

        for season in season_files():
            print(season)

        return 0

    if args.list_metrics:

        for metric, column in sorted(
            METRICS.items()
        ):
            print(
                f"{metric}: {column}"
            )

        return 0

    if args.limit < 1:
        parser.error(
            "--limit must be >= 1"
        )

    if args.query in {
        "top-players",
        "player-total",
    } and not args.season:

        parser.error(
            "--season is required"
        )

    if args.query == "player-total" and not args.player:

        parser.error(
            "--player is required "
            "for player-total"
        )

    if args.query == "fixtures":

        if (
            args.team
            and args.team_id
        ):
            parser.error(
                "Use either --team or "
                "--team-id, not both."
            )

        if (
            args.opponent
            and args.opponent_id
        ):
            parser.error(
                "Use either --opponent or "
                "--opponent-id, not both."
            )

        if (
            args.team
            and not args.season
        ):
            parser.error(
                "--season is required "
                "when using --team."
            )

        if (
            args.opponent
            and not args.season
        ):
            parser.error(
                "--season is required "
                "when using --opponent."
            )

    if args.query == "top-players":

        result = top_players(
            args.season,
            args.metric,
            args.limit,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_top_players(
                result,
                args.explain,
            )

        return 0

    if args.query == "player-total":

        result = player_total(
            args.season,
            args.player,
            args.metric,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_player_total(
                result,
                args.explain,
            )

        return 0

    if args.query == "league-table":

        if not args.season:
            parser.error(
                "--season is required"
            )

        result = league_table(
            season=args.season,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_league_table(
                result,
                args.explain,
            )

        return 0

    if args.query == "team-compare":

        if not args.team:
            parser.error(
                "--team is required for "
                "team-compare"
            )

        if not args.seasons:
            parser.error(
                "--seasons is required for "
                "team-compare"
            )

        result = team_compare(
            team=args.team,
            seasons=args.seasons,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_team_compare(
                result,
                args.explain,
            )

        return 0

    if args.query == "team-summary":

        if not args.season:
            parser.error(
                "--season is required"
            )

        if args.team and args.team_id:
            parser.error(
                "Use either --team or --team-id, not both."
            )

        if not args.team and not args.team_id:
            parser.error(
                "Either --team or --team-id is required."
            )

        result = team_summary(
            season=args.season,
            team=args.team,
            team_id=args.team_id,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_team_summary(
                result,
                args.explain,
            )

        return 0

    if args.query == "fixtures":

        result = query_fixtures(
            season=args.season,
            team_id=args.team_id,
            opponent_id=args.opponent_id,
            team=args.team,
            opponent=args.opponent,
            venue=args.venue,
            result=args.result,
            limit=args.limit,
        )

        if args.json:
            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )
        else:
            print_fixtures(
                result,
                args.explain,
            )

        return 0

    raise RuntimeError(
        "Unsupported query"
    )

def test_team_form():
    result = query_lab.team_form(
        season="2024-25",
        team="Liverpool",
    )

    completed = result["matches"]

    assert completed

    assert all(
        row["result"] in {"W", "D", "L"}
        for row in completed
    )

    assert all(
        row["points"] in {0, 1, 3}
        for row in completed
    )

    assert all(
        row["goals_for"] >= 0
        and row["goals_against"] >= 0
        for row in completed
    )

    assert all(
        row["goal_difference"]
        == row["goals_for"]
        - row["goals_against"]
        for row in completed
    )

    assert all(
        completed[i]["kickoff_time"]
        <= completed[i + 1]["kickoff_time"]
        for i in range(len(completed) - 1)
    )

    assert result["windows"]["3"]["matches"] <= 3
    assert result["windows"]["5"]["matches"] <= 5

    assert (
        result["streaks"]["current_win_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_unbeaten_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_loss_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_clean_sheet_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_scoring_streak"]
        <= len(completed)
    )

    assert result["excluded_unplayed"] >= 0



if __name__ == "__main__":

    try:
        raise SystemExit(
            main()
        )

    except Exception as exc:

        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        raise SystemExit(1)
