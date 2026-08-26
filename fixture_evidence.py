"""Universal fixture-level evidence seam.

This module composes existing FRL identity and source-family mechanisms. It does
not create a second fixture/player identity system and does not infer unsupported
formation, tactical placement, manager or event types.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from relationship_contracts import get_relationship_contract
from source_family_adapters import (
    canonical_fixture,
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


def _fixture_side(fixture: dict[str, str], source_team: str) -> str | None:
    target = _n(source_team).casefold()
    if not target:
        return None
    resolved = resolve_source_match(fixture["season"], fixture["fixture_id"])
    for side in ("home", "away"):
        if target == _n(resolved[side].get("team")).casefold():
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
    """Return event-grain evidence attached to a canonical fixture."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    contract = get_relationship_contract("canonical_fixture_to_source_match")
    source_match_id = _n(source_match["source_match_id"])

    source_rows = [
        row for row in _goal_rows()
        if _n(row.get("season")) == season
        and (
            _n(row.get("fixture_id")) == str(fixture_id)
            or _n(row.get("canonical_fixture_id")) == str(fixture_id)
        )
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
        event = {
            "event_id": _n(row.get("source_event_id")) or None,
            "minute": _n(row.get("source_event_time_label")) or None,
            "seconds": _number(row.get("source_event_seconds")),
            "type": _n(row.get("source_event_type")).casefold() or None,
            "side": _fixture_side(
                fixture,
                _n(row.get("source_scorer_team_resolved") or row.get("source_scorer_team")),
            ),
            "primary_player": {
                "source_player_id": source_player_id,
                "name": _n(row.get("source_scorer_name")) or None,
                "identity_status": _player_identity_status(season, source_player_id),
            },
            # Assist data is only returned once independently structured source
            # evidence exists; it is never parsed from display text here.
            "assist": None,
            "raw_text": _n(row.get("source_event_text")) or None,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_family": "fixture_event",
                "source_match_id": source_match_id,
                "source_event_id": _n(row.get("source_event_id")) or None,
                "source_fields": [key for key in row if key.startswith("source_")],
                "relationship_contract": contract.name,
                "relationship_status": source_match["relationship_status"],
                "transformation": "validated goal-event source attachment",
            },
        }
        if event["event_id"] is None or event["type"] is None or event["side"] is None:
            raise ValueError(f"Incomplete goal event identity/context for {season}/{fixture_id}")
        events.append(event)

    event_ids = [event["event_id"] for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError(f"Duplicate source event IDs for {season}/{fixture_id}")

    events.sort(key=lambda item: (item["seconds"] is None, item["seconds"] or 0, item["event_id"]))
    status = "AVAILABLE" if events else "UNAVAILABLE"
    return {
        "query_type": "fixture_events",
        "status": status,
        "season": season,
        "fixture_id": str(fixture_id),
        "grain": "event",
        "events": events,
        "coverage": {
            "event_types": sorted({event["type"] for event in events}),
            "event_count": len(events),
            "goal_events": sum(event["type"] == "goal" for event in events),
            "card_events": 0,
            "substitution_events": 0,
        },
        "provenance": {
            "source_family": "fixture_event",
            "source_match_id": source_match_id,
            "source_path": str(_goal_source()) if _goal_source() else None,
            "relationship_contract": contract.name,
            "relationship_status": source_match["relationship_status"],
        },
        "limitations": [
            "Validated reusable event evidence currently covers goals only.",
            "Cards, substitutions and other event types remain unavailable unless independently validated event-level evidence exists.",
            "Structured assist evidence is not currently promoted by this seam.",
        ],
    }


def _participation(row: dict) -> str:
    substitute = _n(row.get("substitute")).casefold()
    minutes = _number(row.get("minutesPlayed"))
    minutes = 0 if minutes is None else float(minutes)
    is_substitute = substitute in {"true", "1", "yes"}
    if not is_substitute and minutes > 0:
        return "starting"
    if is_substitute and minutes > 0:
        return "sub_in"
    if is_substitute and minutes == 0:
        return "bench"
    return "unknown"


def fixture_lineup(season: str, fixture_id: str) -> dict:
    """Return player-fixture participation evidence using existing Player-Match records."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    rows = player_match_source_rows(season, fixture_id)
    fields = set(player_match_source_fields(season))

    lineup = []
    identity_failures = []
    seen = set()
    for row in rows:
        source_id = _n(row.get("playerId")) or _n(row.get("pl_code"))
        if not source_id:
            identity_failures.append("MISSING_SOURCE_PLAYER_ID")
            continue
        key = (str(source_match["source_match_id"]), source_id, _n(row.get("venue")).casefold())
        if key in seen:
            raise ValueError(f"Duplicate player-fixture observation for {season}/{fixture_id}: {key}")
        seen.add(key)

        identity = source_player_season_identity(season, source_id)
        verified = bool(identity.get("verified"))
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
                "source_fields": [field for field in ("playerId", "pl_code", "playerName", "team_id", "venue", "substitute", "minutesPlayed", "position") if field in fields],
                "relationship_contract": "player_identity_to_player_match_observations",
                "relationship_status": "VERIFIED" if verified else "UNRESOLVED",
                "transformation": "participation classified from substitute + minutesPlayed; no tactical placement inferred",
            },
        })

    starters = sum(item["participation"] == "starting" for item in lineup)
    bench = sum(item["participation"] == "bench" for item in lineup)
    sub_in = sum(item["participation"] == "sub_in" for item in lineup)
    status = "AVAILABLE" if lineup and not identity_failures else "KNOWN_EXCEPTION" if lineup else "UNAVAILABLE"

    return {
        "query_type": "fixture_lineup",
        "status": status,
        "season": season,
        "fixture_id": str(fixture_id),
        "grain": "player_fixture",
        "lineup": lineup,
        "coverage": {
            "player_rows": len(lineup),
            "starting_rows": starters,
            "bench_rows": bench,
            "sub_in_rows": sub_in,
            "identity_failures": len(identity_failures),
        },
        "formation": {
            "home": {"status": "UNAVAILABLE", "value": None},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "tactical_placement": {"status": "UNAVAILABLE"},
        "provenance": {
            "source_match_id": _n(source_match["source_match_id"]),
            "source_family": "player_match",
            "relationship_contract": "player_identity_to_player_match_observations",
            "relationship_status": source_match["relationship_status"],
        },
        "limitations": [
            "Starting/substitute/bench status is derived only from substitute + minutesPlayed.",
            "Position is retained source evidence and is not converted into tactical placement.",
        ] + (["One or more source-player identities did not resolve uniquely; those relationships remain fail-closed."] if identity_failures else []),
    }


__all__ = ["fixture_events", "fixture_lineup"]
