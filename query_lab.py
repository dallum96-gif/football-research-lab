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
    "own_goals": "own_goals",
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
        "results": [
            {
                "rank": rank,
                "player": names[key],
                "player_key": key,
                "value": value,
            }
            for rank, (key, value)
            in enumerate(
                ranked,
                start=1
            )
        ],
        "source_file": path,
        "source_rows": len(rows),
    }


def top_player_records(season, metric="goals", limit=10):
    rows, path, columns = load_player_rows(season)
    source_column = METRICS[metric]

    if source_column not in columns:
        raise ValueError(
            f"Column '{source_column}' is not present in {season}"
        )

    totals = {}
    names = {}
    teams = {}

    for row in rows:
        key = player_key(row)
        totals[key] = totals.get(key, 0.0) + to_number(row.get(source_column))
        names[key] = display_name(row)
        teams[key] = row.get("team_name") or row.get("team") or ""

    ranked = sorted(
        totals.items(),
        key=lambda item: (-item[1], names[item[0]].lower())
    )[:limit]

    return {
        "query_type": "top_player_records",
        "query_version": QUERY_VERSION,
        "season": season,
        "metric": metric,
        "results": [
            {
                "rank": rank,
                "player": names[key],
                "player_key": key,
                "team": teams[key],
                "value": value,
            }
            for rank, (key, value) in enumerate(ranked, start=1)
        ],
        "source_file": path,
        "source_rows": len(rows),
    }


def player_total(season, player, metric="goals"):
    rows, path, columns = load_player_rows(season)
    source_column = METRICS[metric]

    if source_column not in columns:
        raise ValueError(
            f"Column '{source_column}' is not present in {season}"
        )

    needle = str(player).strip().casefold()
    matched = []
    for row in rows:
        name = display_name(row)
        key = player_key(row)
        if needle in name.casefold() or needle == str(key).casefold():
            matched.append(row)

    if not matched:
        raise ValueError(f"No player matching '{player}' found in {season}.")

    value = sum(to_number(row.get(source_column)) for row in matched)
    return {
        "query_type": "player_total",
        "query_version": QUERY_VERSION,
        "season": season,
        "metric": metric,
        "player": display_name(matched[0]),
        "value": value,
        "source_file": path,
        "source_rows": len(matched),
    }


def _fixture_result(team_id, home_id, away_id, home_score, away_score):
    if home_score in (None, "") or away_score in (None, ""):
        return "UNPLAYED"

    home_score = int(home_score)
    away_score = int(away_score)

    if team_id == home_id:
        return "W" if home_score > away_score else "D" if home_score == away_score else "L"

    return "W" if away_score > home_score else "D" if away_score == home_score else "L"


def league_table(season):
    by_local_id, _, _ = _team_lookup(season)
    fixtures = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]

    stats = {
        local_id: {
            "team_id": local_id,
            "persistent_team_code": record["persistent_team_code"],
            "team": record["team"],
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
        }
        for local_id, record in by_local_id.items()
    }

    for row in fixtures:
        home_id = str(row.get("home_team_id", "")).strip()
        away_id = str(row.get("away_team_id", "")).strip()

        if home_id not in stats or away_id not in stats:
            raise ValueError(
                f"Fixture identity missing for {season}: "
                f"{home_id} vs {away_id} (fixture {row.get('fixture_id')})."
            )

        if row.get("home_score") in (None, "") or row.get("away_score") in (None, ""):
            continue

        home_score = int(row["home_score"])
        away_score = int(row["away_score"])
        home = stats[home_id]
        away = stats[away_id]

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
        elif away_score > home_score:
            away["wins"] += 1
            home["losses"] += 1
            away["points"] += 3
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    rows = []
    for item in stats.values():
        item["goal_difference"] = item["goals_for"] - item["goals_against"]
        rows.append(item)

    rows.sort(
        key=lambda item: (
            -item["points"],
            -item["goal_difference"],
            -item["goals_for"],
            item["team"].casefold(),
        )
    )

    for position, item in enumerate(rows, start=1):
        item["position"] = position

    return {
        "query_type": "league_table",
        "query_version": QUERY_VERSION,
        "season": season,
        "source_file": str(FIXTURE_FILE),
        "source_rows": len(fixtures),
        "teams": rows,
    }


def fixtures(
    season=None,
    team=None,
    opponent=None,
    venue=None,
    result=None,
    limit=100,
):
    if not season:
        raise ValueError("Season is required for fixture queries.")

    by_local_id, _, _ = _team_lookup(season)
    team_id = _resolve_team_id(season, team)
    opponent_id = _resolve_team_id(season, opponent)

    rows = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]
    results = []

    for row in rows:
        home_id = str(row.get("home_team_id", "")).strip()
        away_id = str(row.get("away_team_id", "")).strip()

        if home_id not in by_local_id or away_id not in by_local_id:
            raise ValueError(
                f"Fixture identity missing for {season}: "
                f"{home_id} vs {away_id} (fixture {row.get('fixture_id')})."
            )

        if team_id and team_id not in (home_id, away_id):
            continue
        if opponent_id and opponent_id not in (home_id, away_id):
            continue
        if opponent_id and team_id and opponent_id == team_id:
            continue

        current_venue = None
        if team_id:
            current_venue = "home" if home_id == team_id else "away"
            if venue and venue != current_venue:
                continue

        current_result = (
            _fixture_result(
                team_id,
                home_id,
                away_id,
                row.get("home_score"),
                row.get("away_score"),
            )
            if team_id
            else None
        )

        if result and current_result != result:
            continue

        output = dict(row)
        output["home_team_name"] = by_local_id[home_id]["team"]
        output["away_team_name"] = by_local_id[away_id]["team"]
        results.append(output)

    results.sort(
        key=lambda item: (
            str(item.get("kickoff_time", "")),
            int(item.get("fixture_id", 0)),
        )
    )

    return {
        "query_type": "fixtures",
        "query_version": QUERY_VERSION,
        "season": season,
        "filters": {
            "team_id": team_id,
            "opponent_id": opponent_id,
            "venue": venue,
            "result": result,
        },
        "total_matches": len(results),
        "results": results[:limit],
        "source_file": str(FIXTURE_FILE),
    }


def team_summary(season, team):
    return query_lab.team_summary(season=season, team=team)


def team_compare(team, seasons):
    return query_lab.team_compare(team=team, seasons=seasons)


def head_to_head(team, opponent, seasons):
    return query_lab.head_to_head(team=team, opponent=opponent, seasons=seasons)


def team_form(season, team=None, team_id=None):
    return query_lab.team_form(season=season, team=team, team_id=team_id)


def top_players(season, metric="goals", limit=10):
    return query_lab.top_players(season=season, metric=metric, limit=limit)


def player_total(season, player, metric="goals"):
    return query_lab.player_total(season=season, player_search=player, metric=metric)


def fixture_detail(season, fixture_id):
    return query_lab.fixture_detail(season=season, fixture_id=fixture_id)


def list_seasons():
    rows = query_lab.load_identity_registry()
    return sorted({row["season"] for row in rows})


def list_metrics():
    return dict(query_lab.METRICS)


def dispatch(query, **kwargs):
    queries = {
        "league-table": league_table,
        "team-summary": team_summary,
        "team-compare": team_compare,
        "fixtures": fixtures,
        "head-to-head": head_to_head,
        "team-form": team_form,
        "top-players": top_players,
        "player-total": player_total,
    }

    if query not in queries:
        raise ValueError(
            f"Unknown query '{query}'. Available: {', '.join(sorted(queries))}"
        )

    return queries[query](**kwargs)


def main():
    import json
    payload = json.loads(sys.stdin.read())
    query = payload.get("query")
    if not query:
        raise ValueError("Request must contain 'query'.")
    result = dispatch(query, **payload.get("params", {}))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, indent=2))
        raise SystemExit(1)