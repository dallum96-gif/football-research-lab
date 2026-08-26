"""Universal research-access composition for fixture evidence.

This module is the consumer-facing composition layer: it resolves the canonical
fixture, obtains reusable player-match variables through the established FRL
Universal Research Access layer, and combines those with the event-grain
fixture evidence adapter without exposing storage mechanics to consumers.
"""
from __future__ import annotations

from collections import defaultdict

import research_access
from fixture_evidence import fixture_events
from source_family_adapters import canonical_fixture, resolve_source_match

LINEUP_VARIABLES = ("playerId", "playerName", "team_id", "venue", "substitute", "minutesPlayed", "position")


def _ura_rows(season: str, fixture_id: str) -> dict[str, dict[str, object]]:
    """Fetch the reusable player-fixture fields through Universal Research Access."""
    by_player: dict[str, dict[str, object]] = defaultdict(dict)
    for variable in LINEUP_VARIABLES:
        result = research_access.query(
            research_access.ResearchRequest(
                variable=variable,
                season=season,
                family="player_match",
                fixture_id=str(fixture_id),
            )
        )
        for row in result.get("results", []):
            player_id = str(row.get("source_player_id") or "").strip()
            if not player_id:
                continue
            by_player[player_id][variable] = row.get("value")
    return dict(by_player)


def fixture_research_result(season: str, fixture_id: str) -> dict:
    """Return the structured fixture evidence result used by API/frontend layers."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    events = fixture_events(season, fixture_id)
    ura_rows = _ura_rows(season, fixture_id)

    lineup = []
    for source_player_id, values in ura_rows.items():
        substitute = str(values.get("substitute") or "").strip().casefold()
        minutes_raw = values.get("minutesPlayed")
        try:
            minutes = float(minutes_raw) if minutes_raw not in (None, "") else 0.0
        except (TypeError, ValueError):
            minutes = 0.0
        is_sub = substitute in {"true", "1", "yes"}
        participation = "starting" if not is_sub and minutes > 0 else "sub_in" if is_sub and minutes > 0 else "bench" if is_sub and minutes == 0 else "unknown"
        venue = str(values.get("venue") or "").strip().casefold()
        side = "home" if venue == "home" else "away" if venue == "away" else None
        lineup.append({
            "player": {
                "source_player_id": source_player_id,
                "name": values.get("playerName"),
            },
            "side": side,
            "participation": participation,
            "position": values.get("position"),
            "minutes": minutes_raw,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": str(source_match["source_match_id"]),
                "source_family": "player_match",
                "access_layer": "FRL Universal Research Access",
                "variables": list(LINEUP_VARIABLES),
                "transformation": "participation classification from substitute + minutesPlayed",
            },
        })

    lineup.sort(key=lambda row: (row["side"] != "home", row["participation"] != "starting", row["player"]["name"] or ""))
    status = "AVAILABLE" if lineup and events["status"] == "AVAILABLE" else "KNOWN_EXCEPTION"

    return {
        "query_type": "fixture_evidence",
        "query_version": "0.2.0",
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
        "status": status,
        "population": {"event_grain": "event", "lineup_grain": "player_fixture"},
        "coverage": {
            "event": events["coverage"],
            "lineup": {
                "player_rows": len(lineup),
                "starting_rows": sum(row["participation"] == "starting" for row in lineup),
                "bench_rows": sum(row["participation"] == "bench" for row in lineup),
                "sub_in_rows": sum(row["participation"] == "sub_in" for row in lineup),
            },
            "formation": "UNAVAILABLE",
            "managers": "UNAVAILABLE",
        },
        "temporal_context": {
            "season": season,
            "fixture_identity": [season, str(fixture_id)],
            "historical_state_and_information_availability_distinct": True,
            "information_available_as_of": None,
        },
        "provenance": {
            "access_layer": "FRL Universal Research Access",
            "fixture_relationship": "canonical_fixture_to_source_match",
            "source_match_id": str(source_match["source_match_id"]),
        },
        "limitations": events["limitations"] + [
            "Player-fixture lineup is assembled from existing Universal Research Access variables.",
            "Formation and tactical placement are unavailable unless independently validated source evidence is added.",
            "Manager data is unavailable unless independently validated historical manager evidence is added.",
        ],
    }


__all__ = ["fixture_research_result"]
