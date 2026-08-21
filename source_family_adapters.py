"""Common access layer for the FRL's broad Premier League source families.

This module does not replace the existing verified identity bridges or curated
query adapters. It exposes source-native records through one reusable seam so
new variables can be consumed without creating a new bespoke extractor.

Source identity is kept distinct from FRL identity throughout.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from match_stats import PL_ROOT, fixture_source_match
from query_lab import load_identity_registry
from player_match_stats import (
    fixture_player_match_rows,
    source_player_id,
    classify_participation,
)

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def _number(value: object):
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


@lru_cache(maxsize=1)
def _identity_rows() -> tuple[dict, ...]:
    return tuple(load_identity_registry())


@lru_cache(maxsize=1)
def _fixture_rows() -> tuple[dict[str, str], ...]:
    rows, _ = _read_csv(FIXTURE_FILE)
    return tuple(rows)


def canonical_fixture(season: str, fixture_id: str) -> dict[str, str] | None:
    for row in _fixture_rows():
        if row.get("season") == season and str(row.get("fixture_id", "")).strip() == str(fixture_id).strip():
            return dict(row)
    return None


def resolve_source_match(season: str, fixture_id: str) -> dict:
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    resolved = fixture_source_match(fixture, _identity_rows())
    if resolved is None:
        raise ValueError(f"No verified source match for {season}/{fixture_id}")

    match_id, home_row, away_row = resolved
    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": str(match_id),
        "home": dict(home_row),
        "away": dict(away_row),
    }


def fixture_metadata(season: str, fixture_id: str) -> dict:
    """Return source-native fixture metadata without changing canonical identity."""
    resolved = resolve_source_match(season, fixture_id)
    home = resolved["home"]
    away = resolved["away"]

    metadata = {
        "source_match_id": resolved["source_match_id"],
        "ground": home.get("ground") or away.get("ground"),
        "attendance": _number(home.get("attendance") or away.get("attendance")),
        "half_time_home_score": _number(home.get("halfTimeFor")),
        "half_time_away_score": _number(away.get("halfTimeFor")),
        "home_source_result": home.get("result"),
        "away_source_result": away.get("result"),
        "source_kickoff": home.get("kickoff") or away.get("kickoff"),
    }

    # Source consistency is useful evidence even when the UI never renders it.
    metadata["metadata_consistent"] = (
        home.get("ground") in (None, "", away.get("ground"))
        and home.get("attendance") in (None, "", away.get("attendance"))
    )
    return metadata


def team_match_source_rows(season: str, fixture_id: str) -> tuple[dict, dict]:
    """Return the complete native events_stats rows for both fixture sides."""
    resolved = resolve_source_match(season, fixture_id)
    return resolved["home"], resolved["away"]


def team_match_source_fields(season: str) -> tuple[str, ...]:
    fields: set[str] = set()
    root = Path(PL_ROOT)
    expected = f"{season}_events_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "events_stats" / expected
        if not path.is_file():
            continue
        _, columns = _read_csv(path)
        fields.update(columns)
    return tuple(sorted(fields))


def player_match_source_rows(season: str, fixture_id: str) -> tuple[dict, ...]:
    """Return complete native player-match rows for one canonical fixture."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    return tuple(fixture_player_match_rows(fixture))


def player_match_source_fields(season: str) -> tuple[str, ...]:
    fields: set[str] = set()
    root = Path(PL_ROOT)
    expected = f"{season}_players_match_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "players_match_stats" / expected
        if not path.is_file():
            continue
        _, columns = _read_csv(path)
        fields.update(columns)
    return tuple(sorted(fields))


def player_match_records(season: str, fixture_id: str) -> tuple[dict, ...]:
    rows = []
    for row in player_match_source_rows(season, fixture_id):
        item = dict(row)
        item["frl_source_player_id"] = source_player_id(row) or ""
        item["frl_participation_status"] = classify_participation(row)
        rows.append(item)
    return tuple(rows)


def player_season_source_rows(season: str) -> tuple[dict, ...]:
    """Return complete native players_stats rows for one season."""
    records: list[dict] = []
    root = Path(PL_ROOT)
    expected = f"{season}_players_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "players_stats" / expected
        if not path.is_file():
            continue
        rows, _ = _read_csv(path)
        for row in rows:
            item = dict(row)
            item["_source_file"] = str(path)
            records.append(item)
    return tuple(records)


def player_season_source_fields(season: str) -> tuple[str, ...]:
    rows = player_season_source_rows(season)
    fields: set[str] = set()
    for row in rows:
        fields.update(k for k in row if k != "_source_file")
    return tuple(sorted(fields))


def source_field_inventory(season: str) -> dict[str, tuple[str, ...]]:
    """Return a machine-readable field inventory for the three broad families."""
    return {
        "fixture_team_match": team_match_source_fields(season),
        "player_match": player_match_source_fields(season),
        "player_season": player_season_source_fields(season),
    }
