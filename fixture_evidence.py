"""Universal fixture-level evidence seam.

The module composes already-governed FRL relationships rather than creating a
second identity system. Events remain event-grain observations; lineup rows
remain player-fixture observations. Unsupported evidence stays unavailable.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from relationship_contracts import get_relationship_contract
from source_family_adapters import (
    canonical_fixture,
    player_match_observation_status,
    player_match_source_fields,
    player_match_source_rows,
    resolve_source_match,
    source_player_season_identity,
)

ROOT = Path(__file__).resolve().parent
GOAL_OUTPUT = ROOT / "data" / "fixture_goal_events.csv"
GOAL_STAGED = (
    ROOT.parent
    / "Premier-League-Stats"
    / "fpl_scraper"
    / "fpl_stats"
    / "data"
    / "raw"
    / "fixture_goal_events_pulselive.staged.csv"
)

GOAL_FIELDS = {
    "season",
    "fixture_id",
    "source_match_id",
    "source_event_id",
    "source_event_type",
    "source_event_seconds",
    "source_event_time_label",
    "source_scorer_name",
}


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    if not path.is_file():
        return ()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return tuple(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


@lru_cache(maxsize=1)
def _goal_source() -> Path | None:
    if GOAL_OUTPUT.is_file():
        return GOAL_OUTPUT
    if GOAL_STAGED.is_file():
        return GOAL_STAGED
    return None


@lru_cache(maxsize=1)
def _goal_rows() -> tuple[dict[str, str], ...]:
    path = _goal_source()
    if path is None:
        return ()
    rows = _read_csv(path)
    if not rows:
        return ()
    missing = sorted(GOAL_FIELDS - set(rows[0]))
    if missing:
        raise ValueError(f"Goal event source missing required fields: {missing}")
    return rows


def _n(value: object) -> str:
    return str(value or "").strip()


def _number(value: object):
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _source_event_team(row: dict) -> str:
    return _n(row.get("source_scorer_team_resolved") or row.get("source_scorer_team"))


def _fixture_side(fixture: dict[str, str], source_team: str) -> str | None:
    target = _n(source_team).casefold()
    if not target:
        return None
    resolved = resolve_source_match(fixture["season"], fixture["fixture_id"])
    for side, key in (("home", "home"), ("away", "away")):
        team = _n(resolved[key].get("team")).casefold()
        if target == team:
            return side
    return None


def _player_identity_status(season: str, source_player_id: str | None) -> str:
    if not source_player_id:
        return "UNAVAILABLE"
    try:
        decision = source_player_season_identity(season, source_player_id)
    except (FileNotFoundError, ValueError):
        return "UNRESOLVED"
    return "VERIFIED" if decision.get("verified") else _n(decision.get("status")) or "UNRESOLVED"


def fixture_events(season: str, fixture_id: str) -> dict:
    """Return validated event-level observations for one canonical fixture."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    contract = get_relationship_contract("canonical_fixture_to_source_match")
    source_match_id = _n(source_match["source_match_id"])

    source_rows = [
        row for row in _goal_rows()
        if _n(row.get("season")) == season and _n(row.get("fixture_id")) == str(fixture_id)
    ]
    mismatched = [row for row in source_rows if _n(row.get("source_match_id")) != source_match_id]
    if mismatched:
        raise ValueError(
            f"Event/source-match contradiction for {season}/{fixture_id}: "
            f"expected {source_match_id}, found {sorted({_n(r.get('source_match_id')) for r in mismatched})}"
        )

    events = []
    for row in source_rows:
        source_player_id = _n(row.get("source_scorer_id")) or None
        events.append({
            "event_id": _n(row.get("source_event_id")),
            "minute": _n(row.get("source_event_time_label")) or None,
            "seconds": _number(row.get("source_event_seconds")),
            "type": _n(row.get("source_event_type")).casefold() or None,
            "side": _fixture_side(fixture, _source_event_team(row)),
            "primary_player": {
                "source_player_id": source_player_id,
                "name": _n(row.get("source_scorer_name")) or None,
                "identity_status": _player_identity_status(season, source_player_id),
            },
            "assist": None,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_family": "fixture_event",
                "source_match_id": source_match_id,
                "source_event_id": _n(row.get("source_event_id")),
                "source_fields": [key for key in row if key.startswith("source_")],
                "relationship_contract": contract.name,
                "relationship_status": source_match["relationship_status"],
                "transformation": "validated goal-event source attachment",
            },
        })

    events.sort(key=lambda item: (item["seconds"] is None, item["seconds"] or 0, item["event_id"]))
    event_types = sorted({item["type"] for item in events if item["type"]})
    status = "AVAILABLE" if events else "UNAVAILABLE"
    limitations = []
    if not _goal_rows():
        limitations.append("No validated event-level dataset is materialized in the runtime environment.")
    else:
        limitations.append("Validated reusable event evidence currently covers goals; cards, substitutions and other event types are not promoted without independently verified event-level provenance.")

    return {
        "query_type": "fixture_events",
        "status": status,
        "season": season,
        "fixture_id": str(fixture_id),
        "grain": "event",
        "events": events,
        "coverage": {
            "event_types": event_types,
            "event_count": len(events),
            "goal_events": sum(item["type"] == "goal" for item in events),
            "card_events": sum(item["type"] in {"yellow", "red", "card"} for item in events),
            "substitution_events": sum(item["type"] in {"substitution", "substitution_in", "substitution_out"} for item in events),
        },
        "provenance": {
            "source_family": "fixture_event",
            "source_match_id": source_match_id,
            "source_path": str(_goal_source()) if _goal_source() else None,
            "relationship_contract": contract.name,
            "relationship_status": source_match["relationship_status"],
        },
        "limitations": limitations,
    }


def _participation(row: dict) -> str:
    substitute = _n(row.get("substitute")).casefold()
    minutes = _number(row.get("minutesPlayed"))
    minutes = 0 if minutes is None else float(minutes)
    is_sub = substitute in {"true", "1", "yes"}
    if not is_sub and minutes > 0:
        return "starting"
    if is_sub and minutes > 0:
        return "sub_in"
    if is_sub and minutes == 0:
        return "bench"
    return "unknown"


def fixture_lineup(season: str, fixture_id: str) -> dict:
    """Return player-fixture participation evidence using existing Player-Match access."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    relationship = get_relationship_contract("player_identity_to_player_match_observations")

    try:
        rows = player_match_source_rows(season, fixture_id)
        fields = set(player_match_source_fields(season))
    except FileNotFoundError:
        return {
            "query_type": "fixture_lineup",
            "status": "UNAVAILABLE",
            "season": season,
            "fixture_id": str(fixture_id),
            "grain": "player_fixture",
            "lineup": [],
            "coverage": {"player_rows": 0, "starting_rows": 0, "bench_rows": 0, "sub_in_rows": 0, "identity_failures": 0},
            "formation": {"home": {"status": "UNAVAILABLE", "value": None}, "away": {"status": "UNAVAILABLE", "value": None}},
            "tactical_placement": {"status": "UNAVAILABLE"},
            "provenance": {"source_match_id": _n(source_match["source_match_id"]), "source_family": "player_match"},
            "limitations": ["Player-Match source data is not materialized in the runtime environment."],
        }

    lineup = []
    identity_failures = []
    for row in rows:
        source_id = _n(row.get("playerId")) or None
        if not source_id:
            identity_failures.append("MISSING_SOURCE_PLAYER_ID")
            continue
        identity = source_player_season_identity(season, source_id)
        verified = bool(identity.get("verified"))
        observation = player_match_observation_status(
            season, fixture_id, source_id, player_identity_verified=verified
        )
        if not verified:
            identity_failures.append(source_id)

        venue = _n(row.get("venue")).casefold()
        side = "home" if venue == "home" else "away" if venue == "away" else None
        lineup.append({
            "player": {
                "source_player_id": source_id,
                "name": _n(row.get("playerName")) or None,
                "identity_status": "VERIFIED" if verified else _n(identity.get("status")) or "UNRESOLVED",
            },
            "side": side,
            "participation": _participation(row),
            "position": _n(row.get("position")) or None,
            "minutes": _number(row.get("minutesPlayed")),
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_family": "player_match",
                "source_match_id": _n(source_match["source_match_id"]),
                "source_player_id": source_id,
                "source_fields": [field for field in ("playerId", "playerName", "team_id", "venue", "substitute", "minutesPlayed", "position") if field in fields],
                "relationship_contract": relationship.name,
                "relationship_status": observation["relationship_status"],
                "transformation": "participation = substitute + minutesPlayed; tactical placement not inferred",
            },
        })

    starters = sum(row["participation"] == "starting" for row in lineup)
    bench = sum(row["participation"] == "bench" for row in lineup)
    sub_in = sum(row["participation"] == "sub_in" for row in lineup)
    status = "AVAILABLE" if lineup and not identity_failures else "KNOWN_EXCEPTION" if lineup else "UNAVAILABLE"

    return {
        "query_type": "fixture_lineup",
        "status": status,
        "season": season,
        "fixture_id": str(fixture_id),
        "grain": "player_fixture",
        "lineup": lineup,
        "coverage": {"player_rows": len(lineup), "starting_rows": starters, "bench_rows": bench, "sub_in_rows": sub_in, "identity_failures": len(identity_failures)},
        "formation": {
            "home": {"status": "UNAVAILABLE", "value": None},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "tactical_placement": {"status": "UNAVAILABLE"},
        "provenance": {
            "source_match_id": _n(source_match["source_match_id"]),
            "source_family": "player_match",
            "relationship_contract": relationship.name,
            "relationship_status": source_match["relationship_status"],
        },
        "limitations": [
            "Starting/substitute/bench classification is derived only from source substitute + minutesPlayed.",
            "Position is retained source evidence; no tactical pitch coordinates or formation inference is performed.",
        ] + (["One or more source-player identities did not resolve uniquely; those relationships remain fail-closed."] if identity_failures else []),
    }


def fixture_evidence(season: str, fixture_id: str) -> dict:
    """Return the universal fixture evidence envelope consumed by frontend/API layers."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    events = fixture_events(season, fixture_id)
    lineup = fixture_lineup(season, fixture_id)
    managers = {
        "status": "UNAVAILABLE",
        "items": [],
        "reason": "No validated historical manager-data route was found in the inspected FRL source boundary.",
    }
    overall = "AVAILABLE" if events["status"] == "AVAILABLE" and lineup["status"] == "AVAILABLE" else "KNOWN_EXCEPTION"

    return {
        "query_type": "fixture_evidence",
        "query_version": "0.1.0",
        "parameters": {"season": season, "fixture_id": str(fixture_id)},
        "fixture": {
            "season": season,
            "fixture_id": str(fixture_id),
            "home_team_id": _n(fixture.get("home_team_id")),
            "away_team_id": _n(fixture.get("away_team_id")),
            "home_score": fixture.get("home_score"),
            "away_score": fixture.get("away_score"),
        },
        "events": events["events"],
        "lineup": lineup["lineup"],
        "formation": {"home": lineup["formation"]["home"], "away": lineup["formation"]["away"]},
        "managers": managers,
        "status": overall,
        "population": {"event_grain": "event", "lineup_grain": "player_fixture"},
        "coverage": {"events": events["coverage"], "lineup": lineup["coverage"], "formation": "UNAVAILABLE", "managers": "UNAVAILABLE"},
        "temporal_context": {
            "season": season,
            "fixture_identity": [season, str(fixture_id)],
            "historical_state_and_information_availability_distinct": True,
            "information_available_as_of": None,
        },
        "provenance": {
            "fixture_identity": {"season": season, "fixture_id": str(fixture_id)},
            "event": events["provenance"],
            "lineup": lineup["provenance"],
            "access_layer": "FRL fixture evidence seam",
        },
        "limitations": events["limitations"] + lineup["limitations"] + [managers["reason"]],
    }


__all__ = ["fixture_events", "fixture_lineup", "fixture_evidence"]
