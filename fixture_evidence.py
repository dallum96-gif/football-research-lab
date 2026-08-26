"""Universal fixture evidence access for the FRL.

This module is an additive consumer seam over the existing canonical fixture,
source-match, player-match and identity machinery. It keeps event observations
at event grain and lineup observations at player-fixture grain.

The first event source currently validated for reusable historical access is the
FRL's staged PulseLive goal-event evidence. Cards/substitutions/other event
families are not fabricated when no trusted event-level source is available.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from relationship_contracts import get_relationship_contract
from source_family_adapters import (
    canonical_fixture,
    resolve_source_match,
    player_match_source_rows,
    player_match_source_fields,
    player_match_observation_status,
    source_player_season_identity,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_GOAL_EVENT_OUTPUT = ROOT / "data" / "fixture_goal_events.csv"
DEFAULT_GOAL_EVENT_SOURCE = (
    ROOT.parent
    / "Premier-League-Stats"
    / "fpl_scraper"
    / "fpl_stats"
    / "data"
    / "raw"
    / "fixture_goal_events_pulselive.staged.csv"
)

GOAL_EVENT_REQUIRED = {
    "season",
    "fixture_id",
    "source_match_id",
    "source_event_id",
    "source_event_type",
    "source_event_seconds",
    "source_event_time_label",
    "source_scorer_name",
    "source_scorer_team_resolved",
}


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    if not path.is_file():
        return tuple()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return tuple(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def _first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.is_file():
            return path
    return None


@lru_cache(maxsize=1)
def _goal_event_path() -> Path | None:
    return _first_existing((DEFAULT_GOAL_EVENT_OUTPUT, DEFAULT_GOAL_EVENT_SOURCE))


@lru_cache(maxsize=1)
def _goal_events() -> tuple[dict[str, str], ...]:
    path = _goal_event_path()
    if path is None:
        return tuple()
    rows = _read_csv(path)
    if not rows:
        return tuple()
    missing = GOAL_EVENT_REQUIRED - set(rows[0])
    if missing:
        raise ValueError(f"Goal event source missing required fields: {sorted(missing)}")
    return rows


def _event_identity_status(season: str, fixture_id: str, source_player_id: str | None) -> str:
    if not source_player_id:
        return "UNAVAILABLE"
    try:
        result = source_player_season_identity(season, source_player_id)
    except (FileNotFoundError, ValueError):
        return "UNRESOLVED"
    return "VERIFIED" if result.get("verified") else str(result.get("status") or "UNRESOLVED")


def fixture_events(season: str, fixture_id: str) -> dict:
    """Return event-grain evidence attached to one canonical fixture."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    contract = get_relationship_contract("canonical_fixture_to_source_match")
    source_match_id = str(source_match["source_match_id"])

    rows = [
        dict(row)
        for row in _goal_events()
        if str(row.get("season") or "") == str(season)
        and str(row.get("fixture_id") or "") == str(fixture_id)
    ]

    # Never attach an event to a different verified source match.
    attached = [
        row for row in rows
        if str(row.get("source_match_id") or "") == source_match_id
    ]
    mismatched = [
        row for row in rows
        if str(row.get("source_match_id") or "") != source_match_id
    ]

    if mismatched:
        raise ValueError(
            f"Event/source-match contradiction for {season}/{fixture_id}: "
            f"expected {source_match_id}, found {sorted({str(r.get('source_match_id')) for r in mismatched})}"
        )

    events = []
    for row in attached:
        source_player_id = str(row.get("source_scorer_id") or "").strip() or None
        event = {
            "event_id": str(row.get("source_event_id") or ""),
            "minute": str(row.get("source_event_time_label") or ""),
            "seconds": _number(row.get("source_event_seconds")),
            "type": str(row.get("source_event_type") or "").strip().lower(),
            "side": _fixture_side(
                fixture,
                str(row.get("source_scorer_team_resolved") or "").strip(),
            ),
            "primary_player": {
                "source_player_id": source_player_id,
                "name": str(row.get("source_scorer_name") or "").strip() or None,
                "identity_status": _event_identity_status(season, fixture_id, source_player_id),
            },
            "assist": None,
            "raw_text": str(row.get("source_event_text") or "").strip() or None,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_family": "fixture_event",
                "source_match_id": source_match_id,
                "source_event_id": str(row.get("source_event_id") or ""),
                "source_fields": [
                    "source_event_type",
                    "source_event_seconds",
                    "source_event_time_label",
                    "source_event_text",
                    "source_scorer_name",
                    "source_scorer_team_resolved",
                    "source_scorer_id",
                ],
                "relationship_contract": contract.name,
                "relationship_status": source_match["relationship_status"],
                "transformation": "validated staged goal-event normalization",
            },
        }
        events.append(event)

    events.sort(key=lambda event: (event["seconds"] is None, event["seconds"] or 0, event["event_id"]))

    status = "AVAILABLE" if events else "UNAVAILABLE"
    limitations = []
    if not _goal_events():
        limitations.append("No validated historical event-level source is materialized in the runtime environment.")
    else:
        limitations.append("Current reusable event evidence is goal-level; card/substitution/other event families are not promoted without independently validated event-level provenance.")

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
            "card_events": sum(event["type"] in {"yellow", "red", "card"} for event in events),
            "substitution_events": sum(event["type"] in {"substitution", "substitution_in", "substitution_out"} for event in events),
        },
        "provenance": {
            "source_match_id": source_match_id,
            "relationship_contract": contract.name,
            "relationship_status": source_match["relationship_status"],
            "source_path": str(_goal_event_path()) if _goal_event_path() else None,
        },
        "limitations": limitations,
    }


def fixture_lineup(season: str, fixture_id: str) -> dict:
    """Return player-fixture participation evidence without inferring tactics."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    contract = get_relationship_contract("player_identity_to_player_match_observations")
    rows = player_match_source_rows(season, fixture_id)
    fields = set(player_match_source_fields(season))

    output = []
    identity_failures = []
    for row in rows:
        source_id = str(row.get("playerId") or "").strip() or None
        if not source_id:
            identity_failures.append({"reason": "MISSING_SOURCE_PLAYER_ID", "row": dict(row)})
            continue

        source_identity = source_player_season_identity(season, source_id)
        verified_identity = bool(source_identity.get("verified"))
        observation = player_match_observation_status(
            season,
            fixture_id,
            source_id,
            player_identity_verified=verified_identity,
        )
        participation = _classify(row)
        side = "home" if str(row.get("venue") or "").strip().lower() == "home" else "away" if str(row.get("venue") or "").strip().lower() == "away" else None

        if not verified_identity:
            identity_failures.append({
                "source_player_id": source_id,
                "status": source_identity.get("status"),
            })

        output.append({
            "player": {
                "source_player_id": source_id,
                "name": str(row.get("playerName") or "").strip() or None,
                "identity_status": "VERIFIED" if verified_identity else str(source_identity.get("status") or "UNRESOLVED"),
            },
            "side": side,
            "participation": participation,
            "position": str(row.get("position") or "").strip() or None,
            "minutes": _number(row.get("minutesPlayed")),
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_family": "player_match",
                "source_match_id": str(source_match["source_match_id"]),
                "source_player_id": source_id,
                "source_fields": [field for field in ("playerId", "playerName", "team_id", "venue", "substitute", "minutesPlayed", "position") if field in fields],
                "relationship_contract": contract.name,
                "relationship_status": observation["relationship_status"],
                "transformation": "participation classified from substitute + minutesPlayed; no tactical placement inferred",
            },
        })

    output.sort(key=lambda item: (item["side"] != "home", item["participation"] not in {"starting", "sub_in", "bench"}, item["player"]["name"] or ""))

    starters = sum(item["participation"] == "starting" for item in output)
    bench = sum(item["participation"] == "bench" for item in output)
    sub_in = sum(item["participation"] == "sub_in" for item in output)

    return {
        "query_type": "fixture_lineup",
        "status": "AVAILABLE" if output and not identity_failures else "KNOWN_EXCEPTION" if output else "UNAVAILABLE",
        "season": season,
        "fixture_id": str(fixture_id),
        "grain": "player_fixture",
        "lineup": output,
        "coverage": {
            "player_rows": len(output),
            "starting_rows": starters,
            "bench_rows": bench,
            "sub_in_rows": sub_in,
            "identity_failures": len(identity_failures),
        },
        "formation": {
            "status": "UNAVAILABLE",
            "value": None,
            "reason": "No independently validated historical formation field or safe derivation is currently established in the inspected FRL source boundary.",
        },
        "tactical_placement": {
            "status": "UNAVAILABLE",
            "reason": "No validated historical pitch-coordinate/lineup-placement evidence exposed by the current source boundary.",
        },
        "provenance": {
            "source_match_id": str(source_match["source_match_id"]),
            "relationship_contract": contract.name,
            "relationship_status": source_match["relationship_status"],
            "source_family": "player_match",
        },
        "limitations": [
            "Starting/substitute/bench status is source-derived from substitute + minutesPlayed.",
            "Position is retained source evidence and is not converted into tactical placement.",
        ] + (["One or more source player IDs did not resolve uniquely and were retained fail-closed without promotion."] if identity_failures else []),
    }


def fixture_evidence(season: str, fixture_id: str) -> dict:
    """Compose the universal fixture evidence envelope."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    events = fixture_events(season, fixture_id)
    lineup = fixture_lineup(season, fixture_id)

    managers = {
        "status": "UNAVAILABLE",
        "items": [],
        "reason": "No validated historical manager-data route is exposed by the inspected FRL source boundary.",
    }

    return {
        "query_type": "fixture_evidence",
        "query_version": "0.1.0",
        "parameters": {"season": season, "fixture_id": str(fixture_id)},
        "fixture": {
            "season": season,
            "fixture_id": str(fixture_id),
            "home_team_id": str(fixture.get("home_team_id") or ""),
            "away_team_id": str(fixture.get("away_team_id") or ""),
            "home_score": fixture.get("home_score"),
            "away_score": fixture.get("away_score"),
        },
        "events": events["events"],
        "lineup": lineup["lineup"],
        "formation": {
            "home": lineup["formation"],
            "away": lineup["formation"],
        },
        "managers": managers,
        "status": "AVAILABLE" if events["status"] == "AVAILABLE" and lineup["status"] == "AVAILABLE" else "KNOWN_EXCEPTION" if lineup["status"] != "UNAVAILABLE" else "PARTIAL",
        "provenance": {
            "fixture_identity": {"season": season, "fixture_id": str(fixture_id)},
            "event_source": events["provenance"],
            "lineup_source": lineup["provenance"],
            "access_layer": "FRL fixture evidence seam over Universal Research Access-compatible adapters",
        },
        "coverage": {
            "events": events["coverage"],
            "lineup": lineup["coverage"],
            "formation": {"home": lineup["formation"]["status"], "away": lineup["formation"]["status"]},
            "managers": managers["status"],
        },
        "limitations": events["limitations"] + lineup["limitations"] + [managers["reason"]],
        "temporal_context": {
            "season": season,
            "fixture_identity_is_historical": True,
            "information_available_as_of": None,
            "historical_state_and_information_availability_distinct": True,
        },
        "population": {
            "event_grain": "event",
            "lineup_grain": "player_fixture",
        },
    }


def _fixture_side(fixture: dict[str, str], source_team: str) -> str | None:
    source = str(source_team or "").strip().casefold()
    if not source:
        return None
    # Prefer verified source-match rows over display names.
    try:
        resolved = resolve_source_match(fixture["season"], fixture["fixture_id"])
    except ValueError:
        return None
    if source.casefold() == str(resolved["home"].get("team") or "").strip().casefold():
        return "home"
    if source.casefold() == str(resolved["away"].get("team") or "").strip().casefold():
        return "away"
    return None


def _classify(row: dict) -> str:
    substitute = str(row.get("substitute") or "").strip().casefold()
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


def _number(value: object):
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


__all__ = ["fixture_events", "fixture_lineup", "fixture_evidence"]
