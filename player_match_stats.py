"""Player-match source adapter for the Football Research Laboratory.

This module is deliberately additive. It does not replace the canonical FPL
player dataset or fixture master. It reuses the existing verified fixture/team
identity mechanism from match_stats.py and exposes the external
players_match_stats source as a separate evidence layer.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from match_stats import fixture_source_match
from query_lab import load_identity_registry


PL_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")


# Source fields audited on 16 August 2026. Only fields actually present in the
# source are included here. Coverage varies by season and is exposed explicitly
# rather than silently converting absent fields to zero.
PLAYER_MATCH_METRICS = {
    "passes": {
        "source": "totalPass",
        "kind": "sum",
        "label": "Passes",
    },
    "accurate_passes": {
        "source": "accuratePass",
        "kind": "sum",
        "label": "Accurate passes",
    },
    "own_half_accurate_passes": {
        "source": "accurateOwnHalfPasses",
        "kind": "sum",
        "label": "Accurate passes in own half",
    },
    "opposition_half_accurate_passes": {
        "source": "accurateOppositionHalfPasses",
        "kind": "sum",
        "label": "Accurate passes in opposition half",
    },
    "long_balls": {
        "source": "totalLongBalls",
        "kind": "sum",
        "label": "Long balls",
    },
    "accurate_long_balls": {
        "source": "accurateLongBalls",
        "kind": "sum",
        "label": "Accurate long balls",
    },
    "key_passes": {
        "source": "keyPass",
        "kind": "sum",
        "label": "Key passes",
    },
    "big_chances_created": {
        "source": "bigChanceCreated",
        "kind": "sum",
        "label": "Big chances created",
    },
    "assists": {
        "source": "goalAssist",
        "kind": "sum",
        "label": "Assists",
    },
    "expected_assists": {
        "source": "expectedAssists",
        "kind": "sum",
        "label": "Expected assists",
    },
    "successful_dribbles": {
        "source": "successfulDribbles",
        "kind": "sum",
        "label": "Successful dribbles",
    },
    "unsuccessful_dribbles": {
        "source": "unsuccessfulDribbles",
        "kind": "sum",
        "label": "Unsuccessful dribbles",
    },
    "ball_carries": {
        "source": "ballCarriesCount",
        "kind": "sum",
        "label": "Ball carries",
    },
    "progressive_ball_carries": {
        "source": "progressiveBallCarriesCount",
        "kind": "sum",
        "label": "Progressive ball carries",
    },
    "progressive_carry_distance": {
        "source": "totalProgressiveBallCarriesDistance",
        "kind": "sum",
        "label": "Progressive carry distance",
    },
    "progression": {
        "source": "totalProgression",
        "kind": "sum",
        "label": "Total progression",
    },
}


# These are the first fields suitable for a stable Player Research passing
# contract. Crosses are intentionally not promoted yet, per current product
# direction. Creativity/ICT remain in the existing FPL layer.
PASSING_METRICS = (
    "passes",
    "accurate_passes",
    "own_half_accurate_passes",
    "opposition_half_accurate_passes",
    "long_balls",
    "accurate_long_balls",
    "key_passes",
    "big_chances_created",
    "expected_assists",
)


@lru_cache(maxsize=1)
def _identity_rows():
    return tuple(load_identity_registry())


def _open_csv(path: Path):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            handle = path.open("r", encoding=encoding, newline="")
            reader = csv.DictReader(handle)
            _ = reader.fieldnames
            return handle, reader
        except UnicodeDecodeError as exc:
            last_error = exc
            try:
                handle.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode CSV: {path}") from last_error


@lru_cache(maxsize=20)
def _season_player_match_files(season: str) -> tuple[Path, ...]:
    if not PL_ROOT.is_dir():
        raise FileNotFoundError(f"Player-match source root not found: {PL_ROOT}")

    expected = f"{season}_players_match_stats.csv"
    return tuple(sorted(PL_ROOT.rglob(expected)))


def available_seasons() -> tuple[str, ...]:
    seasons = []
    for path in PL_ROOT.rglob("*_players_match_stats.csv"):
        if path.name.endswith("_players_match_stats.csv"):
            seasons.append(path.name.replace("_players_match_stats.csv", ""))
    return tuple(sorted(set(seasons)))


@lru_cache(maxsize=20)
def source_fields(season: str) -> tuple[str, ...]:
    files = _season_player_match_files(season)
    if not files:
        return tuple()

    fields = set()
    for path in files:
        handle, reader = _open_csv(path)
        fields.update(reader.fieldnames or [])
        handle.close()
    return tuple(sorted(fields))


def available_metrics(season: str | None = None) -> tuple[str, ...]:
    if season is None:
        return tuple(PLAYER_MATCH_METRICS)

    fields = set(source_fields(season))
    return tuple(
        key
        for key, spec in PLAYER_MATCH_METRICS.items()
        if spec["source"] in fields
    )


def metric_coverage() -> dict[str, tuple[str, ...]]:
    return {
        season: available_metrics(season)
        for season in available_seasons()
    }


@lru_cache(maxsize=20)
def _source_match_records(season: str) -> tuple[dict, ...]:
    """Load raw player-match records for one season.

    This is a cached source layer only; no aggregation or identity rewriting
    happens here.
    """
    records: list[dict] = []
    for path in _season_player_match_files(season):
        handle, reader = _open_csv(path)
        for row in reader:
            copy = dict(row)
            copy["_source_file"] = str(path)
            records.append(copy)
        handle.close()
    return tuple(records)


def _number(value):
    if value in (None, ""):
        return 0.0
    return float(value)


def _source_team_ids_for_fixture(fixture: dict) -> tuple[str, str]:
    resolved = fixture_source_match(fixture, _identity_rows())
    if resolved is None:
        raise ValueError(
            f"No verified upstream fixture match for "
            f"{fixture['season']}/{fixture['fixture_id']}"
        )

    _, home_row, away_row = resolved
    return (
        str(home_row.get("team_id", "")).strip(),
        str(away_row.get("team_id", "")).strip(),
    )


def player_match_id_for_fixture(fixture: dict) -> str | None:
    """Resolve a canonical fixture to its player-match source matchId.

    Gameweek is intentionally not part of the identity key because postponed
    and rescheduled fixtures can carry a different source gameweek. The trusted
    fixture resolver supplies the verified source home/away team IDs.
    """
    season = fixture["season"]
    home_team, away_team = _source_team_ids_for_fixture(fixture)

    candidates: set[str] = set()

    for row in _source_match_records(season):
        venue = str(row.get("venue", "")).strip().lower()
        team_id = str(row.get("team_id", "")).strip()
        match_id = str(row.get("matchId", "")).strip()

        if not match_id:
            continue

        if venue == "home" and team_id == home_team:
            candidates.add(f"home:{match_id}")
        elif venue == "away" and team_id == away_team:
            candidates.add(f"away:{match_id}")

    home_matches = {
        value.split(":", 1)[1]
        for value in candidates
        if value.startswith("home:")
    }
    away_matches = {
        value.split(":", 1)[1]
        for value in candidates
        if value.startswith("away:")
    }

    matches = home_matches & away_matches

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous player-match source for "
            f"{season}/{fixture['fixture_id']}: {sorted(matches)}"
        )

    return next(iter(matches)) if matches else None


def fixture_player_match_rows(fixture: dict) -> tuple[dict, ...]:
    """Return the raw player-match rows attached to a canonical fixture."""
    match_id = player_match_id_for_fixture(fixture)
    if match_id is None:
        return tuple()

    season = fixture["season"]
    return tuple(
        row
        for row in _source_match_records(season)
        if str(row.get("matchId", "")).strip() == match_id
    )


def aggregate_player(
    fixture_rows: Iterable[dict],
) -> dict[str, float | None]:
    """Aggregate audited source metrics across player-match rows.

    Missing source fields remain None. Present additive statistics are summed.
    """
    rows = tuple(fixture_rows)
    result: dict[str, float | None] = {}

    for metric, spec in PLAYER_MATCH_METRICS.items():
        source = spec["source"]
        if not any(row.get(source) not in (None, "") for row in rows):
            result[metric] = None
            continue

        result[metric] = sum(
            _number(row.get(source))
            for row in rows
        )

    passes = result["passes"]
    accurate = result["accurate_passes"]
    result["pass_accuracy"] = (
        accurate / passes * 100.0
        if passes not in (None, 0)
        and accurate is not None
        else None
    )

    return result


def player_season_totals(
    season: str,
) -> dict[str, dict[str, float | None]]:
    """Aggregate player-match evidence for all players in one season."""
    grouped: dict[str, list[dict]] = defaultdict(list)

    for row in _source_match_records(season):
        player_id = str(
            row.get("playerId")
            or row.get("pl_code")
            or ""
        ).strip()
        if player_id:
            grouped[player_id].append(row)

    return {
        player_id: aggregate_player(rows)
        for player_id, rows in grouped.items()
    }
