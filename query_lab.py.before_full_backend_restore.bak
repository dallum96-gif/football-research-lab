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
    "own_goals": "own_goals",
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
            f"Matching rows: "
            f"{result['matching_rows']}"
        )
        print(
            f"Generated:     "
            f"{result['generated_at']}"
        )
