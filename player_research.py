from collections import defaultdict
from functools import lru_cache

import query_lab


SUM_METRICS = {
    "minutes": "minutes",
    "starts": "starts",
    "goals": "goals_scored",
    "assists": "assists",
    "clean_sheets": "clean_sheets",
    "goals_conceded": "goals_conceded",
    "own_goals": "own_goals",
    "penalties_saved": "penalties_saved",
    "penalties_missed": "penalties_missed",
    "yellow_cards": "yellow_cards",
    "red_cards": "red_cards",
    "saves": "saves",
    "bonus": "bonus",
    "bps": "bps",
    "tackles": "tackles",
    "recoveries": "recoveries",
    "defensive_contribution": "defensive_contribution",
    "points": "total_points",
    "xg": "expected_goals",
    "xa": "expected_assists",
    "xgi": "expected_goal_involvements",
}

DERIVED_METRICS = {
    "goals_per_90": "goals",
    "assists_per_90": "assists",
    "xg_per_90": "xg",
    "xa_per_90": "xa",
    "xgi_per_90": "xgi",
    "bps_per_90": "bps",
}

DISPLAY_METRICS = {
    "Minutes": "minutes",
    "Starts": "starts",
    "Goals": "goals",
    "Assists": "assists",
    "Clean sheets": "clean_sheets",
    "Goals conceded": "goals_conceded",
    "Own goals": "own_goals",
    "Penalties saved": "penalties_saved",
    "Penalties missed": "penalties_missed",
    "Yellow cards": "yellow_cards",
    "Red cards": "red_cards",
    "Saves": "saves",
    "Tackles": "tackles",
    "Recoveries": "recoveries",
    "Defensive contribution": "defensive_contribution",
    "BPS": "bps",
    "Bonus": "bonus",
    "FPL points": "points",
    "xG": "xg",
    "xA": "xa",
    "xGI": "xgi",
    "Goals / 90": "goals_per_90",
    "Assists / 90": "assists_per_90",
    "xG / 90": "xg_per_90",
    "xA / 90": "xa_per_90",
    "xGI / 90": "xgi_per_90",
    "BPS / 90": "bps_per_90",
}


def _number(value):
    if value in (None, ""):
        return 0.0
    return float(value)


def canonical_player_name(row):
    name = (
        row.get("name")
        or ""
    ).strip()

    if name:
        return " ".join(
            name.casefold().split()
        )

    first = (
        row.get("first_name")
        or ""
    ).strip()

    second = (
        row.get("second_name")
        or ""
    ).strip()

    return " ".join(
        part.casefold()
        for part in (first, second)
        if part
    )


def display_player_name(row):
    name = (
        row.get("name")
        or ""
    ).strip()

    if name:
        return name

    return " ".join(
        part.strip()
        for part in (
            row.get("first_name", ""),
            row.get("second_name", ""),
        )
        if part
        and part.strip()
    )


def seasonal_player_id(row):
    return str(
        row.get("player_code")
        or row.get("element")
        or row.get("id")
        or ""
    )


def available_seasons():
    return tuple(
        query_lab.season_files().keys()
    )


@lru_cache(maxsize=20)
def _season_slice(
    start_season,
    end_season,
):
    seasons = list(
        available_seasons()
    )

    start_index = seasons.index(
        start_season
    )

    end_index = seasons.index(
        end_season
    )

    if start_index > end_index:
        start_index, end_index = (
            end_index,
            start_index,
        )

    return tuple(
        seasons[
            start_index:end_index + 1
        ]
    )


@lru_cache(maxsize=20)
def _verified_team_names(season):
    rows = query_lab.load_identity_registry()

    return {
        str(row["persistent_team_code"]):
            row["canonical_name"].replace(
                "_",
                " ",
            )
        for row in rows
        if (
            row["season"] == season
            and row["mapping_status"] == "VERIFIED"
        )
    }


def _row_club(row):
    if row.get("team"):
        return str(
            row["team"]
        ).strip()

    team_code = row.get(
        "team_code"
    )

    if team_code:
        return _verified_team_names(
            row["_season"]
        ).get(
            str(team_code),
            str(team_code),
        )

    return ""


@lru_cache(maxsize=20)
def _load_season_rows(season):
    rows, source_file, columns = (
        query_lab.load_player_rows(
            season
        )
    )

    decorated = []

    for row in rows:
        copy = dict(row)
        copy["_season"] = season
        copy["_source_file"] = source_file
        copy["_club"] = _row_club(copy)
        decorated.append(copy)

    return tuple(
        decorated
    )


def _aggregate(
    rows,
    seasons,
):
    first = rows[0]

    player = {
        "player_name":
            display_player_name(first),
        "player_code": seasonal_player_id(first),
        "source_file": first["_source_file"],
        "canonical_name":
            canonical_player_name(first),
        "seasons":
            tuple(
                sorted(
                    {
                        row["_season"]
                        for row in rows
                    },
                    key=lambda value:
                        int(value[:4]),
                )
            ),
        "season_count":
            len(
                {
                    row["_season"]
                    for row in rows
                }
            ),
        "position":
            first.get("position", ""),
        "clubs":
            tuple(
                sorted(
                    {
                        row["_club"]
                        for row in rows
                        if row["_club"]
                    },
                    key=str.casefold,
                )
            ),
        "_records":
            list(rows),
        "_source_files":
            tuple(
                sorted(
                    {
                        row["_source_file"]
                        for row in rows
                    }
                )
            ),
        "_source_rows":
            sum(
                len(
                    _load_season_rows(
                        selected_season
                    )
                )
                for selected_season in seasons
            ),
    }

    for metric, source_column in SUM_METRICS.items():
        player[metric] = sum(
            _number(
                row.get(source_column)
            )
            for row in rows
        )

    minutes = player["minutes"]

    for derived, base in DERIVED_METRICS.items():
        player[derived] = (
            player[base]
            / minutes
            * 90
            if minutes > 0
            else 0.0
        )

    return player


def _candidate_groups(seasons):
    grouped = defaultdict(
        lambda: defaultdict(list)
    )

    for season in seasons:
        for row in _load_season_rows(
            season
        ):
            name = canonical_player_name(row)

            if name:
                grouped[name][season].append(row)

    return grouped


def _is_unambiguous(
    seasonal_rows,
):
    ids = {
        seasonal_player_id(row)
        for row in seasonal_rows
    }

    ids.discard("")

    return (
        len(ids) <= 1
        or len(seasonal_rows) == 0
    )


@lru_cache(maxsize=32)
def season_players(season):
    grouped = _candidate_groups(
        (season,)
    )

    results = []

    for name, seasonal in grouped.items():
        rows = seasonal[season]

        if not _is_unambiguous(rows):
            continue

        results.append(
            _aggregate(
                rows,
                (season,),
            )
        )

    return tuple(results)


@lru_cache(maxsize=32)
def multi_season_players(
    start_season,
    end_season,
):
    seasons = _season_slice(
        start_season,
        end_season,
    )

    grouped = _candidate_groups(
        seasons
    )

    results = []

    for name, seasonal in grouped.items():
        combined = []

        valid = True

        for season in seasons:
            rows = seasonal.get(
                season,
                [],
            )

            if not rows:
                continue

            if not _is_unambiguous(
                rows
            ):
                valid = False
                break

            combined.extend(rows)

        if not valid or not combined:
            continue

        results.append(
            _aggregate(
                combined,
                seasons,
            )
        )

    return tuple(results)


def filter_players(
    players,
    position=None,
    team=None,
    min_minutes=0,
    min_seasons=0,
    filters=None,
):
    results = []

    for player in players:
        if (
            position
            and player["position"]
            != position
        ):
            continue

        if (
            team
            and team not in player["clubs"]
        ):
            continue

        if (
            player["minutes"]
            < min_minutes
        ):
            continue

        if (
            player["season_count"]
            < min_seasons
        ):
            continue

        matches = True

        for metric, operator, target in (
            filters or []
        ):
            value = player.get(
                metric
            )

            if value is None:
                matches = False
                break

            if operator == "At least":
                ok = value >= target
            elif operator == "At most":
                ok = value <= target
            elif operator == "Greater than":
                ok = value > target
            elif operator == "Less than":
                ok = value < target
            elif operator == "Equals":
                ok = value == target
            else:
                raise ValueError(
                    f"Unknown operator: {operator}"
                )

            if not ok:
                matches = False
                break

        if matches:
            results.append(player)

    return results
