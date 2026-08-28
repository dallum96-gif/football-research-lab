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

from match_stats import PL_ROOT, fixture_source_match
from query_lab import load_identity_registry
from player_match_stats import (
    fixture_player_match_rows,
    source_player_id,
    classify_participation,
)
from player_identity_registry import build_registry as build_player_identity_registry
from relationship_enforcement import (
    evaluate_identity,
    require_verified,
    classify_observation,
    decision_dict,
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
def _player_identity_rows() -> tuple[dict[str, str], ...]:
    return tuple(build_player_identity_registry())


@lru_cache(maxsize=1)
def _fixture_rows() -> tuple[dict[str, str], ...]:
    rows, _ = _read_csv(FIXTURE_FILE)
    return tuple(rows)


def canonical_fixture(season: str, fixture_id: str) -> dict[str, str] | None:
    for row in _fixture_rows():
        if row.get("season") == season and str(row.get("fixture_id", "")).strip() == str(fixture_id).strip():
            return dict(row)
    return None


def season_fixtures(season: str) -> tuple[dict[str, str], ...]:
    return tuple(row for row in _fixture_rows() if row.get("season") == season)


def resolve_source_match(season: str, fixture_id: str) -> dict:
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    resolved = fixture_source_match(fixture, _identity_rows())
    if resolved is None:
        raise ValueError(f"No verified source match for {season}/{fixture_id}")

    match_id, home_row, away_row = resolved
    decision = evaluate_identity(
        "canonical_fixture_to_source_match",
        source_context_available=True,
        candidates=({"source_match_id": str(match_id)},),
    )
    require_verified(decision)

    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": str(match_id),
        "home": dict(home_row),
        "away": dict(away_row),
        "relationship_contract": decision.contract,
        "relationship_status": decision.status,
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
    metadata["metadata_consistent"] = (
        home.get("ground") in (None, "", away.get("ground"))
        and home.get("attendance") in (None, "", away.get("attendance"))
    )
    return metadata


def team_match_source_rows(season: str, fixture_id: str) -> tuple[dict, dict]:
    """Return the complete native events_stats rows for both fixture sides."""
    resolved = resolve_source_match(season, fixture_id)
    return resolved["home"], resolved["away"]


def team_match_source_rows_for_season(season: str) -> tuple[dict, ...]:
    """Return source team-match rows reconciled to canonical fixtures."""
    rows: list[dict] = []
    for fixture in season_fixtures(season):
        try:
            home, away = team_match_source_rows(season, fixture["fixture_id"])
        except ValueError:
            continue
        for venue, source_row in (("home", home), ("away", away)):
            item = dict(source_row)
            item["frl_season"] = season
            item["frl_fixture_id"] = str(fixture["fixture_id"])
            item["frl_venue"] = venue
            item["frl_home_team_id"] = fixture.get("home_team_id", "")
            item["frl_away_team_id"] = fixture.get("away_team_id", "")
            rows.append(item)
    return tuple(rows)


@lru_cache(maxsize=16)
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


def player_match_source_rows_for_season(season: str) -> tuple[dict, ...]:
    """Return complete player-match records with canonical fixture context."""
    records: list[dict] = []
    for fixture in season_fixtures(season):
        try:
            rows = player_match_source_rows(season, fixture["fixture_id"])
        except ValueError:
            continue
        for row in rows:
            item = dict(row)
            item["frl_season"] = season
            item["frl_fixture_id"] = str(fixture["fixture_id"])
            item["frl_home_team_id"] = fixture.get("home_team_id", "")
            item["frl_away_team_id"] = fixture.get("away_team_id", "")
            records.append(item)
    return tuple(records)


@lru_cache(maxsize=16)
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
    """Return player-match observations with verified fixture context.

    Player identity is not inferred from the observation itself. Consumers must
    resolve an FRL player identity separately before treating the observation as
    belonging to that identity.
    """
    resolved_fixture = resolve_source_match(season, fixture_id)
    rows = []
    for row in player_match_source_rows(season, fixture_id):
        item = dict(row)
        item["frl_source_player_id"] = source_player_id(row) or ""
        item["frl_participation_status"] = classify_participation(row)
        item["relationship_contract"] = "canonical_fixture_to_source_match"
        item["relationship_status"] = resolved_fixture["relationship_status"]
        rows.append(item)
    return tuple(rows)


@lru_cache(maxsize=16)
def player_season_source_rows(season: str) -> tuple[dict, ...]:
    """Return complete native players_stats rows for one season."""
    records: list[dict] = []
    root = Path(PL_ROOT)
    expected = f"{season}_players_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source root not found: {root}")

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


@lru_cache(maxsize=16)
def player_season_source_fields(season: str) -> tuple[str, ...]:
    rows = player_season_source_rows(season)
    fields: set[str] = set()
    for row in rows:
        fields.update(k for k in row if k != "_source_file")
    return tuple(sorted(fields))


def source_field_inventory(season: str) -> dict[str, tuple[str, ...]]:
    return {
        "fixture_team_match": team_match_source_fields(season),
        "player_match": player_match_source_fields(season),
        "player_season": player_season_source_fields(season),
    }


def resolve_fpl_player_identity(season: str, fpl_element: str) -> dict:
    """Return the verified FPL->FRL player identity decision for one season."""
    matches = [
        row for row in _player_identity_rows()
        if row.get("season") == season
        and str(row.get("fpl_element", "")).strip() == str(fpl_element).strip()
    ]
    decision = evaluate_identity(
        "fpl_player_to_frl_player_identity",
        source_context_available=bool(matches) or bool(_player_identity_rows()),
        candidates=matches,
    )
    if not decision.verified:
        return {
            "season": season,
            "fpl_element": str(fpl_element),
            **decision_dict(decision),
        }
    row = dict(matches[0])
    row.update(decision_dict(decision))
    row["frl_player_source_id"] = row.get("source_player_id", "")
    return row


def source_player_season_identity(season: str, source_player_id_value: str) -> dict:
    """Resolve a source player ID to exactly one player-season row."""
    candidates = [
        row for row in player_season_source_rows(season)
        if str(row.get("playerId", "")).strip() == str(source_player_id_value).strip()
    ]
    decision = evaluate_identity(
        "source_player_identity_to_player_season",
        source_context_available=True,
        candidates=candidates,
    )
    result = {
        "season": season,
        "source_player_id": str(source_player_id_value),
        **decision_dict(decision),
    }
    if decision.verified:
        result["player_season"] = dict(candidates[0])
    return result


def player_match_observation_status(
    season: str,
    fixture_id: str,
    source_player_id_value: str,
    *,
    player_identity_verified: bool = True,
) -> dict:
    """Classify a player-match observation without treating absence as identity failure."""
    resolve_source_match(season, fixture_id)
    rows = [
        row for row in player_match_source_rows(season, fixture_id)
        if str(source_player_id(row) or "").strip() == str(source_player_id_value).strip()
    ]
    status = classify_observation(
        identity_verified=player_identity_verified,
        fixture_verified=True,
        observation_present=bool(rows),
    )
    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_player_id": str(source_player_id_value),
        "relationship_contract": "player_identity_to_player_match_observations",
        "relationship_status": status,
        "observation_present": bool(rows),
    }


