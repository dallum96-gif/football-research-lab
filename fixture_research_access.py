"""Fixture-level composition through the established Universal Research Access."""
from __future__ import annotations

from collections import defaultdict

import research_access
from fixture_evidence import fixture_events
from source_family_adapters import canonical_fixture, player_match_source_rows, resolve_source_match

EXPOSED = ("playerId", "team_id", "venue", "minutesPlayed")
RETAINED = ("playerName", "substitute", "position")


def _ura_player_rows(season: str, fixture_id: str) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = defaultdict(dict)
    for variable in EXPOSED:
        result = research_access.query(research_access.ResearchRequest(
            variable=variable,
            season=season,
            family="player_match",
            fixture_id=str(fixture_id),
        ))
        for item in result.get("results", []):
            player_id = str(item.get("source_player_id") or "").strip()
            if player_id:
                grouped[player_id][variable] = item.get("value")

    # Descriptive fields are retained source evidence, not new GUI variables.
    for row in player_match_source_rows(season, fixture_id):
        player_id = str(row.get("playerId") or row.get("pl_code") or "").strip()
        if player_id:
            grouped[player_id].update({field: row.get(field) for field in RETAINED})
    return dict(grouped)


def fixture_research_result(season: str, fixture_id: str) -> dict:
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    events = fixture_events(season, fixture_id)
    grouped = _ura_player_rows(season, fixture_id)

    lineup = []
    for source_player_id, values in grouped.items():
        substitute = str(values.get("substitute") or "").strip().casefold()
        raw_minutes = values.get("minutesPlayed")
        try:
            minutes = float(raw_minutes) if raw_minutes not in (None, "") else 0.0
        except (TypeError, ValueError):
            minutes = 0.0
        is_sub = substitute in {"true", "1", "yes"}
        participation = (
            "starting" if not is_sub and minutes > 0
            else "sub_in" if is_sub and minutes > 0
            else "bench" if is_sub and minutes == 0
            else "unknown"
        )
        venue = str(values.get("venue") or "").strip().casefold()
        side = "home" if venue == "home" else "away" if venue == "away" else None
        lineup.append({
            "player": {"source_player_id": source_player_id, "name": values.get("playerName")},
            "side": side,
            "participation": participation,
            "position": values.get("position"),
            "minutes": raw_minutes,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": str(source_match["source_match_id"]),
                "source_family": "player_match",
                "access_layer": "FRL Universal Research Access",
                "variables": list(EXPOSED),
                "retained_source_fields": list(RETAINED),
                "transformation": "participation from substitute + minutesPlayed",
            },
        })

    lineup.sort(key=lambda item: (
        item["side"] != "home",
        item["participation"] != "starting",
        item["player"]["name"] or "",
    ))

    # Research Result Contract V1 is preserved as the outer envelope; `payload`
    # is the domain-shaped fixture object consumed by API/UI layers.
    payload = {
        "fixture": {
            "season": season,
            "fixture_id": str(fixture_id),
            "home_team_id": str(fixture.get("home_team_id") or ""),
            "away_team_id": str(fixture.get("away_team_id") or ""),
            "home_score": fixture.get("home_score"),
            "away_score": fixture.get("away_score"),
        },
        "events": events["events"],
        "lineup": lineup,
        "formation": {
            "home": {"status": "UNAVAILABLE", "value": None},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "managers": {
            "status": "UNAVAILABLE",
            "items": [],
            "reason": "No validated historical manager-data route is exposed by the inspected FRL source universe.",
        },
        "status": "AVAILABLE" if events["status"] == "AVAILABLE" and lineup else "KNOWN_EXCEPTION",
    }

    return {
        "query_type": "fixture_evidence",
        "query_version": "0.2.0",
        "parameters": {"season": season, "fixture_id": str(fixture_id)},
        "columns": ("fixture", "events", "lineup", "formation", "managers", "status"),
        "rows": [payload],
        "payload": payload,
        "population": {
            "event_grain": "event",
            "lineup_grain": "player_fixture",
            "lineup_rows": len(lineup),
        },
        "provenance": {
            "access_layer": "FRL Universal Research Access",
            "fixture_relationship": "canonical_fixture_to_source_match",
            "source_match_id": str(source_match["source_match_id"]),
            "event_source": events["provenance"],
        },
        "temporal_context": {
            "season": season,
            "fixture_identity": [season, str(fixture_id)],
            "historical_state_and_information_availability_distinct": True,
            "information_available_as_of": None,
        },
        "limitations": events["limitations"] + [
            "Formation and tactical placement are unavailable unless independently validated historical evidence is added.",
            "Manager data is unavailable unless independently validated historical evidence is added.",
        ],
    }


__all__ = ["fixture_research_result"]
