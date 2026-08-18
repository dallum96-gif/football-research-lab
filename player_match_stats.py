"""Additive adapter for the external player-match evidence source.

The canonical FPL player dataset and fixture master remain authoritative.
This module reuses the existing verified fixture/team identity mechanism and
adds player-match evidence without rewriting established research contracts.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from frl_data_paths import player_match_root
from match_stats import fixture_source_match
from query_lab import load_identity_registry


PL_ROOT = player_match_root()


# Source fields audited on 16 August 2026. Coverage is seasonal and absent
# fields remain unavailable rather than being coerced to zero.
PLAYER_MATCH_METRICS = {
    "passes": {"source": "totalPass", "kind": "sum", "label": "Passes"},
    "accurate_passes": {"source": "accuratePass", "kind": "sum", "label": "Accurate passes"},
    "own_half_accurate_passes": {"source": "accurateOwnHalfPasses", "kind": "sum", "label": "Accurate passes in own half"},
    "opposition_half_accurate_passes": {"source": "accurateOppositionHalfPasses", "kind": "sum", "label": "Accurate passes in opposition half"},
    "long_balls": {"source": "totalLongBalls", "kind": "sum", "label": "Long balls"},
    "accurate_long_balls": {"source": "accurateLongBalls", "kind": "sum", "label": "Accurate long balls"},
    "key_passes": {"source": "keyPass", "kind": "sum", "label": "Key passes"},
    "big_chances_created": {"source": "bigChanceCreated", "kind": "sum", "label": "Big chances created"},
    "assists": {"source": "goalAssist", "kind": "sum", "label": "Assists"},
    "expected_assists": {"source": "expectedAssists", "kind": "sum", "label": "Expected assists"},
    "successful_dribbles": {"source": "successfulDribbles", "kind": "sum", "label": "Successful dribbles"},
    "unsuccessful_dribbles": {"source": "unsuccessfulDribbles", "kind": "sum", "label": "Unsuccessful dribbles"},
    "ball_carries": {"source": "ballCarriesCount", "kind": "sum", "label": "Ball carries"},
    "progressive_ball_carries": {"source": "progressiveBallCarriesCount", "kind": "sum", "label": "Progressive ball carries"},
    "progressive_carry_distance": {"source": "totalProgressiveBallCarriesDistance", "kind": "sum", "label": "Progressive carry distance"},
    "progression": {"source": "totalProgression", "kind": "sum", "label": "Total progression"},
}

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
        return tuple()
    expected = f"{season}_players_match_stats.csv"
    return tuple(sorted(PL_ROOT.rglob(expected)))


def available_seasons() -> tuple[str, ...]:
    if not PL_ROOT.is_dir():
        return tuple()
    seasons = [
        path.name.replace("_players_match_stats.csv", "")
        for path in PL_ROOT.rglob("*_players_match_stats.csv")
    ]
    return tuple(sorted(set(seasons)))


@lru_cache(maxsize=20)
def source_fields(season: str) -> tuple[str, ...]:
    fields = set()
    for path in _season_player_match_files(season):
        handle, reader = _open_csv(path)
        fields.update(reader.fieldnames or [])
        handle.close()
    return tuple(sorted(fields))


def available_metrics(season: str | None = None) -> tuple[str, ...]:
    fields = None if season is None else set(source_fields(season))
    return tuple(
        key
        for key, spec in PLAYER_MATCH_METRICS.items()
        if fields is None or spec["source"] in fields
    )


def metric_coverage() -> dict[str, tuple[str, ...]]:
    return {season: available_metrics(season) for season in available_seasons()}


@lru_cache(maxsize=20)
def _source_match_records(season: str) -> tuple[dict, ...]:
    records: list[dict] = []
    for path in _season_player_match_files(season):
        handle, reader = _open_csv(path)
        for row in reader:
            copy = dict(row)
            copy["_source_file"] = str(path)
            records.append(copy)
        handle.close()
    return tuple(records)


@lru_cache(maxsize=20)
def _player_match_pair_index(season: str) -> dict[tuple[str, str], tuple[str, ...]]:
    """Index one season by source home/away team IDs.

    Gameweek is deliberately excluded because postponed/rescheduled fixtures
    can be assigned a different gameweek in the source player-match files.
    """
    home_by_match: dict[str, set[str]] = defaultdict(set)
    away_by_match: dict[str, set[str]] = defaultdict(set)

    for row in _source_match_records(season):
        match_id = str(row.get("matchId", "")).strip()
        team_id = str(row.get("team_id", "")).strip()
        venue = str(row.get("venue", "")).strip().lower()

        if not match_id or not team_id:
            continue

        if venue == "home":
            home_by_match[match_id].add(team_id)
        elif venue == "away":
            away_by_match[match_id].add(team_id)

    index: dict[tuple[str, str], list[str]] = defaultdict(list)

    for match_id in set(home_by_match) & set(away_by_match):
        for home_id in home_by_match[match_id]:
            for away_id in away_by_match[match_id]:
                index[(home_id, away_id)].append(match_id)

    return {
        key: tuple(sorted(values))
        for key, values in index.items()
    }


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
    """Resolve canonical fixture to external player-match ``matchId``."""
    season = fixture["season"]
    home_team, away_team = _source_team_ids_for_fixture(fixture)
    matches = _player_match_pair_index(season).get((home_team, away_team), ())

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous player-match source for "
            f"{season}/{fixture['fixture_id']}: {list(matches)}"
        )

    return matches[0] if matches else None


def fixture_player_match_rows(fixture: dict) -> tuple[dict, ...]:
    """Return raw player-match rows attached to a canonical fixture."""
    match_id = player_match_id_for_fixture(fixture)
    if match_id is None:
        return tuple()

    return tuple(
        row
        for row in _source_match_records(fixture["season"])
        if str(row.get("matchId", "")).strip() == match_id
    )


def aggregate_rows(rows: Iterable[dict]) -> dict[str, float | None]:
    """Aggregate additive source metrics and derive pass accuracy."""
    records = tuple(rows)
    result: dict[str, float | None] = {}

    for metric, spec in PLAYER_MATCH_METRICS.items():
        source = spec["source"]
        if not any(row.get(source) not in (None, "") for row in records):
            result[metric] = None
            continue
        result[metric] = sum(_number(row.get(source)) for row in records)

    passes = result["passes"]
    accurate = result["accurate_passes"]
    result["pass_accuracy"] = (
        accurate / passes * 100.0
        if passes not in (None, 0) and accurate is not None
        else None
    )
    return result


def player_season_totals(season: str) -> dict[str, dict[str, float | None]]:
    """Aggregate player-match evidence for every player in one season."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in _source_match_records(season):
        player_id = str(row.get("playerId") or row.get("pl_code") or "").strip()
        if player_id:
            grouped[player_id].append(row)
    return {player_id: aggregate_rows(rows) for player_id, rows in grouped.items()}



def player_match_records_for_player(player_id: str, season: str) -> tuple[dict, ...]:
    """Return source rows for one player in one season."""
    key = str(player_id).strip()
    return tuple(
        row
        for row in _source_match_records(season)
        if str(row.get("playerId") or row.get("pl_code") or "").strip() == key
    )


def player_season_total(player_id: str, season: str) -> dict[str, float | None]:
    """Return audited source totals for one player/season."""
    return aggregate_rows(player_match_records_for_player(player_id, season))


def _number(value):
    if value in (None, ""):
        return 0.0
    return float(value)
